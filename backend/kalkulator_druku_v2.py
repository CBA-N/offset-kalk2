"""
SYSTEM KALKULACJI DRUKU OFFSETOWEGO V2.0
Zautomatyzowany kalkulator z optymalizacją formatu
"""

import json
import math
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from slowniki_danych import *

@dataclass
class FormatProposal:
    """Propozycja formatu arkusza"""
    format_name: str
    szerokosc: int
    wysokosc: int
    powierzchnia: float
    uzytki_na_ark: int
    orientacja: str  # 'pionowa' lub 'pozioma'
    odpady_procent: float
    wykorzystanie_procent: float
    ilosc_arkuszy: int
    koszt_papieru: float
    czas_produkcji_h: float
    score: float  # wynik wg priorytetu
    
@dataclass
class KalkulacjaZlecenia:
    """Pełna kalkulacja zlecenia"""
    # Dane wejściowe
    nazwa_produktu: str
    format_wydruku_mm: Tuple[int, int]
    naklad: int
    rodzaj_papieru: str
    gramatura: int
    kolorysyka_cmyk: str  # '4+0', '4+4', '4+1'
    kolory_specjalne: List[str]
    uszlachetnienia: List[str]
    obrobka: List[str]
    pakowanie: str
    transport: str
    marza_procent: float
    priorytet_optymalizacji: str
    
    # Kontrahent (opcjonalny)
    kontrahent_id: int = None  # ID kontrahenta z bazy
    kontrahent: dict = None    # Pełne dane kontrahenta (kopia dla historii)
    
    # Wyniki kalkulacji
    wybrany_format: FormatProposal = None
    alternatywne_formaty: List[FormatProposal] = None
    
    koszt_papieru: float = 0
    koszt_druku: float = 0
    koszt_kolorow_spec: float = 0
    koszt_uszlachetnien: float = 0
    koszt_obrobki: float = 0
    koszt_ciecia_papieru: float = 0  # Nowe pole: koszt cięcia z B1
    koszt_pakowania: float = 0
    koszt_transportu: float = 0
    koszt_czasu_druku: float = 0

    suma_kosztow_netto: float = 0
    cena_z_marza_netto: float = 0
    cena_brutto_vat23: float = 0

    czas_realizacji_h: float = 0
    czas_druku_h: float = 0
    waga_kg: float = 0


