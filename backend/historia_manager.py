"""
Manager historii ofert - trwałe przechowywanie w pliku JSON
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class HistoriaManager:
    """Zarządza historią ofert z zapisem do pliku JSON"""
    
    def __init__(self, plik_json='historia_ofert.json', limit=50):
        """
        Args:
            plik_json: Ścieżka do pliku JSON z historią
            limit: Maksymalna liczba ofert do przechowywania
        """
        self.plik_json = plik_json
        self.limit = limit
        self.historia = self._zaladuj_historie()
        
    def _zaladuj_historie(self) -> List[Dict]:
        """Załaduj historię z pliku lub utwórz pustą listę"""
        if os.path.exists(self.plik_json):
            try:
                with open(self.plik_json, 'r', encoding='utf-8') as f:
                    historia = json.load(f)
                    print(f"✅ Załadowano {len(historia)} ofert z historii")
                    return historia
            except Exception as e:
                print(f"⚠️  Błąd wczytywania historii: {e}")
                return []
        return []
    
    def zapisz_historie(self) -> bool:
        """Zapisz historię do pliku JSON"""
        try:
            with open(self.plik_json, 'w', encoding='utf-8') as f:
                json.dump(self.historia, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Błąd zapisu historii: {e}")
            return False
    
    def dodaj_oferte(self, oferta: Dict) -> Dict:
        """
        Dodaj nową ofertę do historii
        
        Args:
            oferta: Słownik z danymi oferty
            
        Returns:
            Oferta z dodanym ID i timestampem
        """
        # Dodaj timestamp jeśli nie ma
        if 'timestamp' not in oferta:
            oferta['timestamp'] = datetime.now().isoformat()
        
        # Dodaj ID
        if self.historia:
            max_id = max(o.get('id', 0) for o in self.historia)
            oferta['id'] = max_id + 1
        else:
            oferta['id'] = 1
        
        # Dodaj na początek listy
        self.historia.insert(0, oferta)
        
        # Ogranicz do limitu
        if len(self.historia) > self.limit:
            self.historia = self.historia[:self.limit]
        
        # Zapisz do pliku
        self.zapisz_historie()
        
        return oferta
    
    def pobierz_wszystkie(self) -> List[Dict]:
        """Pobierz wszystkie oferty z historii"""
        return self.historia
    
    def pobierz_oferte(self, oferta_id: int) -> Optional[Dict]:
        """Pobierz konkretną ofertę po ID"""
        return next((o for o in self.historia if o.get('id') == oferta_id), None)
    
    def usun_oferte(self, oferta_id: int) -> bool:
        """
        Usuń ofertę z historii
        
        Args:
            oferta_id: ID oferty do usunięcia
            
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        dlugosc_przed = len(self.historia)
        self.historia = [o for o in self.historia if o.get('id') != oferta_id]
        
        if len(self.historia) < dlugosc_przed:
            self.zapisz_historie()
            return True
        return False
    
    def wyczysc_historie(self) -> bool:
        """Usuń wszystkie oferty z historii"""
        self.historia = []
        return self.zapisz_historie()
    
    def pobierz_statystyki(self) -> Dict:
        """Pobierz statystyki historii"""
        if not self.historia:
            return {
                'liczba_ofert': 0,
                'suma_wartosci': 0,
                'srednia_wartosc': 0,
                'najstarsza': None,
                'najnowsza': None
            }
        
        wartosci = [o.get('cena_z_marza_netto', 0) for o in self.historia]
        timestampy = [o.get('timestamp', '') for o in self.historia if o.get('timestamp')]
        
        return {
            'liczba_ofert': len(self.historia),
            'suma_wartosci': sum(wartosci),
            'srednia_wartosc': sum(wartosci) / len(wartosci) if wartosci else 0,
            'najstarsza': min(timestampy) if timestampy else None,
            'najnowsza': max(timestampy) if timestampy else None
        }
    
    def eksportuj_do_csv(self, sciezka: str) -> bool:
        """Eksportuj historię do pliku CSV"""
        try:
            import csv
            
            if not self.historia:
                return False
            
            with open(sciezka, 'w', newline='', encoding='utf-8') as f:
                # Pobierz wszystkie klucze z pierwszej oferty
                klucze = list(self.historia[0].keys())
                writer = csv.DictWriter(f, fieldnames=klucze)
                
                writer.writeheader()
                for oferta in self.historia:
                    # Flatten nested structures jeśli są
                    row = {}
                    for k, v in oferta.items():
                        if isinstance(v, (list, dict)):
                            row[k] = json.dumps(v, ensure_ascii=False)
                        else:
                            row[k] = v
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"❌ Błąd eksportu CSV: {e}")
            return False
