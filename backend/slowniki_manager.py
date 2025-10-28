"""
Menedżer słowników - zarządzanie danymi, walidacja, zapis do pliku
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime
import copy


class SlownikiManager:
    """Zarządza słownikami danych z zapisem do pliku JSON"""
    
    def __init__(self, plik_json='slowniki_data.json'):
        """
        Args:
            plik_json: Ścieżka do pliku JSON z danymi
        """
        self.plik_json = plik_json
        self.slowniki = self._zaladuj_slowniki()
        self.historia_zmian = []
        
    def _zaladuj_slowniki(self) -> Dict:
        """Załaduj słowniki z pliku lub utwórz domyślne"""
        from slowniki_danych import (
            PAPIERY, USZLACHETNIENIA, OBROBKA_WYKONCZ,
            KOLORY_SPECJALNE, PAKOWANIE, TRANSPORT,
            FORMATY_ARKUSZY, STAWKI_DRUKARNI,
            MARZA_PREDEFINIOWANE, PRIORYTETY_OPTYMALIZACJI
        )
        
        # Spróbuj załadować z pliku
        if os.path.exists(self.plik_json):
            try:
                with open(self.plik_json, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Błąd wczytywania {self.plik_json}: {e}")
                print("📦 Używam domyślnych wartości")
        
        # Domyślne wartości ze słowników
        return {
            "papiery": PAPIERY,
            "uszlachetnienia": USZLACHETNIENIA,
            "obrobka": OBROBKA_WYKONCZ,
            "kolory_specjalne": KOLORY_SPECJALNE,
            "pakowanie": PAKOWANIE,
            "transport": TRANSPORT,
            "formaty": FORMATY_ARKUSZY,
            "stawki": STAWKI_DRUKARNI,
            "marza": MARZA_PREDEFINIOWANE,
            "priorytety": PRIORYTETY_OPTYMALIZACJI
        }
    
    def zapisz_slowniki(self) -> bool:
        """Zapisz słowniki do pliku JSON"""
        try:
            with open(self.plik_json, 'w', encoding='utf-8') as f:
                json.dump(self.slowniki, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Błąd zapisu: {e}")
            return False
    
    def get_slownik(self, kategoria: str) -> Dict:
        """Pobierz słownik"""
        return self.slowniki.get(kategoria, {})
    
    def get_wszystkie(self) -> Dict:
        """Pobierz wszystkie słowniki"""
        return self.slowniki
    
    # ==================== PAPIERY ====================
    
    def dodaj_papier(self, nazwa: str, gramatury: List[int], ceny: List[float],
                     kategoria: str = 'niepowlekany') -> Dict:
        """Dodaj nowy rodzaj papieru"""
        if nazwa in self.slowniki['papiery']:
            raise ValueError(f"Papier '{nazwa}' już istnieje")
        
        if len(gramatury) != len(ceny):
            raise ValueError("Liczba gramatur musi być równa liczbie cen")
        
        if any(g <= 0 for g in gramatury):
            raise ValueError("Gramatury muszą być dodatnie")
        
        if any(c <= 0 for c in ceny):
            raise ValueError("Ceny muszą być dodatnie")
        
        # Konwersja ceny z listy na dict (gramatura → cena)
        gramatury_sorted = sorted(gramatury)
        ceny_dict = {str(gram): cena for gram, cena in zip(gramatury_sorted, ceny)}
        
        self.slowniki['papiery'][nazwa] = {
            'gramatury': gramatury_sorted,
            'ceny': ceny_dict,
            'kategoria': kategoria
        }
        
        self._zapisz_zmiane('papiery', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['papiery'][nazwa]
    
    def edytuj_papier(self, stara_nazwa: str, nowa_nazwa: str = None, 
                      gramatury: List[int] = None, ceny: List[float] = None,
                      kategoria: str = None) -> Dict:
        """Edytuj istniejący papier"""
        if stara_nazwa not in self.slowniki['papiery']:
            raise ValueError(f"Papier '{stara_nazwa}' nie istnieje")
        
        papier = self.slowniki['papiery'][stara_nazwa]
        
        # Aktualizuj nazwę
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['papiery']:
                raise ValueError(f"Papier '{nowa_nazwa}' już istnieje")
            self.slowniki['papiery'][nowa_nazwa] = papier
            del self.slowniki['papiery'][stara_nazwa]
            stara_nazwa = nowa_nazwa
        
        # Aktualizuj gramatury i ceny (konwersja na dict)
        if gramatury is not None:
            if ceny is None:
                raise ValueError("Musisz podać ceny dla nowych gramatur")
            if len(gramatury) != len(ceny):
                raise ValueError("Liczba gramatur musi być równa liczbie cen")
            
            gramatury_sorted = sorted(gramatury)
            ceny_dict = {str(gram): cena for gram, cena in zip(gramatury_sorted, ceny)}
            
            papier['gramatury'] = gramatury_sorted
            papier['ceny'] = ceny_dict
        
        # Aktualizuj kategorię
        if kategoria is not None:
            papier['kategoria'] = kategoria
        
        self._zapisz_zmiane('papiery', 'edycja', stara_nazwa)
        self.zapisz_slowniki()
        
        return papier
    
    def usun_papier(self, nazwa: str) -> bool:
        """Usuń papier"""
        if nazwa not in self.slowniki['papiery']:
            raise ValueError(f"Papier '{nazwa}' nie istnieje")
        
        del self.slowniki['papiery'][nazwa]
        self._zapisz_zmiane('papiery', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== USZLACHETNIENIA ====================
    
    def dodaj_uszlachetnienie(self, nazwa: str, typ: str, cena_pln: float, 
                              jednostka: str = '1000 ark', opis: str = '',
                              typ_jednostki: str = 'sztukowa') -> Dict:
        """Dodaj nowe uszlachetnienie"""
        if nazwa in self.slowniki['uszlachetnienia']:
            raise ValueError(f"Uszlachetnienie '{nazwa}' już istnieje")
        
        if cena_pln <= 0:
            raise ValueError("Cena musi być dodatnia")
        
        if typ not in ['UV', 'Dyspersyjny', 'Folia', 'Tłoczenie']:
            raise ValueError(f"Nieprawidłowy typ: {typ}")
        
        self.slowniki['uszlachetnienia'][nazwa] = {
            'typ': typ,
            'cena_pln': cena_pln,
            'jednostka': jednostka,
            'typ_jednostki': typ_jednostki,
            'opis': opis
        }
        
        self._zapisz_zmiane('uszlachetnienia', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['uszlachetnienia'][nazwa]
    
    def edytuj_uszlachetnienie(self, stara_nazwa: str, nowa_nazwa: str = None,
                                typ: str = None, cena_pln: float = None,
                                jednostka: str = None, opis: str = None,
                                typ_jednostki: str = None) -> Dict:
        """Edytuj uszlachetnienie"""
        if stara_nazwa not in self.slowniki['uszlachetnienia']:
            raise ValueError(f"Uszlachetnienie '{stara_nazwa}' nie istnieje")
        
        uszl = self.slowniki['uszlachetnienia'][stara_nazwa]
        
        # Zmiana nazwy
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['uszlachetnienia']:
                raise ValueError(f"Uszlachetnienie '{nowa_nazwa}' już istnieje")
            self.slowniki['uszlachetnienia'][nowa_nazwa] = uszl
            del self.slowniki['uszlachetnienia'][stara_nazwa]
            stara_nazwa = nowa_nazwa
        
        # Aktualizuj pola
        if typ is not None:
            uszl['typ'] = typ
        if cena_pln is not None:
            if cena_pln <= 0:
                raise ValueError("Cena musi być dodatnia")
            uszl['cena_pln'] = cena_pln
        if jednostka is not None:
            uszl['jednostka'] = jednostka
        if typ_jednostki is not None:
            uszl['typ_jednostki'] = typ_jednostki
        if opis is not None:
            uszl['opis'] = opis
        
        self._zapisz_zmiane('uszlachetnienia', 'edycja', stara_nazwa)
        self.zapisz_slowniki()
        
        return uszl
    
    def usun_uszlachetnienie(self, nazwa: str) -> bool:
        """Usuń uszlachetnienie"""
        if nazwa not in self.slowniki['uszlachetnienia']:
            raise ValueError(f"Uszlachetnienie '{nazwa}' nie istnieje")
        
        del self.slowniki['uszlachetnienia'][nazwa]
        self._zapisz_zmiane('uszlachetnienia', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== OBRÓBKA ====================
    
    def dodaj_obrobke(self, nazwa: str, cena_pln: float, jednostka: str = '1000 szt',
                      opis: str = '', typ_jednostki: str = 'sztukowa') -> Dict:
        """Dodaj nową operację obróbki"""
        if nazwa in self.slowniki['obrobka']:
            raise ValueError(f"Obróbka '{nazwa}' już istnieje")
        
        if cena_pln <= 0:
            raise ValueError("Cena musi być dodatnia")
        
        self.slowniki['obrobka'][nazwa] = {
            'cena_pln': cena_pln,
            'jednostka': jednostka,
            'typ_jednostki': typ_jednostki,
            'opis': opis
        }
        
        self._zapisz_zmiane('obrobka', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['obrobka'][nazwa]
    
    def edytuj_obrobke(self, stara_nazwa: str, nowa_nazwa: str = None,
                       cena_pln: float = None, jednostka: str = None,
                       opis: str = None, typ_jednostki: str = None) -> Dict:
        """Edytuj obróbkę"""
        if stara_nazwa not in self.slowniki['obrobka']:
            raise ValueError(f"Obróbka '{stara_nazwa}' nie istnieje")
        
        obr = self.slowniki['obrobka'][stara_nazwa]
        
        # Zmiana nazwy
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['obrobka']:
                raise ValueError(f"Obróbka '{nowa_nazwa}' już istnieje")
            self.slowniki['obrobka'][nowa_nazwa] = obr
            del self.slowniki['obrobka'][stara_nazwa]
            stara_nazwa = nowa_nazwa
        
        # Aktualizuj pola
        if cena_pln is not None:
            if cena_pln <= 0:
                raise ValueError("Cena musi być dodatnia")
            obr['cena_pln'] = cena_pln
        if jednostka is not None:
            obr['jednostka'] = jednostka
        if typ_jednostki is not None:
            obr['typ_jednostki'] = typ_jednostki
        if opis is not None:
            obr['opis'] = opis
        
        self._zapisz_zmiane('obrobka', 'edycja', stara_nazwa)
        self.zapisz_slowniki()
        
        return obr
    
    def usun_obrobke(self, nazwa: str) -> bool:
        """Usuń obróbkę"""
        if nazwa not in self.slowniki['obrobka']:
            raise ValueError(f"Obróbka '{nazwa}' nie istnieje")
        
        del self.slowniki['obrobka'][nazwa]
        self._zapisz_zmiane('obrobka', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== RODZAJE PRAC ====================
    
    def dodaj_rodzaj_pracy(self, nazwa: str, szerokosc: int, wysokosc: int, 
                           opis: str = '') -> Dict:
        """Dodaj nowy rodzaj pracy (np. ulotka, wizytówka)"""
        if 'rodzaje_prac' not in self.slowniki:
            self.slowniki['rodzaje_prac'] = {}
        
        if nazwa in self.slowniki['rodzaje_prac']:
            raise ValueError(f"Rodzaj pracy '{nazwa}' już istnieje")
        
        if szerokosc <= 0 or wysokosc <= 0:
            raise ValueError("Wymiary muszą być dodatnie")
        
        self.slowniki['rodzaje_prac'][nazwa] = {
            'szerokosc': int(szerokosc),
            'wysokosc': int(wysokosc),
            'opis': opis
        }
        
        self._zapisz_zmiane('rodzaje_prac', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['rodzaje_prac'][nazwa]
    
    def edytuj_rodzaj_pracy(self, stara_nazwa: str, nowa_nazwa: str = None,
                            szerokosc: int = None, wysokosc: int = None,
                            opis: str = None) -> Dict:
        """Edytuj istniejący rodzaj pracy"""
        if 'rodzaje_prac' not in self.slowniki:
            self.slowniki['rodzaje_prac'] = {}
        
        if stara_nazwa not in self.slowniki['rodzaje_prac']:
            raise ValueError(f"Rodzaj pracy '{stara_nazwa}' nie istnieje")
        
        dane = self.slowniki['rodzaje_prac'][stara_nazwa]
        
        # Aktualizuj wymiary
        if szerokosc is not None:
            if szerokosc <= 0:
                raise ValueError("Szerokość musi być dodatnia")
            dane['szerokosc'] = int(szerokosc)
        
        if wysokosc is not None:
            if wysokosc <= 0:
                raise ValueError("Wysokość musi być dodatnia")
            dane['wysokosc'] = int(wysokosc)
        
        if opis is not None:
            dane['opis'] = opis
        
        # Zmień nazwę jeśli podano
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['rodzaje_prac']:
                raise ValueError(f"Rodzaj pracy '{nowa_nazwa}' już istnieje")
            self.slowniki['rodzaje_prac'][nowa_nazwa] = dane
            del self.slowniki['rodzaje_prac'][stara_nazwa]
            self._zapisz_zmiane('rodzaje_prac', 'edycja', f'{stara_nazwa} -> {nowa_nazwa}')
        else:
            self._zapisz_zmiane('rodzaje_prac', 'edycja', stara_nazwa)
        
        self.zapisz_slowniki()
        return dane
    
    def usun_rodzaj_pracy(self, nazwa: str) -> bool:
        """Usuń rodzaj pracy"""
        if 'rodzaje_prac' not in self.slowniki:
            self.slowniki['rodzaje_prac'] = {}
        
        if nazwa not in self.slowniki['rodzaje_prac']:
            raise ValueError(f"Rodzaj pracy '{nazwa}' nie istnieje")
        
        del self.slowniki['rodzaje_prac'][nazwa]
        self._zapisz_zmiane('rodzaje_prac', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== KOLORY SPECJALNE ====================
    
    def dodaj_kolor_specjalny(self, nazwa: str, cena_pln: float, 
                              cena_preperatu_pln: float = 50.0, opis: str = '') -> Dict:
        """Dodaj nowy kolor specjalny"""
        if nazwa in self.slowniki['kolory_specjalne']:
            raise ValueError(f"Kolor '{nazwa}' już istnieje")
        
        if cena_pln <= 0 or cena_preperatu_pln < 0:
            raise ValueError("Ceny muszą być dodatnie")
        
        self.slowniki['kolory_specjalne'][nazwa] = {
            'cena_pln': cena_pln,
            'cena_preperatu_pln': cena_preperatu_pln,
            'opis': opis
        }
        
        self._zapisz_zmiane('kolory_specjalne', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['kolory_specjalne'][nazwa]
    
    def edytuj_kolor_specjalny(self, stara_nazwa: str, nowa_nazwa: str = None,
                                cena_pln: float = None, cena_preperatu_pln: float = None,
                                opis: str = None) -> Dict:
        """Edytuj kolor specjalny"""
        if stara_nazwa not in self.slowniki['kolory_specjalne']:
            raise ValueError(f"Kolor '{stara_nazwa}' nie istnieje")
        
        kolor = self.slowniki['kolory_specjalne'][stara_nazwa]
        
        # Zmiana nazwy
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['kolory_specjalne']:
                raise ValueError(f"Kolor '{nowa_nazwa}' już istnieje")
            self.slowniki['kolory_specjalne'][nowa_nazwa] = kolor
            del self.slowniki['kolory_specjalne'][stara_nazwa]
            stara_nazwa = nowa_nazwa
        
        # Aktualizuj pola
        if cena_pln is not None:
            if cena_pln <= 0:
                raise ValueError("Cena musi być dodatnia")
            kolor['cena_pln'] = cena_pln
        if cena_preperatu_pln is not None:
            if cena_preperatu_pln < 0:
                raise ValueError("Cena preparatu nie może być ujemna")
            kolor['cena_preperatu_pln'] = cena_preperatu_pln
        if opis is not None:
            kolor['opis'] = opis
        
        self._zapisz_zmiane('kolory_specjalne', 'edycja', stara_nazwa)
        self.zapisz_slowniki()
        
        return kolor
    
    def usun_kolor_specjalny(self, nazwa: str) -> bool:
        """Usuń kolor specjalny"""
        if nazwa not in self.slowniki['kolory_specjalne']:
            raise ValueError(f"Kolor '{nazwa}' nie istnieje")
        
        del self.slowniki['kolory_specjalne'][nazwa]
        self._zapisz_zmiane('kolory_specjalne', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== PAKOWANIE ====================
    
    def dodaj_pakowanie(self, nazwa: str, cena_pln: float, opis: str = '') -> Dict:
        """Dodaj nową opcję pakowania"""
        if nazwa in self.slowniki['pakowanie']:
            raise ValueError(f"Pakowanie '{nazwa}' już istnieje")
        
        if cena_pln < 0:
            raise ValueError("Cena nie może być ujemna")
        
        self.slowniki['pakowanie'][nazwa] = {
            'cena_pln': cena_pln,
            'opis': opis
        }
        
        self._zapisz_zmiane('pakowanie', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['pakowanie'][nazwa]
    
    def edytuj_pakowanie(self, stara_nazwa: str, nowa_nazwa: str = None,
                         cena_pln: float = None, opis: str = None) -> Dict:
        """Edytuj pakowanie"""
        if stara_nazwa not in self.slowniki['pakowanie']:
            raise ValueError(f"Pakowanie '{stara_nazwa}' nie istnieje")
        
        pak = self.slowniki['pakowanie'][stara_nazwa]
        
        # Zmiana nazwy
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['pakowanie']:
                raise ValueError(f"Pakowanie '{nowa_nazwa}' już istnieje")
            self.slowniki['pakowanie'][nowa_nazwa] = pak
            del self.slowniki['pakowanie'][stara_nazwa]
            stara_nazwa = nowa_nazwa
        
        # Aktualizuj pola
        if cena_pln is not None:
            if cena_pln < 0:
                raise ValueError("Cena nie może być ujemna")
            pak['cena_pln'] = cena_pln
        if opis is not None:
            pak['opis'] = opis
        
        self._zapisz_zmiane('pakowanie', 'edycja', stara_nazwa)
        self.zapisz_slowniki()
        
        return pak
    
    def usun_pakowanie(self, nazwa: str) -> bool:
        """Usuń pakowanie"""
        if nazwa not in self.slowniki['pakowanie']:
            raise ValueError(f"Pakowanie '{nazwa}' nie istnieje")
        
        del self.slowniki['pakowanie'][nazwa]
        self._zapisz_zmiane('pakowanie', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== TRANSPORT ====================
    
    def dodaj_transport(self, nazwa: str, cena_pln: float, opis: str = '') -> Dict:
        """Dodaj nową opcję transportu"""
        if nazwa in self.slowniki['transport']:
            raise ValueError(f"Transport '{nazwa}' już istnieje")
        
        if cena_pln < 0:
            raise ValueError("Cena nie może być ujemna")
        
        self.slowniki['transport'][nazwa] = {
            'cena_pln': cena_pln,
            'opis': opis
        }
        
        self._zapisz_zmiane('transport', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['transport'][nazwa]
    
    def edytuj_transport(self, stara_nazwa: str, nowa_nazwa: str = None,
                         cena_pln: float = None, opis: str = None) -> Dict:
        """Edytuj transport"""
        if stara_nazwa not in self.slowniki['transport']:
            raise ValueError(f"Transport '{stara_nazwa}' nie istnieje")
        
        trans = self.slowniki['transport'][stara_nazwa]
        
        # Zmiana nazwy
        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            if nowa_nazwa in self.slowniki['transport']:
                raise ValueError(f"Transport '{nowa_nazwa}' już istnieje")
            self.slowniki['transport'][nowa_nazwa] = trans
            del self.slowniki['transport'][stara_nazwa]
            stara_nazwa = nowa_nazwa
        
        # Aktualizuj pola
        if cena_pln is not None:
            if cena_pln < 0:
                raise ValueError("Cena nie może być ujemna")
            trans['cena_pln'] = cena_pln
        if opis is not None:
            trans['opis'] = opis
        
        self._zapisz_zmiane('transport', 'edycja', stara_nazwa)
        self.zapisz_slowniki()
        
        return trans
    
    def usun_transport(self, nazwa: str) -> bool:
        """Usuń transport"""
        if nazwa not in self.slowniki['transport']:
            raise ValueError(f"Transport '{nazwa}' nie istnieje")
        
        del self.slowniki['transport'][nazwa]
        self._zapisz_zmiane('transport', 'usunięcie', nazwa)
        self.zapisz_slowniki()
        
        return True
    
    # ==================== STAWKI ====================
    
    def edytuj_stawke(self, klucz: str, wartosc: float) -> Dict:
        """Edytuj stawkę drukarni"""
        # Mapowanie kluczy (frontend może używać z sufiksem _pln)
        stawki_map = {
            'roboczogodzina_przygotowania_pln': 'roboczogodzina_przygotowania',
            'roboczogodzina_druku_pln': 'roboczogodzina_druku',
            'forma_offsetowa_pln': 'koszt_formy_drukowej',
            'koszt_1000_arkuszy_pln': 'stawka_nakladu_1000_arkuszy',
            # Bez sufiksu (jeśli backend używa bezpośrednio)
            'roboczogodzina_przygotowania': 'roboczogodzina_przygotowania',
            'stawka_nakladu_1000_arkuszy': 'stawka_nakladu_1000_arkuszy',
            'koszt_formy_drukowej': 'koszt_formy_drukowej',
            'szybkosc_druku_arkuszy_h': 'szybkosc_druku_arkuszy_h'
        }
        
        if klucz not in stawki_map:
            raise ValueError(f"Nieprawidłowy klucz stawki: {klucz}")
        
        # Walidacja wartości (obsługa None, NaN, pustych wartości)
        if wartosc is None:
            raise ValueError(f"Wartość dla '{klucz}' nie może być pusta")
        
        # Sprawdzenie czy wartość jest liczbą (JavaScript może wysłać NaN jako null)
        if not isinstance(wartosc, (int, float)):
            raise ValueError(f"Wartość dla '{klucz}' musi być liczbą")
        
        # Walidacja wartości dodatniej
        if wartosc <= 0:
            raise ValueError(f"Stawka '{klucz}' musi być dodatnia (otrzymano: {wartosc})")
        
        klucz_realny = stawki_map[klucz]
        self.slowniki['stawki'][klucz_realny] = float(wartosc)
        self._zapisz_zmiane('stawki', 'edycja', klucz_realny)
        self.zapisz_slowniki()
        
        return self.slowniki['stawki']
    
    # ==================== CIĘCIE PAPIERU ====================
    
    def edytuj_ciecie_papieru(self, koszt_roboczogodziny: float, wydajnosc: int, 
                               wymiary: Dict, koszt_przygotowania: float) -> Dict:
        """Edytuj parametry cięcia papieru"""
        # Walidacja
        if koszt_roboczogodziny <= 0:
            raise ValueError("Koszt roboczogodziny musi być dodatni")
        if wydajnosc <= 0:
            raise ValueError("Wydajność musi być dodatnia")
        if koszt_przygotowania < 0:
            raise ValueError("Koszt przygotowania nie może być ujemny")
        
        if 'ciecie_papieru' not in self.slowniki:
            self.slowniki['ciecie_papieru'] = {}
        
        self.slowniki['ciecie_papieru']['koszt_roboczogodziny_pln'] = float(koszt_roboczogodziny)
        self.slowniki['ciecie_papieru']['wydajnosc_arkuszy_h'] = int(wydajnosc)
        self.slowniki['ciecie_papieru']['wymiary_zakupu_mm'] = wymiary
        self.slowniki['ciecie_papieru']['koszt_przygotowania_pln'] = float(koszt_przygotowania)
        
        self._zapisz_zmiane('ciecie_papieru', 'edycja', 'parametry')
        self.zapisz_slowniki()
        
        return self.slowniki['ciecie_papieru']
    
    # ==================== HISTORIA ZMIAN ====================
    
    def _zapisz_zmiane(self, kategoria: str, operacja: str, element: str):
        """Zapisz zmianę w historii"""
        zmiana = {
            'timestamp': datetime.now().isoformat(),
            'kategoria': kategoria,
            'operacja': operacja,
            'element': element
        }
        self.historia_zmian.insert(0, zmiana)
        
        # Ogranicz historię do 100 ostatnich zmian
        if len(self.historia_zmian) > 100:
            self.historia_zmian = self.historia_zmian[:100]
    
    def get_historia_zmian(self, limit: int = 50) -> List[Dict]:
        """Pobierz historię zmian"""
        return self.historia_zmian[:limit]
    
    # ==================== BACKUP ====================
    
    def utworz_backup(self) -> str:
        """Utwórz backup słowników"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"slowniki_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.slowniki, f, indent=2, ensure_ascii=False)
            return backup_file
        except Exception as e:
            raise Exception(f"Błąd tworzenia backupu: {e}")
    
    def przywroc_backup(self, backup_file: str) -> bool:
        """Przywróć słowniki z backupu"""
        if not os.path.exists(backup_file):
            raise ValueError(f"Plik backupu nie istnieje: {backup_file}")
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                self.slowniki = json.load(f)
            self.zapisz_slowniki()
            return True
        except Exception as e:
            raise Exception(f"Błąd przywracania backupu: {e}")
