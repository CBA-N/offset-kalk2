"""
Manager kontrahentów - zarządzanie bazą klientów z zapisem do JSON
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class KontrahenciManager:
    """Zarządza kontrahentami z zapisem do pliku JSON"""
    
    def __init__(self, plik_json='kontrahenci.json'):
        """
        Args:
            plik_json: Ścieżka do pliku JSON z kontrahentami
        """
        self.plik_json = plik_json
        self.kontrahenci = self._zaladuj_kontrahentow()
        
    def _zaladuj_kontrahentow(self) -> List[Dict]:
        """Załaduj kontrahentów z pliku lub utwórz pustą listę"""
        if os.path.exists(self.plik_json):
            try:
                with open(self.plik_json, 'r', encoding='utf-8') as f:
                    kontrahenci = json.load(f)
                    print(f"✅ Załadowano {len(kontrahenci)} kontrahentów")
                    return kontrahenci
            except Exception as e:
                print(f"⚠️  Błąd wczytywania kontrahentów: {e}")
                return []
        return []
    
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
        dane['data_dodania'] = teraz
        dane['ostatnia_modyfikacja'] = teraz
        
        # Dodaj ID
        if self.kontrahenci:
            max_id = max(k.get('id', 0) for k in self.kontrahenci)
            dane['id'] = max_id + 1
        else:
            dane['id'] = 1
        
        # Dodaj na początek listy
        self.kontrahenci.insert(0, dane)
        
        # Zapisz do pliku
        self.zapisz_kontrahentow()
        
        return dane
    
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
                dane['id'] = kontrahent_id
                dane['data_dodania'] = kontrahent.get('data_dodania')
                dane['ostatnia_modyfikacja'] = datetime.now().isoformat()
                
                # Zastąp kontrahenta
                self.kontrahenci[i] = dane
                self.zapisz_kontrahentow()
                
                return dane
        
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
        return next((k for k in self.kontrahenci if k.get('id') == kontrahent_id), None)
    
    def pobierz_wszystkich(self) -> List[Dict]:
        """Pobierz wszystkich kontrahentów"""
        return self.kontrahenci
    
    def szukaj(self, fraza: str) -> List[Dict]:
        """
        Wyszukaj kontrahentów (nazwa, NIP, miasto, email)
        
        Args:
            fraza: Fraza do wyszukania
            
        Returns:
            Lista pasujących kontrahentów
        """
        if not fraza:
            return self.kontrahenci
        
        fraza_lower = fraza.lower()
        wyniki = []
        
        for kontrahent in self.kontrahenci:
            # Przeszukaj różne pola
            pola_do_przeszukania = [
                kontrahent.get('nazwa', ''),
                kontrahent.get('nip', ''),
                kontrahent.get('adres_miasto', ''),
                kontrahent.get('email', ''),
                kontrahent.get('telefon', '')
            ]
            
            # Sprawdź czy któreś pole zawiera frazę
            for pole in pola_do_przeszukania:
                if fraza_lower in str(pole).lower():
                    wyniki.append(kontrahent)
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
        miasta = list(set(k.get('adres_miasto', 'Nieznane') for k in self.kontrahenci))
        
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
            'adres_ulica': "[USUNIĘTE]",
            'adres_kod': "XX-XXX",
            'adres_miasto': "[USUNIĘTE]",
            'adres_wojewodztwo': "",
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
