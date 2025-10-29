"""
Adapter słowników - konwertuje nową strukturę danych (z cena_pln)
na starą strukturę wymaganą przez KalkulatorDruku
"""

import re


def adapter_nowy_do_starego(slowniki_nowe: dict) -> dict:
    """
    Konwertuje nową strukturę słowników (z cena_pln) na starą (wymaganą przez kalkulator)
    
    Args:
        slowniki_nowe: Słowniki z nową strukturą (z SlownikiManager)
        
    Returns:
        Słowniki w starej strukturze (dla KalkulatorDruku)
    """
    # PAPIERY: Zachowaj klucze cen jako stringi (kalkulator używa str(gramatura))
    papiery_stare = {}
    for nazwa, dane in slowniki_nowe.get('papiery', {}).items():
        papiery_stare[nazwa] = {
            'gramatury': dane['gramatury'],
            'ceny': {str(k): v for k, v in dane['ceny'].items()},  # Zachowaj jako String!
            'kategoria': dane.get('kategoria', '')
        }
    
    slowniki_stare = {
        'papiery': papiery_stare,
        'formaty': slowniki_nowe.get('formaty', {}),
        'stawki': slowniki_nowe.get('stawki', {}),
        'marza': slowniki_nowe.get('marza', {}),
        'priorytety': slowniki_nowe.get('priorytety', {}),
        'jednostki': slowniki_nowe.get('jednostki', {}),
    }
    
    # USZLACHETNIENIA: zachowaj ceny jednostkowe oraz stare pola pomocnicze
    uszlachetnienia_stare = {}
    for nazwa, dane in slowniki_nowe.get('uszlachetnienia', {}).items():
        if 'cena_pln' in dane:
            # cena_pln jest za 1000 ark, więc dla 1 arkusza:
            cena_arkusz = dane['cena_pln'] / 1000

            # Oblicz cena_za_m2 (zakładając arkusz B2 = 0.35 m²)
            cena_za_m2 = cena_arkusz / 0.35

            # Arkusze: B2 (500x700mm = 0.35m²), A2 (420x594mm = 0.25m²)
            czas_przygotowania = dane.get('czas_przygotowania_min')
            if czas_przygotowania is None:
                match = re.search(r'Czas:\s*(\d+)\s*min', dane.get('opis', ''))
                czas_przygotowania = int(match.group(1)) if match else 45

            rekord_uszl = {
                'cena_za_m2': cena_za_m2,
                'cena_za_arkusz_B2': cena_arkusz,
                'cena_za_arkusz_A2': cena_arkusz * (0.25 / 0.35),  # proporcja powierzchni
                'czas_przygotowania_min': czas_przygotowania,
                'typ': dane.get('typ', 'lakier'),
                # Pola wymagane przez nowy kalkulator
                'cena_pln': dane['cena_pln'],
                'jednostka': dane.get('jednostka', '1000 ark'),
                'typ_jednostki': dane.get('typ_jednostki', 'sztukowa'),
                'kod_jednostki': dane.get('kod_jednostki'),
                'opis': dane.get('opis', '')
            }

            # Zachowaj dodatkowe dane jeżeli istnieją (np. koszt matrycy)
            for dodatkowe in ['koszt_matrycy']:
                if dodatkowe in dane:
                    rekord_uszl[dodatkowe] = dane[dodatkowe]

            uszlachetnienia_stare[nazwa] = rekord_uszl
    slowniki_stare['uszlachetnienia'] = uszlachetnienia_stare
    
    # OBRÓBKA: cena_pln → stawka_godzinowa, wydajnosc_arkuszy_h
    obrobka_stara = {}
    for nazwa, dane in slowniki_nowe.get('obrobka', {}).items():
        if 'cena_pln' in dane:
            # cena_pln jest za jednostkę (np. 1000 arkuszy)
            # Zachowujemy dane jednostki, aby kalkulator mógł skalować koszt
            jednostka = dane.get('jednostka', '1000 ark')
            typ_jednostki = dane.get('typ_jednostki', 'sztukowa')
            kod_jednostki = dane.get('kod_jednostki')

            # Zachowaj także pola wykorzystywane przez starsze wersje kalkulatora
            jednostka_match = re.search(r'([\d.,]+)', jednostka)
            try:
                jednostka_wartosc = float(jednostka_match.group(1).replace(',', '.')) if jednostka_match else 1000.0
            except ValueError:
                jednostka_wartosc = 1000.0
            if jednostka_wartosc == 0:
                jednostka_wartosc = 1.0

            cena_za_ark = dane['cena_pln'] / jednostka_wartosc if jednostka_wartosc else dane['cena_pln']
            stawka_godzinowa = 80.0  # standard
            wydajnosc = stawka_godzinowa / cena_za_ark if cena_za_ark > 0 else 2000

            obrobka_stara[nazwa] = {
                'stawka_godzinowa': stawka_godzinowa,
                'wydajnosc_arkuszy_h': wydajnosc,
                'koszt_przygotowania': 20.0,  # domyślnie
                'jednostka': jednostka,
                'typ': 'obrobka',
                # Pola wymagane przez nowy kalkulator
                'cena_pln': dane['cena_pln'],
                'typ_jednostki': typ_jednostki,
                'kod_jednostki': kod_jednostki,
                'opis': dane.get('opis', ''),
            }

            # Usuń puste klucze aby uniknąć nadpisywania None
            if obrobka_stara[nazwa]['kod_jednostki'] is None:
                del obrobka_stara[nazwa]['kod_jednostki']
    slowniki_stare['obrobka'] = obrobka_stara
    
    # KOLORY SPECJALNE: cena_pln → koszt_za_kolor
    kolory_stare = {}
    for nazwa, dane in slowniki_nowe.get('kolory_specjalne', {}).items():
        if 'cena_pln' in dane:
            kolory_stare[nazwa] = {
                'koszt_za_kolor': dane['cena_pln'],
                'koszt_preparatu': dane.get('cena_preparatu_pln', 50.0),
                'czas_przygotowania_min': 30,
                'opis': dane.get('opis', '')
            }
    slowniki_stare['kolory_specjalne'] = kolory_stare

    # KOLORYSTYKI DRUKU: kopiuj wprost (zawierają metadane do UI)
    slowniki_stare['kolorystyki'] = slowniki_nowe.get('kolorystyki', {})

    # PAKOWANIE: cena_pln → cena
    pakowanie_stare = {}
    for nazwa, dane in slowniki_nowe.get('pakowanie', {}).items():
        if 'cena_pln' in dane:
            pakowanie_stare[nazwa] = {
                'cena': dane['cena_pln'],
                'opis': dane.get('opis', '')
            }
    slowniki_stare['pakowanie'] = pakowanie_stare
    
    # TRANSPORT: cena_pln → cena
    transport_stary = {}
    for nazwa, dane in slowniki_nowe.get('transport', {}).items():
        if 'cena_pln' in dane:
            transport_stary[nazwa] = {
                'cena': dane['cena_pln'],
                'czas_dni': 3 if 'standardowy' in nazwa.lower() else 1,
                'opis': dane.get('opis', '')
            }
    slowniki_stare['transport'] = transport_stary
    
    return slowniki_stare


