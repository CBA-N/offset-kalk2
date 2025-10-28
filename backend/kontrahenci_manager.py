"""
Manager kontrahentów - zarządzanie bazą klientów z zapisem do JSON
"""

import json
import os
from copy import deepcopy
from datetime import datetime
from typing import List, Dict, Optional, Any


class KontrahenciManager:
    """Zarządza kontrahentami z zapisem do pliku JSON"""
    
    def __init__(self, plik_json='kontrahenci.json'):
        """
        Args:
            plik_json: Ścieżka do pliku JSON z kontrahentami
        """
        if os.path.isabs(plik_json):
            self.plik_json = plik_json
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.plik_json = os.path.abspath(os.path.join(base_dir, plik_json))

        os.makedirs(os.path.dirname(self.plik_json), exist_ok=True)
        self.kontrahenci = self._zaladuj_kontrahentow()
        
    def _zaladuj_kontrahentow(self) -> List[Dict]:
        """Załaduj kontrahentów z pliku lub utwórz pustą listę"""
        if not os.path.exists(self.plik_json):
            return []

        try:
            with open(self.plik_json, 'r', encoding='utf-8') as f:
                dane = json.load(f)
        except Exception as e:
            print(f"⚠️  Błąd wczytywania kontrahentów: {e}")
            return []

        if not isinstance(dane, list):
            print("⚠️  Niepoprawny format danych kontrahentów – oczekiwano listy")
            return []

        wynik = []
        for wpis in dane:
            norm = self._normalizuj_kontrahenta(wpis) if isinstance(wpis, dict) else None
            if norm is not None:
                wynik.append(norm)

        print(f"✅ Załadowano {len(wynik)} kontrahentów")
        return wynik
    
    def zapisz_kontrahentow(self) -> bool:
        """Zapisz kontrahentów do pliku JSON"""
        try:
            with open(self.plik_json, 'w', encoding='utf-8') as f:
                json.dump(self.kontrahenci, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Błąd zapisu kontrahentów: {e}")
            return False

    def dodaj_kontrahenta(self, dane: Dict) -> Dict:
        """
        Dodaj nowego kontrahenta
        
        Args:
            dane: Słownik z danymi kontrahenta
            
        Returns:
            Kontrahent z dodanym ID i timestampem
        """
        # Dodaj timestamp
        teraz = datetime.now().isoformat()
        dane_normalized = self._normalizuj_kontrahenta(dane)
        dane_normalized['data_dodania'] = teraz
        dane_normalized['ostatnia_modyfikacja'] = teraz

        # Dodaj ID
        if self.kontrahenci:
            max_id = max(k.get('id', 0) for k in self.kontrahenci)
            dane_normalized['id'] = max_id + 1
        else:
            dane_normalized['id'] = 1

        # Dodaj na początek listy
        self.kontrahenci.insert(0, dane_normalized)

        # Zapisz do pliku
        self.zapisz_kontrahentow()

        return deepcopy(dane_normalized)
    
    def edytuj_kontrahenta(self, kontrahent_id: int, dane: Dict) -> Optional[Dict]:
        """
        Edytuj istniejącego kontrahenta
        
        Args:
            kontrahent_id: ID kontrahenta do edycji
            dane: Nowe dane kontrahenta
            
        Returns:
            Zaktualizowany kontrahent lub None jeśli nie znaleziono
        """
        for i, kontrahent in enumerate(self.kontrahenci):
            if kontrahent.get('id') == kontrahent_id:
                # Zachowaj ID i datę dodania
                dane_normalized = self._normalizuj_kontrahenta(
                    dane,
                    domyslny={
                        'id': kontrahent_id,
                        'data_dodania': kontrahent.get('data_dodania')
                    }
                )
                dane_normalized['id'] = kontrahent_id
                dane_normalized['data_dodania'] = kontrahent.get('data_dodania')
                dane_normalized['ostatnia_modyfikacja'] = datetime.now().isoformat()

                # Zastąp kontrahenta
                self.kontrahenci[i] = dane_normalized
                self.zapisz_kontrahentow()

                return deepcopy(dane_normalized)

        return None
    
    def usun_kontrahenta(self, kontrahent_id: int) -> bool:
        """
        Usuń kontrahenta
        
        Args:
            kontrahent_id: ID kontrahenta do usunięcia
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        dlugosc_przed = len(self.kontrahenci)
        self.kontrahenci = [k for k in self.kontrahenci if k.get('id') != kontrahent_id]
        
        if len(self.kontrahenci) < dlugosc_przed:
            self.zapisz_kontrahentow()
            return True
        return False
    
    def pobierz_kontrahenta(self, kontrahent_id: int) -> Optional[Dict]:
        """Pobierz kontrahenta po ID"""
        kontrahent = next((k for k in self.kontrahenci if k.get('id') == kontrahent_id), None)
        return deepcopy(kontrahent) if kontrahent else None

    def pobierz_wszystkich(self) -> List[Dict]:
        """Pobierz wszystkich kontrahentów"""
        return [deepcopy(k) for k in self.kontrahenci]
    
    def szukaj(self, fraza: str) -> List[Dict]:
        """
        Wyszukaj kontrahentów (nazwa, NIP, miasto, email)
        
        Args:
            fraza: Fraza do wyszukania
            
        Returns:
            Lista pasujących kontrahentów
        """
        if not fraza:
            return [deepcopy(k) for k in self.kontrahenci]
        
        fraza_lower = fraza.lower()
        wyniki = []

        for kontrahent in self.kontrahenci:
            adres = kontrahent.get('adres') or {}
            pola_do_przeszukania = [
                kontrahent.get('nazwa', ''),
                kontrahent.get('nip', ''),
                kontrahent.get('email', ''),
                kontrahent.get('telefon', ''),
                kontrahent.get('osoba_kontaktowa', ''),
                adres.get('miasto', ''),
                adres.get('ulica', ''),
                adres.get('kod_pocztowy', ''),
                adres.get('wojewodztwo', ''),
            ]

            for pole in pola_do_przeszukania:
                if fraza_lower in str(pole).lower():
                    wyniki.append(deepcopy(kontrahent))
                    break

        return wyniki
    
    def pobierz_statystyki(self) -> Dict:
        """Pobierz statystyki kontrahentów"""
        if not self.kontrahenci:
            return {
                'liczba_kontrahentow': 0,
                'z_nip': 0,
                'bez_nip': 0,
                'miasta': []
            }
        
        z_nip = sum(1 for k in self.kontrahenci if k.get('nip'))
        miasta = set()
        for k in self.kontrahenci:
            adres = k.get('adres') or {}
            miasto = adres.get('miasto') or k.get('adres_miasto') or 'Nieznane'
            miasta.add(miasto)

        return {
            'liczba_kontrahentow': len(self.kontrahenci),
            'z_nip': z_nip,
            'bez_nip': len(self.kontrahenci) - z_nip,
            'miasta': sorted(miasta)
        }
    
    def anonimizuj_kontrahenta(self, kontrahent_id: int) -> bool:
        """
        Anonimizuj dane kontrahenta (RODO - prawo do usunięcia)
        
        Args:
            kontrahent_id: ID kontrahenta do anonimizacji
            
        Returns:
            True jeśli anonimizowano, False jeśli nie znaleziono
        """
        kontrahent = self.pobierz_kontrahenta(kontrahent_id)
        
        if not kontrahent:
            return False
        
        # Anonimizuj dane osobowe
        dane_anonim = {
            'id': kontrahent_id,
            'nazwa': f"[USUNIĘTY #{kontrahent_id}]",
            'nip': "XXXXXXXXXX",
            'regon': "XXXXXXXXX",
            'adres': {
                'ulica': "[USUNIĘTE]",
                'kod_pocztowy': "XX-XXX",
                'miasto': "[USUNIĘTE]",
                'wojewodztwo': ""
            },
            'email': "usuniete@example.com",
            'telefon': "XXX XXX XXX",
            'osoba_kontaktowa': "[USUNIĘTE]",
            'uwagi': "[Dane usunięte zgodnie z RODO]",
            'forma_prawna': "",
            'pkd_glowny': "",
            'data_rejestracji': "",
            'status': "anonimizowany",
            'data_dodania': kontrahent.get('data_dodania', ''),
            'ostatnia_modyfikacja': datetime.now().isoformat()
        }

        # Edytuj kontrahenta
        return self.edytuj_kontrahenta(kontrahent_id, dane_anonim) is not None

    def _normalizuj_kontrahenta(
        self,
        dane: Dict[str, Any],
        domyslny: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ujednolicenie struktury danych kontrahenta."""

        wynik: Dict[str, Any] = {}
        if domyslny:
            wynik.update(domyslny)

        wynik.update(deepcopy(dane))

        # Zapewnij strukturę adresu
        adres = wynik.get('adres')
        if not isinstance(adres, dict):
            adres = {}

        adres = {
            'ulica': adres.get('ulica') or wynik.pop('adres_ulica', ''),
            'kod_pocztowy': adres.get('kod_pocztowy') or wynik.pop('adres_kod', ''),
            'miasto': adres.get('miasto') or wynik.pop('adres_miasto', ''),
            'wojewodztwo': adres.get('wojewodztwo') or wynik.pop('adres_wojewodztwo', ''),
        }
        wynik['adres'] = adres

        # Usuń stare płaskie klucze jeśli pozostały
        for klucz in ('adres_ulica', 'adres_kod', 'adres_miasto', 'adres_wojewodztwo'):
            wynik.pop(klucz, None)

        # Zadbaj o typ ID
        if 'id' in wynik and wynik['id'] is not None:
            try:
                wynik['id'] = int(wynik['id'])
            except (TypeError, ValueError):
                wynik['id'] = None

        return wynik
