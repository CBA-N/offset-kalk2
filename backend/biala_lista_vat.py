"""
Klient API Białej Listy VAT - Ministerstwo Finansów
https://wl-api.mf.gov.pl/
"""

import requests
from datetime import datetime
from typing import Dict, Optional


class BialaListaVATClient:
    """Klient API Białej Listy VAT (Ministerstwo Finansów)"""
    
    BASE_URL = "https://wl-api.mf.gov.pl/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Kalkulator-Offsetowy/1.2',
            'Accept': 'application/json'
        })
    
    @staticmethod
    def waliduj_nip(nip: str) -> bool:
        """
        Waliduj NIP przy użyciu algorytmu sumy kontrolnej
        
        Args:
            nip: NIP do walidacji (10 cyfr)
            
        Returns:
            True jeśli NIP jest poprawny
        """
        # Usuń znaki niebędące cyframi
        nip = ''.join(c for c in nip if c.isdigit())
        
        if len(nip) != 10:
            return False
        
        # Wagi dla kolejnych cyfr NIP
        wagi = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        
        try:
            # Oblicz sumę kontrolną
            suma = sum(int(nip[i]) * wagi[i] for i in range(9))
            cyfra_kontrolna = suma % 11
            
            # Jeśli suma kontrolna to 10, NIP jest niepoprawny
            if cyfra_kontrolna == 10:
                return False
            
            # Porównaj z ostatnią cyfrą NIP
            return cyfra_kontrolna == int(nip[9])
        except (ValueError, IndexError):
            return False
    
    @staticmethod
    def formatuj_nip(nip: str) -> str:
        """
        Formatuj NIP do standardowego formatu XXX-XXX-XX-XX
        
        Args:
            nip: NIP (10 cyfr)
            
        Returns:
            Sformatowany NIP
        """
        nip = ''.join(c for c in nip if c.isdigit())
        
        if len(nip) != 10:
            return nip
        
        return f"{nip[:3]}-{nip[3:6]}-{nip[6:8]}-{nip[8:10]}"
    
    def pobierz_dane_z_nip(self, nip: str, data: Optional[str] = None) -> Dict:
        """
        Pobierz dane podmiotu z Białej Listy VAT po NIP
        
        Args:
            nip: NIP (10 cyfr, z lub bez kresek)
            data: Data sprawdzenia w formacie YYYY-MM-DD (domyślnie dzisiaj)
            
        Returns:
            Słownik z danymi podmiotu lub błędem
        """
        # Wyczyść NIP
        nip_czysty = ''.join(c for c in nip if c.isdigit())
        
        # Walidacja NIP
        if not self.waliduj_nip(nip_czysty):
            return {
                'success': False,
                'error': 'Nieprawidłowy NIP (błąd sumy kontrolnej)'
            }
        
        # Data sprawdzenia (domyślnie dzisiaj)
        if not data:
            data = datetime.now().strftime('%Y-%m-%d')
        
        # Endpoint API
        url = f"{self.BASE_URL}/search/nip/{nip_czysty}"
        params = {'date': data}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            # Sprawdź kod odpowiedzi
            if response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Nie znaleziono podmiotu w Białej Liście VAT',
                    'info': 'Podmiot może nie być zarejestrowany jako podatnik VAT'
                }
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Błąd API: {response.status_code}'
                }
            
            # Parsuj odpowiedź JSON
            data_json = response.json()
            
            # Sprawdź czy znaleziono podmiot
            if 'result' not in data_json or 'subject' not in data_json['result']:
                return {
                    'success': False,
                    'error': 'Nie znaleziono podmiotu',
                    'raw_response': data_json
                }
            
            subject = data_json['result']['subject']
            
            # Ekstraktuj i przetworz dane
            dane = self._przetworz_dane_podmiotu(subject)
            
            # Detekcja formy prawnej
            forma_prawna = self._wykryj_forme_prawna(dane['nazwa'])
            dane['forma_prawna'] = forma_prawna
            
            # Zwraca strukturę zgodną z frontend
            return {
                'success': True,
                'dane': dane,
                'zrodlo': 'Biała Lista VAT (Ministerstwo Finansów)',
                'data_sprawdzenia': data
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Przekroczono limit czasu połączenia z API'
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Błąd połączenia: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Nieoczekiwany błąd: {str(e)}'
            }
    
    def _przetworz_dane_podmiotu(self, subject: Dict) -> Dict:
        """
        Przetworz dane podmiotu z API na ustandaryzowany format
        
        Args:
            subject: Dane podmiotu z API
            
        Returns:
            Przetworzone dane
        """
        # Parsuj adres (format: "ul. Przykładowa 10, 00-001 Warszawa")
        # Dla firm: workingAddress, dla osób fizycznych: residenceAddress
        adres_siedziby = subject.get('workingAddress') or subject.get('residenceAddress', '')
        ulica, kod_miasto = self._parsuj_adres(adres_siedziby)
        
        # Kod pocztowy i miasto
        kod_pocztowy = ''
        miasto = ''
        wojewodztwo = ''
        
        if kod_miasto:
            # Format: "00-001 Warszawa"
            parts = kod_miasto.split(' ', 1)
            if len(parts) == 2:
                kod_pocztowy = parts[0]
                miasto = parts[1]
            else:
                miasto = kod_miasto
        
        # Określ województwo na podstawie kodu pocztowego (uproszczone)
        if kod_pocztowy:
            wojewodztwo = self._okresl_wojewodztwo(kod_pocztowy)
        
        return {
            'nazwa': subject.get('name', ''),
            'nip': self.formatuj_nip(subject.get('nip', '')),
            'regon': subject.get('regon', ''),
            'krs': subject.get('krs', ''),
            'status_vat': subject.get('statusVat', ''),
            'adres': {
                'ulica': ulica,
                'kod_pocztowy': kod_pocztowy,
                'miasto': miasto,
                'wojewodztwo': wojewodztwo
            },
            'adres_pelny': adres_siedziby,
            'data_rejestracji_vat': subject.get('registrationLegalDate', ''),
            'data_wykreslenia_vat': subject.get('removalDate', ''),
            'konta_bankowe': subject.get('accountNumbers', []),
            'reprezentanci': subject.get('representatives', []),
            'prokurenci': subject.get('authorizedClerks', []),
            'wspolnicy': subject.get('partners', [])
        }
    
    @staticmethod
    def _parsuj_adres(adres: str) -> tuple:
        """
        Parsuj adres na ulicę i kod pocztowy + miasto
        
        Args:
            adres: Adres w formacie "ul. Przykładowa 10, 00-001 Warszawa"
            
        Returns:
            Tuple (ulica, kod_miasto)
        """
        if not adres or ',' not in adres:
            return (adres, '')
        
        parts = adres.split(',', 1)
        ulica = parts[0].strip()
        kod_miasto = parts[1].strip()
        
        return (ulica, kod_miasto)
    
    @staticmethod
    def _okresl_wojewodztwo(kod_pocztowy: str) -> str:
        """
        Określ województwo na podstawie kodu pocztowego (uproszczone)
        
        Args:
            kod_pocztowy: Kod pocztowy XX-XXX
            
        Returns:
            Nazwa województwa
        """
        # Mapowanie przedziałów kodów pocztowych na województwa
        # To jest uproszczona wersja - w rzeczywistości granice są bardziej złożone
        kod = kod_pocztowy.replace('-', '')
        
        if not kod or len(kod) < 2:
            return ''
        
        prefix = kod[:2]
        
        mapa_wojewodztw = {
            '00': 'mazowieckie', '01': 'mazowieckie', '02': 'mazowieckie',
            '03': 'mazowieckie', '04': 'mazowieckie', '05': 'mazowieckie',
            '06': 'mazowieckie', '07': 'mazowieckie', '08': 'mazowieckie',
            '09': 'mazowieckie',
            '10': 'warmińsko-mazurskie', '11': 'warmińsko-mazurskie',
            '12': 'podlaskie', '13': 'podlaskie', '14': 'podlaskie',
            '15': 'podlaskie', '16': 'podlaskie', '17': 'podlaskie',
            '18': 'podlaskie', '19': 'podlaskie',
            '20': 'lubelskie', '21': 'lubelskie', '22': 'lubelskie',
            '23': 'lubelskie', '24': 'lubelskie',
            '25': 'świętokrzyskie', '26': 'świętokrzyskie',
            '27': 'świętokrzyskie', '28': 'świętokrzyskie',
            '30': 'małopolskie', '31': 'małopolskie', '32': 'małopolskie',
            '33': 'małopolskie', '34': 'małopolskie',
            '35': 'podkarpackie', '36': 'podkarpackie', '37': 'podkarpackie',
            '38': 'podkarpackie', '39': 'podkarpackie',
            '40': 'śląskie', '41': 'śląskie', '42': 'śląskie',
            '43': 'śląskie', '44': 'śląskie',
            '45': 'opolskie', '46': 'opolskie', '47': 'opolskie',
            '48': 'opolskie', '49': 'opolskie',
            '50': 'dolnośląskie', '51': 'dolnośląskie', '52': 'dolnośląskie',
            '53': 'dolnośląskie', '54': 'dolnośląskie', '55': 'dolnośląskie',
            '56': 'dolnośląskie', '57': 'dolnośląskie', '58': 'dolnośląskie',
            '59': 'dolnośląskie',
            '60': 'wielkopolskie', '61': 'wielkopolskie', '62': 'wielkopolskie',
            '63': 'wielkopolskie', '64': 'wielkopolskie',
            '65': 'lubuskie', '66': 'lubuskie', '67': 'lubuskie',
            '68': 'lubuskie', '69': 'lubuskie',
            '70': 'zachodniopomorskie', '71': 'zachodniopomorskie',
            '72': 'zachodniopomorskie', '73': 'zachodniopomorskie',
            '74': 'zachodniopomorskie', '75': 'zachodniopomorskie',
            '76': 'zachodniopomorskie', '77': 'zachodniopomorskie',
            '78': 'zachodniopomorskie',
            '80': 'pomorskie', '81': 'pomorskie', '82': 'pomorskie',
            '83': 'pomorskie', '84': 'pomorskie'
        }
        
        return mapa_wojewodztw.get(prefix, '')
    
    @staticmethod
    def _wykryj_forme_prawna(nazwa: str) -> str:
        """
        Wykryj formę prawną na podstawie nazwy
        
        Args:
            nazwa: Nazwa firmy
            
        Returns:
            Forma prawna
        """
        nazwa_lower = nazwa.lower()
        
        if 'sp. z o.o.' in nazwa_lower or 'spółka z ograniczoną' in nazwa_lower:
            return 'Sp. z o.o.'
        elif 's.a.' in nazwa_lower or 'spółka akcyjna' in nazwa_lower:
            return 'S.A.'
        elif 'sp. j.' in nazwa_lower or 'spółka jawna' in nazwa_lower:
            return 'Spółka jawna'
        elif 'sp. k.' in nazwa_lower or 'spółka komandytowa' in nazwa_lower:
            return 'Spółka komandytowa'
        elif 'sp. p.' in nazwa_lower or 'spółka partnerska' in nazwa_lower:
            return 'Spółka partnerska'
        elif 'sp. cywilna' in nazwa_lower or 'spółka cywilna' in nazwa_lower:
            return 'Spółka cywilna'
        elif 'fundacja' in nazwa_lower:
            return 'Fundacja'
        elif 'stowarzyszenie' in nazwa_lower:
            return 'Stowarzyszenie'
        else:
            return 'JDG'  # Domyślnie Jednoosobowa Działalność Gospodarcza
