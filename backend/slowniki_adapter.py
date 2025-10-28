"""
Adapter słowników - konwertuje nową strukturę danych (z cena_pln)
na starą strukturę wymaganą przez KalkulatorDruku
"""


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
    }
    
    # USZLACHETNIENIA: cena_pln → cena_za_m2, cena_za_arkusz_B2, cena_za_arkusz_A2
    uszlachetnienia_stare = {}
    for nazwa, dane in slowniki_nowe.get('uszlachetnienia', {}).items():
        if 'cena_pln' in dane:
            # cena_pln jest za 1000 ark, więc dla 1 arkusza:
            cena_arkusz = dane['cena_pln'] / 1000
            
            # Oblicz cena_za_m2 (zakładając arkusz B2 = 0.35 m²)
            cena_za_m2 = cena_arkusz / 0.35
            
            # Arkusze: B2 (500x700mm = 0.35m²), A2 (420x594mm = 0.25m²)
            uszlachetnienia_stare[nazwa] = {
                'cena_za_m2': cena_za_m2,
                'cena_za_arkusz_B2': cena_arkusz,
                'cena_za_arkusz_A2': cena_arkusz * (0.25 / 0.35),  # proporcja powierzchni
                'czas_przygotowania_min': 45,  # domyślnie
                'jednostka': 'm²',
                'typ': dane.get('typ', 'lakier')
            }
    slowniki_stare['uszlachetnienia'] = uszlachetnienia_stare
    
    # OBRÓBKA: cena_pln → stawka_godzinowa, wydajnosc_arkuszy_h
    obrobka_stara = {}
    for nazwa, dane in slowniki_nowe.get('obrobka', {}).items():
        if 'cena_pln' in dane:
            # cena_pln jest za 1000 ark
            # Zakładamy: stawka = 80 PLN/h, wydajność = stawka / (cena_pln/1000)
            cena_za_ark = dane['cena_pln'] / 1000
            stawka_godzinowa = 80.0  # standard
            wydajnosc = stawka_godzinowa / cena_za_ark if cena_za_ark > 0 else 2000
            
            obrobka_stara[nazwa] = {
                'stawka_godzinowa': stawka_godzinowa,
                'wydajnosc_arkuszy_h': wydajnosc,
                'koszt_przygotowania': 20.0,  # domyślnie
                'jednostka': 'arkusz',
                'typ': 'obrobka'
            }
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
    kalkulator.ciecie_papieru = slowniki_nowe.get('ciecie_papieru', {})  # Nowe: konfiguracja cięcia
    
    return kalkulator