class KalkulatorDruku:
    """Główna klasa kalkulatora"""
    
    def __init__(self):
        self.papiery = PAPIERY
        self.formaty = FORMATY_ARKUSZY
        self.uszlachetnienia = USZLACHETNIENIA
        self.obrobka = OBROBKA_WYKONCZ
        self.kolory_spec = KOLORY_SPECJALNE
        self.pakowanie = PAKOWANIE
        self.transport = TRANSPORT
        self.priorytety = PRIORYTETY_OPTYMALIZACJI
        self.stawki = STAWKI_DRUKARNI
        self.ciecie_papieru = {}  # Konfiguracja cięcia (wstrzyknięta przez adapter)
        
    def oblicz_uzytki_na_arkuszu(self, 
                                  format_wydruku: Tuple[int, int],
                                  format_arkusza: Tuple[int, int]) -> Dict:
        """
        Oblicza ile użytków zmieści się na arkuszu w obu orientacjach
        """
        szerokosc_w, wysokosc_w = format_wydruku
        szerokosc_a, wysokosc_a = format_arkusza
        
        # Margines techniczny 5mm z każdej strony
        margines = 10
        szerokosc_a_uzyteczna = szerokosc_a - margines
        wysokosc_a_uzyteczna = wysokosc_a - margines
        
        # Orientacja pionowa wydruku
        uzytki_pion_x = szerokosc_a_uzyteczna // szerokosc_w
        uzytki_pion_y = wysokosc_a_uzyteczna // wysokosc_w
        uzytki_pion = uzytki_pion_x * uzytki_pion_y
        
        # Orientacja pozioma wydruku (obrócony o 90°)
        uzytki_poziom_x = szerokosc_a_uzyteczna // wysokosc_w
        uzytki_poziom_y = wysokosc_a_uzyteczna // szerokosc_w
        uzytki_poziom = uzytki_poziom_x * uzytki_poziom_y
        
        # Wybierz lepszą orientację
        if uzytki_pion >= uzytki_poziom:
            uzytki = uzytki_pion
            orientacja = 'pionowa'
            powierzchnia_uzytku = (szerokosc_w * wysokosc_w) / 1_000_000  # m²
        else:
            uzytki = uzytki_poziom
            orientacja = 'pozioma'
            powierzchnia_uzytku = (wysokosc_w * szerokosc_w) / 1_000_000  # m²
        
        # Oblicz wykorzystanie i odpady
        powierzchnia_arkusza = (szerokosc_a * wysokosc_a) / 1_000_000  # m²
        powierzchnia_wykorzystana = uzytki * powierzchnia_uzytku
        wykorzystanie = (powierzchnia_wykorzystana / powierzchnia_arkusza) * 100
        odpady = 100 - wykorzystanie
        
        return {
            'uzytki': uzytki,
            'orientacja': orientacja,
            'wykorzystanie_procent': wykorzystanie,
            'odpady_procent': odpady,
            'powierzchnia_arkusza_m2': powierzchnia_arkusza
        }
    
    def optymalizuj_format(self,
                          format_wydruku: Tuple[int, int],
                          naklad: int,
                          rodzaj_papieru: str,
                          gramatura: int,
                          priorytet: str = 'Zrównoważony') -> List[FormatProposal]:
        """
        Analizuje wszystkie formaty i zwraca ranking propozycji
        """
        propozycje = []
        
        # Pobierz cenę papieru (klucz jako string dla kompatybilności z JSON)
        cena_kg = self.papiery[rodzaj_papieru]['ceny'][str(gramatura)]
        
        # Wagi z priorytetu
        wagi = self.priorytety[priorytet]

        szybkosc_ark_h = self.stawki.get('szybkosc_druku_arkuszy_h')
        if not szybkosc_ark_h or szybkosc_ark_h <= 0:
            raise ValueError("Szybkość druku musi być dodatnia. Ustaw ją w słowniku stawek drukarni.")
        
        for nazwa_formatu, dane_formatu in self.formaty.items():
            format_ark = (dane_formatu['szerokosc_mm'], dane_formatu['wysokosc_mm'])
            
            # Oblicz układ użytków
            uklad = self.oblicz_uzytki_na_arkuszu(format_wydruku, format_ark)
            
            if uklad['uzytki'] == 0:
                continue  # Format za mały
            
            # Oblicz ilość arkuszy (z zaokrągleniem w górę)
            ilosc_arkuszy = math.ceil(naklad / uklad['uzytki'])
            # Dodaj 10% odpady
            ilosc_arkuszy_z_odpadami = math.ceil(ilosc_arkuszy * 1.1)
            
            # Koszt papieru
            powierzchnia_ark = uklad['powierzchnia_arkusza_m2']
            waga_arkusza_kg = powierzchnia_ark * (gramatura / 1000)
            koszt_papieru = ilosc_arkuszy_z_odpadami * waga_arkusza_kg * cena_kg
            
            # Czas produkcji
            czas_produkcji = ilosc_arkuszy_z_odpadami / szybkosc_ark_h
            
            # Normalizacja do 0-1 dla scoringu
            # Im mniej odpady/koszt/czas tym lepiej, więc odwracamy
            norm_odpady = 1 - (uklad['odpady_procent'] / 100)
            norm_koszt = 1 / (koszt_papieru / 1000 + 1)  # Normalizacja
            norm_czas = 1 / (czas_produkcji + 1)
            
            # Oblicz wynik wg wag
            score = (norm_odpady * wagi['waga_odpady'] + 
                    norm_koszt * wagi['waga_koszt'] +
                    norm_czas * wagi['waga_czas'])
            
            propozycja = FormatProposal(
                format_name=nazwa_formatu,
                szerokosc=dane_formatu['szerokosc_mm'],
                wysokosc=dane_formatu['wysokosc_mm'],
                powierzchnia=powierzchnia_ark,
                uzytki_na_ark=uklad['uzytki'],
                orientacja=uklad['orientacja'],
                odpady_procent=uklad['odpady_procent'],
                wykorzystanie_procent=uklad['wykorzystanie_procent'],
                ilosc_arkuszy=ilosc_arkuszy_z_odpadami,
                koszt_papieru=koszt_papieru,
                czas_produkcji_h=czas_produkcji,
                score=score
            )
            
            propozycje.append(propozycja)
        
        # Sortuj po wyniku (score)
        propozycje.sort(key=lambda p: p.score, reverse=True)
        
        return propozycje
    
    def kalkuluj_druk(self,
                     ilosc_arkuszy: int,
                     kolorystyka: str,
                     ilosc_form: int = 4) -> Dict[str, float]:
        """
        Kalkulacja kosztów druku
        """
        # Przygotowanie (czas × stawka)
        czas_przygotowania_h = 1.0  # Standardowo 1h
        stawka_przygotowania = self.stawki.get('roboczogodzina_przygotowania')
        if not stawka_przygotowania or stawka_przygotowania <= 0:
            raise ValueError("Roboczogodzina przygotowania musi być dodatnia. Ustaw ją w słowniku stawek drukarni.")
        koszt_przygotowania = czas_przygotowania_h * stawka_przygotowania

        szybkosc = self.stawki.get('szybkosc_druku_arkuszy_h')
        if not szybkosc or szybkosc <= 0:
            raise ValueError("Szybkość druku musi być dodatnia. Ustaw ją w słowniku stawek drukarni.")

        # Formy drukowe
        koszt_form = ilosc_form * self.stawki['koszt_formy_drukowej']

        # Przeloty
        if kolorystyka == '4+0':
            przeloty = ilosc_arkuszy  # Jednostronny
        elif kolorystyka == '4+4':
            przeloty = ilosc_arkuszy * 2  # Dwustronny
        elif kolorystyka == '4+1':
            przeloty = ilosc_arkuszy * 1.25  # 4 kolory + 1 kolor
        else:
            przeloty = ilosc_arkuszy
        
        koszt_przelotow = (przeloty / 1000) * self.stawki['stawka_nakladu_1000_arkuszy']

        stawka_druku_h = self.stawki.get('roboczogodzina_druku', stawka_przygotowania)
        if not stawka_druku_h or stawka_druku_h <= 0:
            raise ValueError("Roboczogodzina druku musi być dodatnia. Ustaw ją w słowniku stawek drukarni.")
        czas_druku_h = ilosc_arkuszy / szybkosc
        koszt_czasu_druku = czas_druku_h * stawka_druku_h

        koszt_calkowity = koszt_przygotowania + koszt_form + koszt_przelotow + koszt_czasu_druku

        return {
            'przygotowanie': koszt_przygotowania,
            'formy': koszt_form,
            'przeloty': koszt_przelotow,
            'czas_druku_h': czas_druku_h,
            'koszt_czasu_druku': koszt_czasu_druku,
            'razem': koszt_calkowity,
            'czas_h': czas_przygotowania_h + czas_druku_h,
            'czas_przygotowania_h': czas_przygotowania_h,
            'szybkosc_druku_arkuszy_h': szybkosc
        }
    
    def kalkuluj_kolory_specjalne(self, lista_kolorow: List[str]) -> Dict[str, float]:
        """Kalkulacja kolorów Pantone/Spot"""
        koszt = 0
        czas = 0
        
        for kolor in lista_kolorow:
            if kolor in self.kolory_spec:
                koszt += self.kolory_spec[kolor]['koszt_za_kolor']
                koszt += self.kolory_spec[kolor]['koszt_preparatu']
                czas += self.kolory_spec[kolor]['czas_przygotowania_min'] / 60
        
        return {'koszt': koszt, 'czas_h': czas}
    
    def kalkuluj_uszlachetnienia(self,
                                 lista_uszlachetnien: List[str],
                                 ilosc_arkuszy: int,
                                 powierzchnia_arkusza: float,
                                 naklad: int = 0,
                                 waga_kg: float = 0) -> Dict[str, float]:
        """Kalkulacja uszlachetnień z elastycznymi jednostkami"""
        koszt = 0
        czas = 0
        
        for uszlachetnienie in lista_uszlachetnien:
            if uszlachetnienie in self.uszlachetnienia:
                dane = self.uszlachetnienia[uszlachetnienie]

                cena_pln = dane.get('cena_pln')
                typ_jednostki = dane.get('typ_jednostki')
                jednostka_str = dane.get('jednostka', '')

                if cena_pln is not None and typ_jednostki:
                    jednostka_wartosc = 1.0
                    match = re.search(r'([\d.,]+)', jednostka_str)
                    if match:
                        jednostka_wartosc = float(match.group(1).replace(',', '.')) or 1.0

                    if typ_jednostki == 'sztukowa':
                        ilosc_bazowa = 0
                        jednostka_lower = jednostka_str.lower()
                        if 'ark' in jednostka_lower:
                            ilosc_bazowa = ilosc_arkuszy or 0
                        else:
                            ilosc_bazowa = naklad or 0
                        if ilosc_bazowa == 0:
                            ilosc_bazowa = ilosc_arkuszy or naklad
                        if ilosc_bazowa is None:
                            ilosc_bazowa = 0
                        koszt += cena_pln * (ilosc_bazowa / jednostka_wartosc)

                    elif typ_jednostki == 'metrowa':
                        powierzchnia_calkowita_m2 = powierzchnia_arkusza * ilosc_arkuszy
                        koszt += cena_pln * (powierzchnia_calkowita_m2 / jednostka_wartosc)

                    elif typ_jednostki == 'wagowa':
                        koszt += cena_pln * (waga_kg / jednostka_wartosc)

                    else:
                        koszt += cena_pln
                else:
                    # Zgodność wsteczna: użyj starych pól jeśli brak nowych
                    if 'cena_za_arkusz_B2' in dane:
                        koszt += dane['cena_za_arkusz_B2'] * ilosc_arkuszy
                    elif 'cena_za_m2' in dane:
                        koszt += dane['cena_za_m2'] * powierzchnia_arkusza * ilosc_arkuszy

                # Koszt matrycy jeśli istnieje
                if 'koszt_matrycy' in dane:
                    koszt += dane['koszt_matrycy']

                # Czas przygotowania (wydobycie z opisu lub wartość domyślna)
                if 'czas_przygotowania_min' in dane:
                    czas += dane['czas_przygotowania_min'] / 60
                else:
                    opis = dane.get('opis', '')
                    match = re.search(r'Czas:\s*(\d+)\s*min', opis)
                    if match:
                        czas += int(match.group(1)) / 60

        return {'koszt': koszt, 'czas_h': czas}
    
    def kalkuluj_obrobke(self,
                        lista_obrobki: List[str],
                        naklad: int,
                        powierzchnia_arkusza: float = 0,
                        ilosc_arkuszy: int = 0,
                        waga_kg: float = 0) -> Dict[str, float]:
        """Kalkulacja obróbki wykończeniowej z elastycznymi jednostkami"""
        koszt = 0
        czas = 0
        
        for obrobka in lista_obrobki:
            if obrobka in self.obrobka:
                dane = self.obrobka[obrobka]
                cena_pln = dane.get('cena_pln', 0)
                typ_jednostki = dane.get('typ_jednostki', 'sztukowa')  # domyślnie sztukowa
                jednostka_str = dane.get('jednostka', '') or ''

                jednostka_wartosc = 1.0
                match = re.search(r'([\d.,]+)', jednostka_str)
                if match:
                    try:
                        jednostka_wartosc = float(match.group(1).replace(',', '.'))
                    except ValueError:
                        jednostka_wartosc = 1.0
                if jednostka_wartosc == 0:
                    jednostka_wartosc = 1.0

                jednostka_lower = jednostka_str.lower()

                # Opcjonalne wsparcie słownika jednostek (jeśli został wstrzyknięty)
                jednostka_meta = None
                slownik_jednostek = (
                    getattr(self, 'slownik_jednostek', None)
                    or getattr(self, 'jednostki_slownik', None)
                    or getattr(self, 'jednostki_meta', None)
                    or getattr(self, 'jednostki', None)
                )
                if isinstance(slownik_jednostek, dict):
                    lookup_keys = [jednostka_str.strip(), jednostka_lower.strip()]
                    for key in lookup_keys:
                        if key in slownik_jednostek:
                            jednostka_meta = slownik_jednostek[key]
                            break

                bazowa_kategoria = None
                if isinstance(jednostka_meta, dict):
                    for meta_key in (
                        'bazowa_kategoria',
                        'base_category',
                        'typ_bazowy',
                        'rodzaj_bazowy',
                        'bazowa_ilosc',
                        'base_quantity',
                    ):
                        if meta_key in jednostka_meta:
                            bazowa_kategoria = jednostka_meta[meta_key]
                            break
                    if isinstance(bazowa_kategoria, str):
                        bazowa_kategoria = bazowa_kategoria.lower()

                ilosc_bazowa = None

                if typ_jednostki == 'metrowa':
                    ilosc_bazowa = powierzchnia_arkusza * ilosc_arkuszy
                elif typ_jednostki == 'wagowa':
                    ilosc_bazowa = waga_kg
                else:
                    if bazowa_kategoria:
                        if bazowa_kategoria in {'arkusz', 'arkusze', 'arkuszowa', 'ark'}:
                            ilosc_bazowa = ilosc_arkuszy
                        elif bazowa_kategoria in {'sztuka', 'sztuki', 'naklad', 'egzemplarze', 'sztukowa'}:
                            ilosc_bazowa = naklad
                        elif bazowa_kategoria in {'metry', 'metry_biezace', 'mb', 'm2', 'powierzchnia', 'metrowa'}:
                            ilosc_bazowa = powierzchnia_arkusza * ilosc_arkuszy
                        elif bazowa_kategoria in {'waga', 'kg', 'wagowa'}:
                            ilosc_bazowa = waga_kg

                    if ilosc_bazowa is None:
                        if 'ark' in jednostka_lower:
                            ilosc_bazowa = ilosc_arkuszy
                        elif 'mb' in jednostka_lower:
                            ilosc_bazowa = powierzchnia_arkusza * ilosc_arkuszy
                        elif 'kg' in jednostka_lower:
                            ilosc_bazowa = waga_kg
                        else:
                            ilosc_bazowa = naklad

                if not ilosc_bazowa:
                    ilosc_bazowa = naklad

                koszt += cena_pln * (ilosc_bazowa / jednostka_wartosc)

                # Koszt przygotowania jeśli istnieje
                if 'koszt_przygotowania' in dane:
                    koszt += dane['koszt_przygotowania']
                
                # Czas (parsowanie z opisu jeśli istnieje)
                if 'czas_min' in dane:
                    czas += dane['czas_min'] / 60
                else:
                    opis = dane.get('opis', '')
                    match = re.search(r'Czas:\s*(\d+)\s*min', opis)
                    if match:
                        czas += int(match.group(1)) / 60
        
        return {'koszt': koszt, 'czas_h': czas}
    
    def kalkuluj_pakowanie_transport(self,
                                    pakowanie: str,
                                    transport: str) -> Dict[str, float]:
        """Kalkulacja pakowania i transportu"""
        koszt_pak = self.pakowanie.get(pakowanie, {}).get('cena', 0)
        koszt_trans = self.transport.get(transport, {}).get('cena', 0)
        czas_trans_dni = self.transport.get(transport, {}).get('czas_dni', 0)
        
        return {
            'pakowanie': koszt_pak,
            'transport': koszt_trans,
            'czas_dni': czas_trans_dni,
            'razem': koszt_pak + koszt_trans
        }
    
    def kalkuluj_ciecie_papieru(self,
                                format_arkusza_mm: tuple,
                                ilosc_arkuszy: int,
                                wymaga_ciecia: bool = True) -> Dict[str, float]:
        """
        Kalkulacja kosztu cięcia papieru z arkuszy B1
        
        Args:
            format_arkusza_mm: (szerokość, wysokość) formatu drukarskiego w mm
            ilosc_arkuszy: liczba arkuszy drukarskich do wycięcia
            wymaga_ciecia: czy papier wymaga cięcia z B1 (False = już docięty)
        
        Returns:
            Dict z kosztem cięcia, ilością arkuszy B1, czasem
        """
        if not wymaga_ciecia:
            return {
                'koszt': 0,
                'arkusze_B1': 0,
                'czas_h': 0,
                'opis': 'Papier już docięty - bez kosztu cięcia'
            }
        
        # Pobierz konfigurację cięcia
        config = getattr(self, 'ciecie_papieru', {})
        if not config:
            # Domyślne wartości jeśli brak konfiguracji
            config = {
                'koszt_roboczogodziny_pln': 60.0,
                'wydajnosc_arkuszy_h': 500,
                'wymiary_zakupu_mm': {'szerokosc': 700, 'wysokosc': 1000},
                'koszt_przygotowania_pln': 20.0
            }
        
        szerokosc_ark, wysokosc_ark = format_arkusza_mm
        B1_szer = config['wymiary_zakupu_mm']['szerokosc']
        B1_wys = config['wymiary_zakupu_mm']['wysokosc']
        
        # Sprawdź czy arkusz drukarski mieści się w B1
        if szerokosc_ark > B1_szer or wysokosc_ark > B1_wys:
            # Może po obrocie?
            if wysokosc_ark <= B1_szer and szerokosc_ark <= B1_wys:
                # Pasuje po obrocie
                szerokosc_ark, wysokosc_ark = wysokosc_ark, szerokosc_ark
            else:
                # Nie pasuje wcale - zwróć koszt 0 (zakładamy że kupiony w rozmiarze)
                return {
                    'koszt': 0,
                    'arkusze_B1': 0,
                    'czas_h': 0,
                    'opis': f'Format {szerokosc_ark}×{wysokosc_ark}mm większy niż B1 - papier kupiony w rozmiarze'
                }
        
        # Oblicz ile arkuszy drukarskich wyčnie się z 1 arkusza B1
        # Sprawdzamy dwie orientacje
        uzytkow_pionowo = (B1_szer // szerokosc_ark) * (B1_wys // wysokosc_ark)
        uzytkow_poziomo = (B1_szer // wysokosc_ark) * (B1_wys // szerokosc_ark)
        uzytkow_z_B1 = max(uzytkow_pionowo, uzytkow_poziomo)
        
        if uzytkow_z_B1 == 0:
            # Arkusz większy niż B1
            return {
                'koszt': 0,
                'arkusze_B1': 0,
                'czas_h': 0,
                'opis': 'Format większy niż B1 - papier kupiony w rozmiarze'
            }
        
        # Oblicz ile arkuszy B1 potrzeba
        import math
        arkusze_B1_potrzebne = math.ceil(ilosc_arkuszy / uzytkow_z_B1)
        
        # Oblicz czas cięcia
        wydajnosc = config['wydajnosc_arkuszy_h']  # arkuszy drukarskich / godzinę
        czas_ciecia_h = ilosc_arkuszy / wydajnosc
        
        # Oblicz koszt
        koszt_roboczogodziny = config['koszt_roboczogodziny_pln']
        koszt_przygotowania = config['koszt_przygotowania_pln']
        koszt_ciecia = (czas_ciecia_h * koszt_roboczogodziny) + koszt_przygotowania
        
        return {
            'koszt': koszt_ciecia,
            'arkusze_B1': arkusze_B1_potrzebne,
            'uzytkow_z_B1': uzytkow_z_B1,
            'czas_h': czas_ciecia_h,
            'opis': f'Cięcie {ilosc_arkuszy} ark. z {arkusze_B1_potrzebne} ark. B1 ({uzytkow_z_B1} użytków/B1)'
        }
    
    def kalkuluj_zlecenie(self, dane: Dict) -> KalkulacjaZlecenia:
        """
        Główna funkcja kalkulacji całego zlecenia
        """
        # Parsowanie danych wejściowych
        format_mm = tuple(dane['format_wydruku_mm'])
        naklad = dane['naklad']
        rodzaj_papieru = dane['rodzaj_papieru']
        gramatura = dane['gramatura']
        kolorystyka = dane['kolorystyka_cmyk']
        priorytet = dane.get('priorytet_optymalizacji', 'Zrównoważony')
        marza = dane.get('marza_procent', 20)
        
        # KROK 1: Optymalizacja formatu
        propozycje = self.optymalizuj_format(
            format_mm, naklad, rodzaj_papieru, gramatura, priorytet
        )
        
        if not propozycje:
            raise ValueError("Nie znaleziono odpowiedniego formatu arkusza!")
        
        wybrany_format = propozycje[0]
        
        # KROK 2: Kalkulacja druku
        kalk_druku = self.kalkuluj_druk(
            wybrany_format.ilosc_arkuszy,
            kolorystyka,
            dane.get('ilosc_form', 4)
        )
        
        # KROK 3: Kolory specjalne
        kalk_kolory = self.kalkuluj_kolory_specjalne(
            dane.get('kolory_specjalne', [])
        )
        
        # Obliczenie wagi papieru (w kg)
        waga_kg = (wybrany_format.powierzchnia * gramatura * wybrany_format.ilosc_arkuszy) / 1000
        
        # KROK 4: Uszlachetnienia
        kalk_uszlach = self.kalkuluj_uszlachetnienia(
            dane.get('uszlachetnienia', []),
            wybrany_format.ilosc_arkuszy,
            wybrany_format.powierzchnia,
            naklad=naklad,
            waga_kg=waga_kg
        )
        
        # KROK 5: Obróbka
        kalk_obrobka = self.kalkuluj_obrobke(
            dane.get('obrobka', []),
            naklad,
            powierzchnia_arkusza=wybrany_format.powierzchnia,
            ilosc_arkuszy=wybrany_format.ilosc_arkuszy,
            waga_kg=waga_kg
        )
        
        # KROK 6: Pakowanie i transport
        kalk_pak_trans = self.kalkuluj_pakowanie_transport(
            dane.get('pakowanie', 'Folia stretch (standard)'),
            dane.get('transport', 'Odbiór własny')
        )
        
        # KROK 6.5: Cięcie papieru z arkuszy B1
        wymaga_ciecia = dane.get('wymaga_ciecia_papieru', True)  # Domyślnie: TAK
        kalk_ciecie = self.kalkuluj_ciecie_papieru(
            (wybrany_format.szerokosc, wybrany_format.wysokosc),
            wybrany_format.ilosc_arkuszy,
            wymaga_ciecia
        )
        
        # KROK 7: Suma kosztów
        suma_netto = (
            wybrany_format.koszt_papieru +
            kalk_druku['razem'] +
            kalk_kolory['koszt'] +
            kalk_uszlach['koszt'] +
            kalk_obrobka['koszt'] +
            kalk_pak_trans['razem'] +
            kalk_ciecie['koszt']  # Dodany koszt cięcia
        )
        
        # KROK 8: Marża
        cena_z_marza = suma_netto * (1 + marza / 100)
        
        # KROK 9: VAT
        cena_brutto = cena_z_marza * 1.23
        
        # KROK 10: Czas realizacji
        czas_razem = (
            kalk_druku['czas_h'] +
            kalk_kolory['czas_h'] +
            kalk_uszlach['czas_h'] +
            kalk_obrobka['czas_h'] +
            kalk_ciecie['czas_h']  # Dodany czas cięcia
        )
        
        # KROK 11: Waga
        waga_kg = wybrany_format.ilosc_arkuszy * wybrany_format.powierzchnia * (gramatura / 1000)
        
        # Tworzenie obiektu wyniku
        kalkulacja = KalkulacjaZlecenia(
            nazwa_produktu=dane.get('nazwa_produktu', 'Bez nazwy'),
            format_wydruku_mm=format_mm,
            naklad=naklad,
            rodzaj_papieru=rodzaj_papieru,
            gramatura=gramatura,
            kolorysyka_cmyk=kolorystyka,
            kolory_specjalne=dane.get('kolory_specjalne', []),
            uszlachetnienia=dane.get('uszlachetnienia', []),
            obrobka=dane.get('obrobka', []),
            pakowanie=dane.get('pakowanie', ''),
            transport=dane.get('transport', ''),
            marza_procent=marza,
            priorytet_optymalizacji=priorytet,
            
            wybrany_format=wybrany_format,
            alternatywne_formaty=propozycje[1:4] if len(propozycje) > 1 else [],
            
            koszt_papieru=wybrany_format.koszt_papieru,
            koszt_druku=kalk_druku['razem'],
            koszt_kolorow_spec=kalk_kolory['koszt'],
            koszt_uszlachetnien=kalk_uszlach['koszt'],
            koszt_obrobki=kalk_obrobka['koszt'],
            koszt_ciecia_papieru=kalk_ciecie['koszt'],  # Nowe pole: koszt cięcia
            koszt_pakowania=kalk_pak_trans['pakowanie'],
            koszt_transportu=kalk_pak_trans['transport'],
            koszt_czasu_druku=kalk_druku['koszt_czasu_druku'],

            suma_kosztow_netto=suma_netto,
            cena_z_marza_netto=cena_z_marza,
            cena_brutto_vat23=cena_brutto,

            czas_realizacji_h=czas_razem,
            czas_druku_h=kalk_druku['czas_druku_h'],
            waga_kg=waga_kg,
            
            # Kontrahent (v1.2)
            kontrahent_id=dane.get('kontrahent_id'),
            kontrahent=dane.get('kontrahent')
        )
        
        return kalkulacja


def drukuj_oferte(kalkulacja: KalkulacjaZlecenia):
    """Formatuje i drukuje ofertę"""
    print("\n" + "="*80)
    print("OFERTA CENOWA - DRUK OFFSETOWY".center(80))
    print("="*80)
    
    print(f"\n📋 PRODUKT: {kalkulacja.nazwa_produktu}")
    print(f"📏 Format: {kalkulacja.format_wydruku_mm[0]}×{kalkulacja.format_wydruku_mm[1]} mm")
    print(f"📦 Nakład: {kalkulacja.naklad} szt")
    
    print(f"\n📄 MATERIAŁ:")
    print(f"   • Papier: {kalkulacja.rodzaj_papieru} {kalkulacja.gramatura}g/m²")
    print(f"   • Kolorystyka: {kalkulacja.kolorysyka_cmyk}")
    
    if kalkulacja.wybrany_format:
        f = kalkulacja.wybrany_format
        print(f"\n📐 WYBRANY FORMAT ARKUSZA: {f.format_name}")
        print(f"   • Wymiary: {f.szerokosc}×{f.wysokosc} mm")
        print(f"   • Użytków na arkusz: {f.uzytki_na_ark} ({f.orientacja})")
        print(f"   • Wykorzystanie: {f.wykorzystanie_procent:.1f}%")
        print(f"   • Odpady: {f.odpady_procent:.1f}%")
        print(f"   • Arkuszy potrzebnych: {f.ilosc_arkuszy}")
    
    if kalkulacja.alternatywne_formaty:
        print(f"\n🔄 ALTERNATYWNE FORMATY:")
        for i, alt in enumerate(kalkulacja.alternatywne_formaty[:2], 1):
            print(f"   {i}. {alt.format_name}: {alt.uzytki_na_ark} użytków, "
                  f"wykorzystanie {alt.wykorzystanie_procent:.1f}%, "
                  f"koszt papieru {alt.koszt_papieru:.2f} PLN")
    
    print(f"\n💰 KALKULACJA KOSZTÓW:")
    print(f"   • Papier:              {kalkulacja.koszt_papieru:>10.2f} PLN")
    print(f"   • Druk:                {kalkulacja.koszt_druku:>10.2f} PLN")
    if kalkulacja.koszt_czasu_druku > 0:
        print(f"       • Czas druku:       {kalkulacja.koszt_czasu_druku:>10.2f} PLN")
    if kalkulacja.koszt_kolorow_spec > 0:
        print(f"   • Kolory specjalne:    {kalkulacja.koszt_kolorow_spec:>10.2f} PLN")
    if kalkulacja.koszt_uszlachetnien > 0:
        print(f"   • Uszlachetnienia:     {kalkulacja.koszt_uszlachetnien:>10.2f} PLN")
    if kalkulacja.koszt_obrobki > 0:
        print(f"   • Obróbka:             {kalkulacja.koszt_obrobki:>10.2f} PLN")
    if kalkulacja.koszt_pakowania > 0:
        print(f"   • Pakowanie:           {kalkulacja.koszt_pakowania:>10.2f} PLN")
    if kalkulacja.koszt_transportu > 0:
        print(f"   • Transport:           {kalkulacja.koszt_transportu:>10.2f} PLN")
    
    print(f"   " + "-"*40)
    print(f"   SUMA KOSZTÓW NETTO:    {kalkulacja.suma_kosztow_netto:>10.2f} PLN")
    print(f"   Marża ({kalkulacja.marza_procent}%):         {kalkulacja.cena_z_marza_netto - kalkulacja.suma_kosztow_netto:>10.2f} PLN")
    print(f"   " + "-"*40)
    print(f"   CENA NETTO:            {kalkulacja.cena_z_marza_netto:>10.2f} PLN")
    print(f"   VAT 23%:               {kalkulacja.cena_brutto_vat23 - kalkulacja.cena_z_marza_netto:>10.2f} PLN")
    print(f"   " + "="*40)
    print(f"   CENA BRUTTO:           {kalkulacja.cena_brutto_vat23:>10.2f} PLN")
    
    print(f"\n⏱️  CZAS REALIZACJI: {kalkulacja.czas_realizacji_h:.1f} godz roboczych")
    print(f"⚖️  WAGA: {kalkulacja.waga_kg:.2f} kg")
    
    print(f"\n🎯 PRIORYTET OPTYMALIZACJI: {kalkulacja.priorytet_optymalizacji}")
    
    print("\n" + "="*80)


# PRZYKŁAD UŻYCIA
if __name__ == "__main__":
    kalkulator = KalkulatorDruku()
    
    # Przykładowe zlecenie
    zlecenie = {
        'nazwa_produktu': 'Plakat A2 reklamowy',
        'format_wydruku_mm': (420, 594),  # A2
        'naklad': 2000,
        'rodzaj_papieru': 'Kreda błysk',
        'gramatura': 150,
        'kolorystyka_cmyk': '4+0',
        'ilosc_form': 4,
        'kolory_specjalne': [],
        'uszlachetnienia': ['Folia mat'],
        'obrobka': ['Cięcie formatowe (standardowe)'],
        'pakowanie': 'Karton + folia',
        'transport': 'Kurier standardowy (30-50 kg)',
        'marza_procent': 20,
        'priorytet_optymalizacji': 'Najniższy koszt'
    }
    
    print("🖨️  KALKULATOR DRUKU OFFSETOWEGO V2.0")
    print("Rozpoczynam kalkulację zlecenia...\n")
    
    wynik = kalkulator.kalkuluj_zlecenie(zlecenie)
    drukuj_oferte(wynik)
    
    # Eksport do JSON
    wynik_dict = asdict(wynik)
    with open('/home/user/oferta_przyklad.json', 'w', encoding='utf-8') as f:
        json.dump(wynik_dict, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Oferta zapisana do pliku: oferta_przyklad.json")
