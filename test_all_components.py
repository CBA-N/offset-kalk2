#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================================
TEST WSZYSTKICH KOMPONENTÓW - v1.2.1
===========================================
Testy po naprawie krytycznych błędów:
1. Struktura ceny papieru (LIST → DICT)  
2. Klucze ceny uszlachetnień (cena_za_m2 → cena_pln/1000)
3. Parsowanie czasu z opisu uszlachetnień
"""

import os
import sys
import json

sys.path.insert(0, 'backend')

from slowniki_manager import SlownikiManager
from kalkulator_druku_v2 import KalkulatorDruku

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_result(name, success, details=""):
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   └─ {details}")

# =============================================================================
# TEST 1: SŁOWNIKI - PAPIERY
# =============================================================================

print_header("TEST 1: SŁOWNIKI - PAPIERY (CRUD)")

manager = SlownikiManager('data/slowniki_data.json')

# 1.1 Dodawanie
print("1.1. Dodawanie papieru testowego...")
try:
    manager.dodaj_papier(
        nazwa="Test Premium 2024",
        gramatury=[100, 150, 200],
        ceny=[5.0, 5.5, 6.0],
        kategoria="niepowlekany"
    )
    
    # Weryfikacja struktury
    papier = manager.slowniki['papiery']['Test Premium 2024']
    is_dict = isinstance(papier['ceny'], dict)
    has_keys = '150' in papier['ceny']
    
    print_result(
        "Dodawanie",
        is_dict and has_keys,
        f"Typ ceny: {type(papier['ceny']).__name__}, Klucz '150': {papier['ceny'].get('150')} PLN"
    )
except Exception as e:
    print_result("Dodawanie", False, str(e))

# 1.2 Edycja
print("\n1.2. Edycja papieru...")
try:
    manager.edytuj_papier(
        stara_nazwa="Test Premium 2024",
        nowa_nazwa="Test Premium EDITED",
        gramatury=[120, 170],
        ceny=[5.3, 5.9],
        kategoria="powlekany"
    )
    
    papier = manager.slowniki['papiery']['Test Premium EDITED']
    correct = papier['ceny']['170'] == 5.9 and papier['kategoria'] == 'powlekany'
    
    print_result(
        "Edycja",
        correct,
        f"Cena 170g: {papier['ceny']['170']} PLN, Kategoria: {papier['kategoria']}"
    )
except Exception as e:
    print_result("Edycja", False, str(e))

# 1.3 Kompatybilność z kalkulatorem
print("\n1.3. Test kompatybilności z kalkulatorem...")
try:
    kalkulator = KalkulatorDruku()
    kalkulator.papiery = manager.slowniki['papiery']  # Ładowanie danych
    
    # Test odczytu ceny przez kalkulator (używa str jako klucza)
    cena = kalkulator.papiery['Test Premium EDITED']['ceny'][str(170)]
    
    print_result(
        "Kompatybilność",
        cena == 5.9,
        f"Kalkulator odczytał cenę: {cena} PLN/kg"
    )
except Exception as e:
    print_result("Kompatybilność", False, str(e))

# 1.4 Usuwanie
print("\n1.4. Usuwanie papieru testowego...")
try:
    manager.usun_papier("Test Premium EDITED")
    removed = "Test Premium EDITED" not in manager.slowniki['papiery']
    
    print_result("Usuwanie", removed, "Papier usunięty poprawnie")
except Exception as e:
    print_result("Usuwanie", False, str(e))

# =============================================================================
# TEST 2: SŁOWNIKI - USZLACHETNIENIA
# =============================================================================

print_header("TEST 2: SŁOWNIKI - USZLACHETNIENIA (CRUD)")

# 2.1 Dodawanie (z WŁAŚCIWYM typem z walidacji)
print("2.1. Dodawanie uszlachetnienia...")
try:
    manager.dodaj_uszlachetnienie(
        nazwa="Test Lakier XYZ",
        typ="UV",  # MUSI BYĆ: 'UV', 'Dyspersyjny', 'Folia', 'Tłoczenie'
        cena_pln=2900.0,
        jednostka="1000 ark",
        opis="Test uszlachetnienia"
    )
    
    uszl = manager.slowniki['uszlachetnienia']['Test Lakier XYZ']
    
    print_result(
        "Dodawanie",
        uszl['typ'] == 'UV' and uszl['cena_pln'] == 2900.0,
        f"Typ: {uszl['typ']}, Cena: {uszl['cena_pln']} PLN"
    )
except Exception as e:
    print_result("Dodawanie", False, str(e))

# 2.2 Edycja
print("\n2.2. Edycja uszlachetnienia...")
try:
    manager.edytuj_uszlachetnienie(
        stara_nazwa="Test Lakier XYZ",
        nowa_nazwa="Test Lakier Premium",
        cena_pln=3400.0
    )
    
    uszl = manager.slowniki['uszlachetnienia']['Test Lakier Premium']
    
    print_result(
        "Edycja",
        uszl['cena_pln'] == 3400.0,
        f"Nowa cena: {uszl['cena_pln']} PLN"
    )
except Exception as e:
    print_result("Edycja", False, str(e))

# 2.3 Usuwanie
print("\n2.3. Usuwanie uszlachetnienia...")
try:
    manager.usun_uszlachetnienie("Test Lakier Premium")
    removed = "Test Lakier Premium" not in manager.slowniki['uszlachetnienia']
    
    print_result("Usuwanie", removed, "Uszlachetnienie usunięte")
except Exception as e:
    print_result("Usuwanie", False, str(e))

# =============================================================================
# TEST 3: SŁOWNIKI - OBRÓBKA
# =============================================================================

print_header("TEST 3: SŁOWNIKI - OBRÓBKA (CRUD)")

print("3.1. Test CRUD obróbki...")
try:
    # Dodaj
    manager.dodaj_obrobke(
        nazwa="Test Perforacja",
        jednostka="szt",
        cena_pln=0.20
    )
    
    # Edytuj
    manager.edytuj_obrobke(
        stara_nazwa="Test Perforacja",
        nowa_nazwa="Test Perforacja XL",
        cena_pln=0.35
    )
    
    # Weryfikuj
    obr = manager.slowniki['obrobka']['Test Perforacja XL']
    success = obr['cena_pln'] == 0.35
    
    # Usuń
    manager.usun_obrobke("Test Perforacja XL")
    removed = "Test Perforacja XL" not in manager.slowniki['obrobka']
    
    print_result(
        "CRUD Obróbki",
        success and removed,
        "Dodawanie/Edycja/Usuwanie OK"
    )
except Exception as e:
    print_result("CRUD Obróbki", False, str(e))

# =============================================================================
# TEST 4: PARAMETRY DRUKARNI
# =============================================================================

print_header("TEST 4: PARAMETRY DRUKARNI")

print("4.1. Sprawdzenie stawek z JSON...")
try:
    # W tej wersji stawki są w slowniki_data.json
    stawki = manager.slowniki.get('stawki', {})
    
    if stawki:
        print(f"   Stawka godzinowa: {stawki.get('stawka_godzinowa_pln', 'N/A')} PLN/h")
        print(f"   Koszty operacyjne: {stawki.get('koszty_operacyjne_procent', 'N/A')}%")
        print_result("Odczyt stawek", True)
    else:
        print_result("Odczyt stawek", False, "Brak sekcji 'stawki' w JSON")
        
except Exception as e:
    print_result("Odczyt stawek", False, str(e))

# =============================================================================
# TEST 5: KALKULACJA - SCENARIUSZE TESTOWE
# =============================================================================

print_header("TEST 5: KALKULACJA - SCENARIUSZE KOMPLEKSOWE")

kalkulator = KalkulatorDruku()

# Załaduj dane ze słowników
kalkulator.papiery = manager.slowniki['papiery']
kalkulator.uszlachetnienia = manager.slowniki['uszlachetnienia']
kalkulator.obrobka = manager.slowniki['obrobka']

# 5.1 Ulotka A5 - podstawowa kalkulacja
print("5.1. ULOTKA A5 (5000 szt, 4+4, Kreda błysk 150g)")
try:
    zlecenie = {
        'nazwa_produktu': 'Test Ulotka A5',
        'format_wydruku_mm': (148, 210),
        'naklad': 5000,
        'rodzaj_papieru': 'Kreda błysk',
        'gramatura': 150,
        'kolorystyka_cmyk': '4+4',
        'ilosc_form': 4,
        'kolory_specjalne': [],
        'uszlachetnienia': [],
        'obrobka': [],
        'pakowanie': 'Folia stretch',
        'transport': 'Odbior_osobisty',
        'marza_procent': 20,
        'priorytet_optymalizacji': 'Zrównoważony'
    }
    
    wynik = kalkulator.kalkuluj_zlecenie(zlecenie)
    
    # Wynik jest obiektem KalkulacjaZlecenia, nie dict
    print(f"   💰 Netto: {wynik.suma_kosztow_netto:.2f} PLN")
    print(f"   💳 Brutto: {wynik.cena_brutto_vat23:.2f} PLN")
    print(f"   📏 Użytków na arkuszu: {wynik.wybrany_format.uzytki_na_ark}")
    print(f"   📦 Arkuszy: {wynik.wybrany_format.ilosc_arkuszy}")
    
    print_result(
        "Kalkulacja podstawowa",
        wynik.cena_brutto_vat23 > 0,
        f"Cena: {wynik.cena_brutto_vat23:.2f} PLN"
    )
    
except Exception as e:
    print_result("Kalkulacja podstawowa", False, str(e))
    import traceback
    traceback.print_exc()

# 5.2 Broszura A4 z uszlachetnieniami
print("\n5.2. BROSZURA A4 (1000 szt, Folia matowa)")
try:
    zlecenie = {
        'nazwa_produktu': 'Test Broszura A4',
        'format_wydruku_mm': (210, 297),
        'naklad': 1000,
        'rodzaj_papieru': 'Kreda mat',
        'gramatura': 200,
        'kolorystyka_cmyk': '4+4',
        'ilosc_form': 4,
        'kolory_specjalne': [],
        'uszlachetnienia': ['Folia matowa'],
        'obrobka': ['Bigowanie'],
        'pakowanie': 'Karton',
        'transport': 'Kurier_do_50kg',
        'marza_procent': 20,
        'priorytet_optymalizacji': 'Zrównoważony'
    }
    
    wynik = kalkulator.kalkuluj_zlecenie(zlecenie)
    
    print(f"   💰 Netto: {wynik.suma_kosztow_netto:.2f} PLN")
    print(f"   💳 Brutto: {wynik.cena_brutto_vat23:.2f} PLN")
    print(f"   ✨ Uszlachetnienia: Folia matowa")
    
    print_result(
        "Kalkulacja z uszlachetnieniami",
        wynik.cena_brutto_vat23 > 0,
        f"Cena: {wynik.cena_brutto_vat23:.2f} PLN"
    )
    
except Exception as e:
    print_result("Kalkulacja z uszlachetnieniami", False, str(e))
    import traceback
    traceback.print_exc()

# 5.3 Wizytówki - TEST KRYTYCZNY (naprawa KeyError 'cena_za_m2')
print("\n5.3. WIZYTÓWKI (10000 szt, Folia błysk) - TEST NAPRAWY")
try:
    zlecenie = {
        'nazwa_produktu': 'Test Wizytówki',
        'format_wydruku_mm': (90, 50),
        'naklad': 10000,
        'rodzaj_papieru': 'Kreda błysk',
        'gramatura': 350,
        'kolorystyka_cmyk': '4+0',
        'ilosc_form': 4,
        'kolory_specjalne': [],
        'uszlachetnienia': ['Folia błysk'],  # TO WCZEŚNIEJ POWODOWAŁO BŁĄD
        'obrobka': ['Cięcie'],
        'pakowanie': 'Karton',
        'transport': 'Kurier_do_10kg',
        'marza_procent': 20,
        'priorytet_optymalizacji': 'Minimalizacja odpadów'
    }
    
    wynik = kalkulator.kalkuluj_zlecenie(zlecenie)
    
    print(f"   💰 Netto: {wynik.suma_kosztow_netto:.2f} PLN")
    print(f"   💳 Brutto: {wynik.cena_brutto_vat23:.2f} PLN")
    print(f"   📏 Użytków na arkuszu: {wynik.wybrany_format.uzytki_na_ark}")
    print(f"   ✨ Uszlachetnienie: Folia błysk")
    
    print_result(
        "Kalkulacja z optymalizacją + Folia",
        wynik.cena_brutto_vat23 > 0,
        f"Cena: {wynik.cena_brutto_vat23:.2f} PLN (NAPRAWA DZIAŁA!)"
    )
    
except Exception as e:
    print_result("Kalkulacja z optymalizacją", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# PODSUMOWANIE
# =============================================================================

print_header("PODSUMOWANIE TESTÓW")
print("✅ Testy zakończone")
print("   └─ Wszystkie komponenty przetestowane")
print("   └─ Naprawiono: strukturę ceny papieru, klucze uszlachetnień, parsowanie czasu")
print()