def wstrzyknij_slowniki_do_kalkulatora(kalkulator, slowniki_mgr):
    """
    Wstrzykuje przekonwertowane słowniki do istniejącego kalkulatora
    
    Args:
        kalkulator: Instancja KalkulatorDruku
        slowniki_mgr: Instancja SlownikiManager
    """
    slowniki_nowe = slowniki_mgr.get_wszystkie()
    slowniki_stare = adapter_nowy_do_starego(slowniki_nowe)
    
    # Zaktualizuj atrybuty kalkulatora
    kalkulator.papiery = slowniki_stare['papiery']
    kalkulator.formaty = slowniki_stare['formaty']
    kalkulator.uszlachetnienia = slowniki_stare['uszlachetnienia']
    kalkulator.obrobka = slowniki_stare['obrobka']
    kalkulator.kolory_spec = slowniki_stare['kolory_specjalne']
    kalkulator.pakowanie = slowniki_stare['pakowanie']
    kalkulator.transport = slowniki_stare['transport']
    kalkulator.stawki = slowniki_stare['stawki']
    kalkulator.priorytety = slowniki_stare['priorytety']
    kalkulator.marza = slowniki_stare.get('marza', {})
    kalkulator.kolorystyki = slowniki_nowe.get('kolorystyki', {})
    kalkulator.jednostki = slowniki_nowe.get('jednostki', {})
    kalkulator.ciecie_papieru = slowniki_nowe.get('ciecie_papieru', {})  # Nowe: konfiguracja cięcia
    
    return kalkulator
