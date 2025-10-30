"""
Menedżer słowników - zarządzanie danymi, walidacja, zapis do pliku
"""

import json
import os
from typing import Dict, Any, List, Optional
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
        self._migracje_wymagaja_zapisu = False
        self.slowniki = self._zaladuj_slowniki()
        self._mapuj_jednostki_na_kody()
        self.historia_zmian = []

        # Zapisz zmiany migracyjne (np. dodanie nowych słowników)
        if self._migracje_wymagaja_zapisu:
            self.zapisz_slowniki()
        
    def _zaladuj_slowniki(self) -> Dict:
        """Załaduj słowniki z pliku lub utwórz domyślne"""
        from slowniki_danych import (
            PAPIERY,
            KATEGORIE_PAPIERU,
            USZLACHETNIENIA,
            OBROBKA_WYKONCZ,
            KOLORY_SPECJALNE,
            KOLORYSTYKI_DRUKU,
            PAKOWANIE,
            TRANSPORT,
            FORMATY_ARKUSZY,
            STAWKI_DRUKARNI,
            MARZA_PREDEFINIOWANE,
            PRIORYTETY_OPTYMALIZACJI,
            RODZAJE_PRAC,
            CIECIE_PAPIERU,
            JEDNOSTKI,
        )

        defaults = {
            "papiery": PAPIERY,
            "kategorie_papieru": KATEGORIE_PAPIERU,
            "uszlachetnienia": USZLACHETNIENIA,
            "obrobka": OBROBKA_WYKONCZ,
            "kolory_specjalne": KOLORY_SPECJALNE,
            "kolorystyki": KOLORYSTYKI_DRUKU,
            "pakowanie": PAKOWANIE,
            "transport": TRANSPORT,
            "formaty": FORMATY_ARKUSZY,
            "stawki": STAWKI_DRUKARNI,
            "marza": MARZA_PREDEFINIOWANE,
            "priorytety": PRIORYTETY_OPTYMALIZACJI,
            "rodzaje_prac": RODZAJE_PRAC,
            "ciecie_papieru": CIECIE_PAPIERU,
            "jednostki": JEDNOSTKI,
        }

        # Spróbuj załadować z pliku
        if os.path.exists(self.plik_json):
            try:
                with open(self.plik_json, 'r', encoding='utf-8') as f:
                    dane = json.load(f)
                    dane = self._uzupelnij_domyslne_slowniki(dane, defaults)
                    self._dopelnij_kategorie_na_podstawie_papierow(dane)
                    self._dopelnij_spad_dla_rodzajow_prac(dane)
                    return dane
            except Exception as e:
                print(f"⚠️  Błąd wczytywania {self.plik_json}: {e}")
                print("📦 Używam domyślnych wartości")

        # Domyślne wartości ze słowników
        dane = {klucz: copy.deepcopy(wartosc) for klucz, wartosc in defaults.items()}
        self._dopelnij_kategorie_na_podstawie_papierow(dane)
        self._dopelnij_spad_dla_rodzajow_prac(dane)
        return dane

    def _dopelnij_spad_dla_rodzajow_prac(self, dane: Dict[str, Any]) -> None:
        """Uzupełnij brakujący parametr spadu w rodzajach prac."""
        if dane is None:
            return

        rodzaje = dane.get('rodzaje_prac')
        if not isinstance(rodzaje, dict) or not rodzaje:
            return

        zaktualizowano = False
        for definicja in rodzaje.values():
            if not isinstance(definicja, dict):
                continue
            if 'spad' not in definicja:
                definicja['spad'] = 2.5
                zaktualizowano = True

        if zaktualizowano:
            self._migracje_wymagaja_zapisu = True

    def _dopelnij_kategorie_na_podstawie_papierow(self, dane: Dict[str, Any]) -> None:
        """Dodaj brakujące kategorie papieru wykorzystywane przez papiery."""
        if dane is None:
            return

        papiery = dane.get('papiery', {})
        if not isinstance(papiery, dict) or not papiery:
            return

        kategorie = dane.get('kategorie_papieru')
        if not isinstance(kategorie, dict):
            kategorie = {}
            dane['kategorie_papieru'] = kategorie
            self._migracje_wymagaja_zapisu = True

        for rekord in papiery.values():
            if not isinstance(rekord, dict):
                continue
            kat_id = rekord.get('kategoria')
            if not kat_id:
                continue
            kat_id = str(kat_id).strip()
            if not kat_id:
                continue
            if kat_id in kategorie:
                continue

            kategorie[kat_id] = {
                'nazwa': self._formatuj_nazwe_kategorii(kat_id),
                'opis': ''
            }
            self._migracje_wymagaja_zapisu = True

    @staticmethod
    def _formatuj_nazwe_kategorii(kategoria_id: str) -> str:
        """Zwróć domyślną etykietę dla kategorii papieru."""
        if not kategoria_id:
            return 'Inne'

        kategoria_id = str(kategoria_id).strip()
        specjalne = {
            'etykietowy': 'Papier etykietowy',
            'inne': 'Inne'
        }

        if kategoria_id in specjalne:
            return specjalne[kategoria_id]

        return kategoria_id.replace('_', ' ').title()
    
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

    # ==================== JEDNOSTKI ====================

    def get_jednostki(self) -> Dict[str, Any]:
        return self.slowniki.get('jednostki', {})

    def dodaj_jednostke(self,
                        kod: str,
                        etykieta: str,
                        typ_jednostki: str,
                        mnoznik_domyslny: float,
                        slowa_kluczowe: Optional[List[str]] = None,
                        zrodlo_bazowej_ilosci: Optional[str] = None) -> Dict[str, Any]:
        if not kod or not etykieta or not typ_jednostki:
            raise ValueError("Kod, etykieta i typ jednostki są wymagane")

        kod_norm = kod.strip().upper()
        jednostki = self.slowniki.setdefault('jednostki', {})
        if kod_norm in jednostki:
            raise ValueError(f"Jednostka '{kod_norm}' już istnieje")

        typ_jednostki = typ_jednostki.strip()
        if typ_jednostki not in {'sztukowa', 'metrowa', 'wagowa'}:
            raise ValueError("Nieprawidłowy typ jednostki")

        if mnoznik_domyslny is None or float(mnoznik_domyslny) <= 0:
            raise ValueError("Mnożnik jednostki musi być dodatni")

        slowa = [s.strip().lower() for s in (slowa_kluczowe or []) if s.strip()]

        definicja = {
            'kod': kod_norm,
            'etykieta': etykieta.strip(),
            'typ_jednostki': typ_jednostki,
            'mnoznik_domyslny': float(mnoznik_domyslny),
            'slowa_kluczowe': slowa,
        }

        if zrodlo_bazowej_ilosci:
            definicja['zrodlo_bazowej_ilosci'] = zrodlo_bazowej_ilosci
        else:
            domyslne_zrodlo = {
                'sztukowa': 'naklad',
                'metrowa': 'powierzchnia',
                'wagowa': 'waga'
            }.get(typ_jednostki)
            if domyslne_zrodlo:
                definicja['zrodlo_bazowej_ilosci'] = domyslne_zrodlo

        jednostki[kod_norm] = definicja
        self._mapuj_jednostki_na_kody()
        self._zapisz_zmiane('jednostki', 'dodanie', kod_norm)
        self.zapisz_slowniki()

        return definicja

    def edytuj_jednostke(self,
                         stary_kod: str,
                         nowy_kod: Optional[str] = None,
                         etykieta: Optional[str] = None,
                         typ_jednostki: Optional[str] = None,
                         mnoznik_domyslny: Optional[float] = None,
                         slowa_kluczowe: Optional[List[str]] = None,
                         zrodlo_bazowej_ilosci: Optional[str] = None) -> Dict[str, Any]:
        jednostki = self.slowniki.setdefault('jednostki', {})
        stary_kod = stary_kod.strip().upper()
        if stary_kod not in jednostki:
            raise ValueError(f"Jednostka '{stary_kod}' nie istnieje")

        jednostka = jednostki[stary_kod]
        docelowy_kod = stary_kod

        if nowy_kod and nowy_kod.strip().upper() != stary_kod:
            nowy_kod_norm = nowy_kod.strip().upper()
            if nowy_kod_norm in jednostki:
                raise ValueError(f"Jednostka '{nowy_kod_norm}' już istnieje")
            jednostki[nowy_kod_norm] = jednostka
            del jednostki[stary_kod]
            jednostka['kod'] = nowy_kod_norm
            for kategoria in ('uszlachetnienia', 'obrobka'):
                for dane in self.slowniki.get(kategoria, {}).values():
                    if dane.get('kod_jednostki') == stary_kod:
                        dane['kod_jednostki'] = nowy_kod_norm
            docelowy_kod = nowy_kod_norm

        if etykieta is not None:
            jednostka['etykieta'] = etykieta.strip()

        if typ_jednostki is not None:
            typ_jednostki = typ_jednostki.strip()
            if typ_jednostki not in {'sztukowa', 'metrowa', 'wagowa'}:
                raise ValueError("Nieprawidłowy typ jednostki")
            jednostka['typ_jednostki'] = typ_jednostki

        if mnoznik_domyslny is not None:
            if float(mnoznik_domyslny) <= 0:
                raise ValueError("Mnożnik jednostki musi być dodatni")
            jednostka['mnoznik_domyslny'] = float(mnoznik_domyslny)

        if slowa_kluczowe is not None:
            jednostka['slowa_kluczowe'] = [s.strip().lower() for s in slowa_kluczowe if s.strip()]

        if zrodlo_bazowej_ilosci is not None:
            jednostka['zrodlo_bazowej_ilosci'] = zrodlo_bazowej_ilosci
        elif typ_jednostki is not None:
            domyslne_zrodlo = {
                'sztukowa': 'naklad',
                'metrowa': 'powierzchnia',
                'wagowa': 'waga'
            }[jednostka['typ_jednostki']]
            jednostka['zrodlo_bazowej_ilosci'] = domyslne_zrodlo

        self._mapuj_jednostki_na_kody()
        self._zapisz_zmiane('jednostki', 'edycja', docelowy_kod)
        self.zapisz_slowniki()

        return jednostka

    def usun_jednostke(self, kod: str) -> bool:
        jednostki = self.slowniki.setdefault('jednostki', {})
        kod = kod.strip().upper()
        if kod not in jednostki:
            raise ValueError(f"Jednostka '{kod}' nie istnieje")

        del jednostki[kod]

        for kategoria in ('uszlachetnienia', 'obrobka'):
            for dane in self.slowniki.get(kategoria, {}).values():
                if dane.get('kod_jednostki') == kod:
                    dane.pop('kod_jednostki', None)

        self._mapuj_jednostki_na_kody()
        self._zapisz_zmiane('jednostki', 'usunięcie', kod)
        self.zapisz_slowniki()

        return True

    def _uzupelnij_domyslne_slowniki(self, dane: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Uzupełnij brakujące sekcje słowników wartościami domyślnymi"""
        if dane is None:
            dane = {}

        for klucz, wartosc in defaults.items():
            if klucz not in dane or dane[klucz] in (None, {}):
                dane[klucz] = copy.deepcopy(wartosc)

        return dane

    def _mapuj_jednostki_na_kody(self) -> None:
        """Uzupełnij rekordy o kod jednostki oraz typ na podstawie słownika jednostek"""
        jednostki = self.slowniki.get('jednostki', {})
        if not isinstance(jednostki, dict) or not jednostki:
            return

        for kategoria in ('uszlachetnienia', 'obrobka'):
            for dane in self.slowniki.get(kategoria, {}).values():
                self._dopasuj_i_uzupelnij_jednostke(dane, jednostki)

    def _dopasuj_i_uzupelnij_jednostke(self, rekord: Dict[str, Any], jednostki: Dict[str, Any]) -> None:
        if not isinstance(rekord, dict):
            return

        definicja = None
        kod = rekord.get('kod_jednostki')
        if kod and kod in jednostki:
            definicja = jednostki[kod]
        else:
            definicja = self._dopasuj_jednostke_po_stringu(jednostki, rekord.get('jednostka'))
            if definicja:
                rekord['kod_jednostki'] = definicja['kod']

        if definicja:
            rekord['typ_jednostki'] = definicja.get('typ_jednostki', rekord.get('typ_jednostki'))
            if not rekord.get('jednostka'):
                rekord['jednostka'] = definicja.get('etykieta', rekord.get('jednostka'))

    def _pobierz_definicje_jednostki(self, kod: Optional[str], jednostka: Optional[str]) -> Optional[Dict[str, Any]]:
        jednostki = self.slowniki.get('jednostki', {})
        if not isinstance(jednostki, dict) or not jednostki:
            return None

        if kod:
            kod_norm = kod.strip().upper()
            definicja = jednostki.get(kod_norm)
            if definicja:
                return definicja

        return self._dopasuj_jednostke_po_stringu(jednostki, jednostka)

    @staticmethod
    def _dopasuj_jednostke_po_stringu(jednostki: Dict[str, Any], jednostka_str: Optional[str]) -> Optional[Dict[str, Any]]:
        if not jednostka_str:
            return None

        tekst = jednostka_str.lower()
        for definicja in jednostki.values():
            for slowo in definicja.get('slowa_kluczowe', []):
                if slowo.lower() in tekst:
                    return definicja
        return None

    # ==================== KATEGORIE PAPIERU ====================

    def get_kategorie_papieru(self) -> Dict[str, Any]:
        kategorie = self.slowniki.setdefault('kategorie_papieru', {})
        if not isinstance(kategorie, dict):
            kategorie = {}
            self.slowniki['kategorie_papieru'] = kategorie
        return kategorie

    def dodaj_kategorie_papieru(self, nazwa: str, opis: str = '') -> Dict[str, Any]:
        if not nazwa or not nazwa.strip():
            raise ValueError("Nazwa kategorii jest wymagana")

        nazwa = nazwa.strip()
        opis = opis.strip() if opis else ''

        kategorie = self.get_kategorie_papieru()
        if nazwa in kategorie:
            raise ValueError(f"Kategoria '{nazwa}' już istnieje")

        rekord = {
            'nazwa': nazwa,
            'opis': opis
        }
        kategorie[nazwa] = rekord

        self._zapisz_zmiane('kategorie_papieru', 'dodanie', nazwa)
        self.zapisz_slowniki()

        rekord_zwracany = {
            'id': nazwa,
            'nazwa': nazwa,
            'opis': opis
        }
        return rekord_zwracany

    def edytuj_kategorie_papieru(self, stara_nazwa: str, nowa_nazwa: Optional[str] = None,
                                 opis: Optional[str] = None) -> Dict[str, Any]:
        if not stara_nazwa or not stara_nazwa.strip():
            raise ValueError("Nazwa kategorii do edycji jest wymagana")

        stara_nazwa = stara_nazwa.strip()
        kategorie = self.get_kategorie_papieru()

        if stara_nazwa not in kategorie:
            raise ValueError(f"Kategoria '{stara_nazwa}' nie istnieje")

        rekord = kategorie[stara_nazwa]
        docelowa_nazwa = stara_nazwa
        zmiana_nazwy = False

        if nowa_nazwa is not None:
            nowa_nazwa = nowa_nazwa.strip()
            if not nowa_nazwa:
                raise ValueError("Nowa nazwa kategorii jest wymagana")
            if nowa_nazwa != stara_nazwa and nowa_nazwa in kategorie:
                raise ValueError(f"Kategoria '{nowa_nazwa}' już istnieje")

            if nowa_nazwa != stara_nazwa:
                kategorie[nowa_nazwa] = rekord
                del kategorie[stara_nazwa]

                for dane in self.slowniki.get('papiery', {}).values():
                    if dane.get('kategoria') == stara_nazwa:
                        dane['kategoria'] = nowa_nazwa

                docelowa_nazwa = nowa_nazwa
                zmiana_nazwy = True

        if opis is not None:
            rekord['opis'] = opis.strip()

        if zmiana_nazwy:
            rekord['nazwa'] = docelowa_nazwa
        elif 'nazwa' not in rekord:
            rekord['nazwa'] = docelowa_nazwa

        opis_zmiany = f"{stara_nazwa} -> {docelowa_nazwa}" if zmiana_nazwy else stara_nazwa
        self._zapisz_zmiane('kategorie_papieru', 'edycja', opis_zmiany)
        self.zapisz_slowniki()

        return {
            'id': docelowa_nazwa,
            'nazwa': rekord['nazwa'],
            'opis': rekord.get('opis', '')
        }

    def usun_kategorie_papieru(self, nazwa: str) -> bool:
        if not nazwa or not nazwa.strip():
            raise ValueError("Nazwa kategorii do usunięcia jest wymagana")

        nazwa = nazwa.strip()
        kategorie = self.get_kategorie_papieru()

        if nazwa not in kategorie:
            raise ValueError(f"Kategoria '{nazwa}' nie istnieje")

        powiazane = [p for p in self.slowniki.get('papiery', {}).values() if p.get('kategoria') == nazwa]
        if powiazane:
            raise ValueError("Nie można usunąć kategorii przypisanej do papierów")

        del kategorie[nazwa]

        self._zapisz_zmiane('kategorie_papieru', 'usunięcie', nazwa)
        self.zapisz_slowniki()

        return True

    def _waliduj_kategorie_papieru(self, kategoria: Optional[str]) -> str:
        if not kategoria or not str(kategoria).strip():
            raise ValueError("Kategoria papieru jest wymagana")

        kategoria = str(kategoria).strip()
        kategorie = self.get_kategorie_papieru()
        if kategoria in kategorie:
            return kategoria

        for istniejaca in kategorie.keys():
            if istniejaca.lower() == kategoria.lower():
                return istniejaca

        raise ValueError(f"Kategoria papieru '{kategoria}' nie istnieje")

    # ==================== PAPIERY ====================

    def dodaj_papier(self, nazwa: str, gramatury: List[int], ceny: List[float],
                     kategoria: str = 'niepowlekany') -> Dict:
        """Dodaj nowy rodzaj papieru"""
        if nazwa in self.slowniki['papiery']:
            raise ValueError(f"Papier '{nazwa}' już istnieje")

        kategoria_id = self._waliduj_kategorie_papieru(kategoria)
        
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
            'kategoria': kategoria_id
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
            papier['kategoria'] = self._waliduj_kategorie_papieru(kategoria)
        
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
                              typ_jednostki: str = 'sztukowa',
                              kod_jednostki: Optional[str] = None) -> Dict:
        """Dodaj nowe uszlachetnienie"""
        if nazwa in self.slowniki['uszlachetnienia']:
            raise ValueError(f"Uszlachetnienie '{nazwa}' już istnieje")

        if cena_pln <= 0:
            raise ValueError("Cena musi być dodatnia")

        if typ not in ['UV', 'Dyspersyjny', 'Folia', 'Tłoczenie']:
            raise ValueError(f"Nieprawidłowy typ: {typ}")

        definicja_jednostki = self._pobierz_definicje_jednostki(kod_jednostki, jednostka)
        if definicja_jednostki:
            kod_jednostki = definicja_jednostki['kod']
            jednostka = definicja_jednostki.get('etykieta', jednostka)
            typ_jednostki = definicja_jednostki.get('typ_jednostki', typ_jednostki)
        elif kod_jednostki:
            kod_jednostki = kod_jednostki.strip().upper()

        self.slowniki['uszlachetnienia'][nazwa] = {
            'typ': typ,
            'cena_pln': cena_pln,
            'jednostka': jednostka,
            'typ_jednostki': typ_jednostki,
            'opis': opis
        }

        if kod_jednostki:
            self.slowniki['uszlachetnienia'][nazwa]['kod_jednostki'] = kod_jednostki

        self._zapisz_zmiane('uszlachetnienia', 'dodanie', nazwa)
        self._mapuj_jednostki_na_kody()
        self.zapisz_slowniki()

        return self.slowniki['uszlachetnienia'][nazwa]

    def edytuj_uszlachetnienie(self, stara_nazwa: str, nowa_nazwa: str = None,
                                typ: str = None, cena_pln: float = None,
                                jednostka: str = None, opis: str = None,
                                typ_jednostki: str = None,
                                kod_jednostki: Optional[str] = None) -> Dict:
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
        if kod_jednostki is not None:
            kod_norm = kod_jednostki.strip().upper()
            if kod_norm:
                uszl['kod_jednostki'] = kod_norm
            else:
                uszl.pop('kod_jednostki', None)

        definicja_jednostki = self._pobierz_definicje_jednostki(uszl.get('kod_jednostki'), uszl.get('jednostka'))
        if definicja_jednostki:
            uszl['kod_jednostki'] = definicja_jednostki['kod']
            uszl['jednostka'] = definicja_jednostki.get('etykieta', uszl.get('jednostka'))
            uszl['typ_jednostki'] = definicja_jednostki.get('typ_jednostki', uszl.get('typ_jednostki'))

        self._zapisz_zmiane('uszlachetnienia', 'edycja', stara_nazwa)
        self._mapuj_jednostki_na_kody()
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
                      opis: str = '', typ_jednostki: str = 'sztukowa',
                      kod_jednostki: Optional[str] = None) -> Dict:
        """Dodaj nową operację obróbki"""
        if nazwa in self.slowniki['obrobka']:
            raise ValueError(f"Obróbka '{nazwa}' już istnieje")

        if cena_pln <= 0:
            raise ValueError("Cena musi być dodatnia")

        definicja_jednostki = self._pobierz_definicje_jednostki(kod_jednostki, jednostka)
        if definicja_jednostki:
            kod_jednostki = definicja_jednostki['kod']
            jednostka = definicja_jednostki.get('etykieta', jednostka)
            typ_jednostki = definicja_jednostki.get('typ_jednostki', typ_jednostki)
        elif kod_jednostki:
            kod_jednostki = kod_jednostki.strip().upper()

        self.slowniki['obrobka'][nazwa] = {
            'cena_pln': cena_pln,
            'jednostka': jednostka,
            'typ_jednostki': typ_jednostki,
            'opis': opis
        }

        if kod_jednostki:
            self.slowniki['obrobka'][nazwa]['kod_jednostki'] = kod_jednostki

        self._zapisz_zmiane('obrobka', 'dodanie', nazwa)
        self._mapuj_jednostki_na_kody()
        self.zapisz_slowniki()

        return self.slowniki['obrobka'][nazwa]

    def edytuj_obrobke(self, stara_nazwa: str, nowa_nazwa: str = None,
                       cena_pln: float = None, jednostka: str = None,
                       opis: str = None, typ_jednostki: str = None,
                       kod_jednostki: Optional[str] = None) -> Dict:
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
        if kod_jednostki is not None:
            kod_norm = kod_jednostki.strip().upper()
            if kod_norm:
                obr['kod_jednostki'] = kod_norm
            else:
                obr.pop('kod_jednostki', None)

        definicja_jednostki = self._pobierz_definicje_jednostki(obr.get('kod_jednostki'), obr.get('jednostka'))
        if definicja_jednostki:
            obr['kod_jednostki'] = definicja_jednostki['kod']
            obr['jednostka'] = definicja_jednostki.get('etykieta', obr.get('jednostka'))
            obr['typ_jednostki'] = definicja_jednostki.get('typ_jednostki', obr.get('typ_jednostki'))

        self._zapisz_zmiane('obrobka', 'edycja', stara_nazwa)
        self._mapuj_jednostki_na_kody()
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
                           opis: str = '', spad: float = 2.5) -> Dict:
        """Dodaj nowy rodzaj pracy (np. ulotka, wizytówka)"""
        if 'rodzaje_prac' not in self.slowniki:
            self.slowniki['rodzaje_prac'] = {}
        
        if nazwa in self.slowniki['rodzaje_prac']:
            raise ValueError(f"Rodzaj pracy '{nazwa}' już istnieje")
        
        if szerokosc <= 0 or wysokosc <= 0:
            raise ValueError("Wymiary muszą być dodatnie")

        spad_wartosc = float(spad)
        if spad_wartosc < 0:
            raise ValueError("Spad nie może być ujemny")

        self.slowniki['rodzaje_prac'][nazwa] = {
            'szerokosc': int(szerokosc),
            'wysokosc': int(wysokosc),
            'opis': opis,
            'spad': spad_wartosc
        }
        
        self._zapisz_zmiane('rodzaje_prac', 'dodanie', nazwa)
        self.zapisz_slowniki()
        
        return self.slowniki['rodzaje_prac'][nazwa]
    
    def edytuj_rodzaj_pracy(self, stara_nazwa: str, nowa_nazwa: str = None,
                            szerokosc: int = None, wysokosc: int = None,
                            opis: str = None, spad: float = None) -> Dict:
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

        if spad is not None:
            spad_wartosc = float(spad)
            if spad_wartosc < 0:
                raise ValueError("Spad nie może być ujemny")
            dane['spad'] = spad_wartosc
        
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

    # ==================== KOLORYSTYKI DRUKU ====================

    def get_kolorystyki(self) -> Dict[str, Any]:
        kolorystyki = self.slowniki.get('kolorystyki')
        if not isinstance(kolorystyki, dict):
            kolorystyki = {}
            self.slowniki['kolorystyki'] = kolorystyki
        return kolorystyki

    @staticmethod
    def _sanitize_int(value: Any, pole: str, min_value: int = 0) -> int:
        try:
            wartosc = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{pole} musi być liczbą całkowitą")

        if wartosc < min_value:
            if min_value > 0:
                raise ValueError(f"{pole} musi być większe lub równe {min_value}")
            raise ValueError(f"{pole} nie może być ujemne")

        return wartosc

    @staticmethod
    def _sanitize_float(value: Any, pole: str, min_value: float = 0.0) -> float:
        try:
            wartosc = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{pole} musi być liczbą")

        if wartosc <= min_value:
            raise ValueError(f"{pole} musi być większe niż {min_value}")

        return wartosc

    def _zbuduj_rekord_kolorystyki(self,
                                   kolory_przod: Any,
                                   kolory_tyl: Any,
                                   mnoznik_przelotow: Any,
                                   domyslna_ilosc_form: Any,
                                   etykieta: Optional[str],
                                   opis: Optional[str]) -> Dict[str, Any]:
        kolory_przod_int = self._sanitize_int(kolory_przod, 'Liczba kolorów na awersie', 0)
        kolory_tyl_int = self._sanitize_int(kolory_tyl, 'Liczba kolorów na rewersie', 0)
        domyslna_formy = self._sanitize_int(domyslna_ilosc_form if domyslna_ilosc_form is not None else 1,
                                            'Domyślna liczba form', 1)
        mnoznik = self._sanitize_float(mnoznik_przelotow if mnoznik_przelotow is not None else 1.0,
                                       'Mnożnik przelotów', 0.0)

        rekord = {
            'kolory_przod': kolory_przod_int,
            'kolory_tyl': kolory_tyl_int,
            'mnoznik_przelotow': mnoznik,
            'domyslna_ilosc_form': domyslna_formy,
            'opis': (opis or '').strip()
        }

        etykieta_wynik = (etykieta or '').strip()
        if etykieta_wynik:
            rekord['etykieta'] = etykieta_wynik
        else:
            rekord['etykieta'] = ''

        return rekord

    def dodaj_kolorystyke(self,
                           nazwa: str,
                           kolory_przod: Any,
                           kolory_tyl: Any,
                           mnoznik_przelotow: Any,
                           domyslna_ilosc_form: Any,
                           etykieta: Optional[str] = None,
                           opis: str = '') -> Dict[str, Any]:
        nazwa_norm = (nazwa or '').strip()
        if not nazwa_norm:
            raise ValueError('Nazwa kolorystyki jest wymagana')

        kolorystyki = self.get_kolorystyki()
        if nazwa_norm in kolorystyki:
            raise ValueError(f"Kolorystyka '{nazwa_norm}' już istnieje")

        rekord = self._zbuduj_rekord_kolorystyki(kolory_przod, kolory_tyl,
                                                  mnoznik_przelotow, domyslna_ilosc_form,
                                                  etykieta if etykieta is not None else nazwa_norm,
                                                  opis)

        kolorystyki[nazwa_norm] = rekord
        self._zapisz_zmiane('kolorystyki', 'dodanie', nazwa_norm)
        self.zapisz_slowniki()

        return rekord

    def edytuj_kolorystyke(self,
                            stara_nazwa: str,
                            nowa_nazwa: Optional[str] = None,
                            kolory_przod: Any = None,
                            kolory_tyl: Any = None,
                            mnoznik_przelotow: Any = None,
                            domyslna_ilosc_form: Any = None,
                            etykieta: Optional[str] = None,
                            opis: Optional[str] = None) -> Dict[str, Any]:
        kolorystyki = self.get_kolorystyki()
        if stara_nazwa not in kolorystyki:
            raise ValueError(f"Kolorystyka '{stara_nazwa}' nie istnieje")

        rekord = kolorystyki[stara_nazwa]

        if nowa_nazwa and nowa_nazwa != stara_nazwa:
            nowa_nazwa_norm = nowa_nazwa.strip()
            if not nowa_nazwa_norm:
                raise ValueError('Nowa nazwa kolorystyki nie może być pusta')
            if nowa_nazwa_norm in kolorystyki:
                raise ValueError(f"Kolorystyka '{nowa_nazwa_norm}' już istnieje")
            kolorystyki[nowa_nazwa_norm] = rekord
            del kolorystyki[stara_nazwa]
            stara_nazwa = nowa_nazwa_norm

        if kolory_przod is not None:
            rekord['kolory_przod'] = self._sanitize_int(kolory_przod, 'Liczba kolorów na awersie', 0)
        if kolory_tyl is not None:
            rekord['kolory_tyl'] = self._sanitize_int(kolory_tyl, 'Liczba kolorów na rewersie', 0)
        if mnoznik_przelotow is not None:
            rekord['mnoznik_przelotow'] = self._sanitize_float(mnoznik_przelotow, 'Mnożnik przelotów', 0.0)
        if domyslna_ilosc_form is not None:
            rekord['domyslna_ilosc_form'] = self._sanitize_int(domyslna_ilosc_form, 'Domyślna liczba form', 1)
        if etykieta is not None:
            rekord['etykieta'] = etykieta.strip() if etykieta else ''
        if opis is not None:
            rekord['opis'] = opis.strip()

        self._zapisz_zmiane('kolorystyki', 'edycja', stara_nazwa)
        self.zapisz_slowniki()

        return rekord

    def usun_kolorystyke(self, nazwa: str) -> bool:
        kolorystyki = self.get_kolorystyki()
        if nazwa not in kolorystyki:
            raise ValueError(f"Kolorystyka '{nazwa}' nie istnieje")

        del kolorystyki[nazwa]
        self._zapisz_zmiane('kolorystyki', 'usunięcie', nazwa)
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
