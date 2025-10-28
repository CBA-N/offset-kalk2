#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Kompletny Wszystkich Komponentów
Kalkulator Druku Offsetowego v1.2

Test sprawdza:
1. SŁOWNIKI - Papiery (CRUD)
2. SŁOWNIKI - Uszlachetnienia (CRUD)
3. SŁOWNIKI - Obróbka (CRUD)
4. PARAMETRY DRUKARNI - Stawki (edycja)
5. KALKULACJA - 3 scenariusze testowe
"""

import json
import os
import sys
from datetime import datetime

# Dodanie ścieżki do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from slowniki_manager import SlownikiManager
from kalkulator_druku_v2 import KalkulatorDruku

def print_header(text):
    """Nagłówek sekcji"""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_subheader(text):
    """Podtytuł"""
    print(f"\n{'-'*80}")
    print(f"  {text}")
    print(f"{'-'*80}\n")

def print_test_result(test_name, success, details=""):
    """Wynik testu"""
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{test_name}: {status}")
    if details:
        print(f"   {details}")

# =============================================================================
# CZĘŚĆ 1: TESTY SŁOWNIKÓW - PAPIERY
# =============================================================================

def test_slowniki_papiery():
    print_header("CZĘŚĆ 1: SŁOWNIKI - PAPIERY")
    
    manager = SlownikiManager('data/slowniki_data.json')
    
    # Test 1.1: Dodawanie papieru
    print_subheader("1.1. Test Dodawania Papieru")
    try:
        manager.dodaj_papier(
            nazwa="Test Papier 2024",
            gramatury=[100, 150, 200, 250],
            ceny=[5.0, 5.5, 6.0, 6.5],
            kategoria="niepowlekany"
        )
        
        # Weryfikacja struktury
        data = manager.wczytaj_dane()
        papier = data['papiery']['Test Papier 2024']
        
        # Sprawdzenie czy ceny są DICT, nie LISTĄ
        is_dict = isinstance(papier['ceny'], dict)
        has_correct_keys = all(str(g) in papier['ceny'] for g in [100, 150, 200, 250])
        
        print_test_result(
            "Dodawanie papieru",
            is_dict and has_correct_keys,
            f"Struktura ceny: {type(papier['ceny']).__name__} | Klucze: {list(papier['ceny'].keys())[:3]}..."
        )
    except Exception as e:
        print_test_result("Dodawanie papieru", False, str(e))
    
    # Test 1.2: Edycja papieru
    print_subheader("1.2. Test Edycji Papieru")
    try:
        manager.edytuj_papier(
            stara_nazwa="Test Papier 2024",
            nowa_nazwa="Test Papier 2024 EDITED",
            nowe_gramatury=[120, 160, 200],
            nowe_ceny=[5.2, 5.7, 6.2],
            kategoria="powlekany"
        )
        
        # Weryfikacja
        data = manager.wczytaj_dane()
        papier = data['papiery']['Test Papier 2024 EDITED']
        
        is_dict = isinstance(papier['ceny'], dict)
        correct_values = papier['ceny'].get('160') == 5.7
        correct_category = papier.get('kategoria') == 'powlekany'
        
        print_test_result(
            "Edycja papieru",
            is_dict and correct_values and correct_category,
            f"Cena 160g: {papier['ceny'].get('160')} PLN | Kategoria: {papier.get('kategoria')}"
        )
    except Exception as e:
        print_test_result("Edycja papieru", False, str(e))
    
    # Test 1.3: Kompatybilność z kalkulatorem
    print_subheader("1.3. Test Kompatybilności z Kalkulatorem")
    try:
        kalkulator = KalkulatorDruku('data/slowniki_data.json', 'data/stawki.json')
        
        # Próba odczytu ceny za gramaturę 160g
        papier_data = kalkulator.papiery['Test Papier 2024 EDITED']
        cena = papier_data['ceny'][str(160)]  # Kalkulator używa str(gramatura)
        
        print_test_result(
            "Kompatybilność",
            cena == 5.7,
            f"Odczyt ceny przez kalkulator: {cena} PLN/kg"
        )
    except Exception as e:
        print_test_result("Kompatybilność", False, str(e))
    
    # Test 1.4: Usuwanie papieru
    print_subheader("1.4. Test Usuwania Papieru")
    try:
        manager.usun_papier("Test Papier 2024 EDITED")
        
        data = manager.wczytaj_dane()
        removed = "Test Papier 2024 EDITED" not in data['papiery']
        
        print_test_result(
            "Usuwanie papieru",
            removed,
            "Papier testowy usunięty poprawnie"
        )
    except Exception as e:
        print_test_result("Usuwanie papieru", False, str(e))

# =============================================================================
# CZĘŚĆ 2: TESTY SŁOWNIKÓW - USZLACHETNIENIA
# =============================================================================

def test_slowniki_uszlachetnienia():
    print_header("CZĘŚĆ 2: SŁOWNIKI - USZLACHETNIENIA")
    
    manager = SlownikiManager('data/slowniki_data.json')
    
    # Test 2.1: Dodawanie uszlachetnienia
    print_subheader("2.1. Test Dodawania Uszlachetnienia")
    try:
        manager.dodaj_uszlachetnienie(
            nazwa="Test Lakier 2024",
            typ="lakier",
            cena_pln=2800.0,
            jednostka="1000 ark"
        )
        
        data = manager.wczytaj_dane()
        uszl = data['uszlachetnienia']['Test Lakier 2024']
        
        print_test_result(
            "Dodawanie uszlachetnienia",
            uszl['cena_pln'] == 2800.0 and uszl['typ'] == 'lakier',
            f"Cena: {uszl['cena_pln']} PLN | Typ: {uszl['typ']}"
        )
    except Exception as e:
        print_test_result("Dodawanie uszlachetnienia", False, str(e))
    
    # Test 2.2: Edycja uszlachetnienia
    print_subheader("2.2. Test Edycji Uszlachetnienia")
    try:
        manager.edytuj_uszlachetnienie(
            stara_nazwa="Test Lakier 2024",
            nowa_nazwa="Test Lakier UV Premium",
            typ="lakier",
            cena_pln=3500.0,
            jednostka="1000 ark"
        )
        
        data = manager.wczytaj_dane()
        uszl = data['uszlachetnienia']['Test Lakier UV Premium']
        
        print_test_result(
            "Edycja uszlachetnienia",
            uszl['cena_pln'] == 3500.0,
            f"Nowa cena: {uszl['cena_pln']} PLN"
        )
    except Exception as e:
        print_test_result("Edycja uszlachetnienia", False, str(e))
    
    # Test 2.3: Usuwanie uszlachetnienia
    print_subheader("2.3. Test Usuwania Uszlachetnienia")
    try:
        manager.usun_uszlachetnienie("Test Lakier UV Premium")
        
        data = manager.wczytaj_dane()
        removed = "Test Lakier UV Premium" not in data['uszlachetnienia']
        
        print_test_result(
            "Usuwanie uszlachetnienia",
            removed,
            "Uszlachetnienie testowe usunięte poprawnie"
        )
    except Exception as e:
        print_test_result("Usuwanie uszlachetnienia", False, str(e))

# =============================================================================
# CZĘŚĆ 3: TESTY SŁOWNIKÓW - OBRÓBKA
# =============================================================================

def test_slowniki_obrobka():
    print_header("CZĘŚĆ 3: SŁOWNIKI - OBRÓBKA")
    
    manager = SlownikiManager('data/slowniki_data.json')
    
    # Test 3.1-3.3: Dodawanie, edycja, usuwanie
    print_subheader("3.1. Test CRUD Obróbki")
    try:
        # Dodaj
        manager.dodaj_obrobke(
            nazwa="Test Cięcie 2024",
            jednostka="szt",
            cena_pln=0.15
        )
        
        # Edytuj
        manager.edytuj_obrobke(
            stara_nazwa="Test Cięcie 2024",
            nowa_nazwa="Test Cięcie Premium",
            jednostka="szt",
            cena_pln=0.25
        )
        
        # Weryfikuj
        data = manager.wczytaj_dane()
        obr = data['obrobka']['Test Cięcie Premium']
        
        success = obr['cena_pln'] == 0.25 and obr['jednostka'] == 'szt'
        
        # Usuń
        manager.usun_obrobke("Test Cięcie Premium")
        data = manager.wczytaj_dane()
        removed = "Test Cięcie Premium" not in data['obrobka']
        
        print_test_result(
            "CRUD Obróbki",
            success and removed,
            f"Dodawanie/Edycja/Usuwanie: OK"
        )
    except Exception as e:
        print_test_result("CRUD Obróbki", False, str(e))

# =============================================================================
# CZĘŚĆ 4: PARAMETRY DRUKARNI - STAWKI
# =============================================================================

def test_parametry_drukarni():
    print_header("CZĘŚĆ 4: PARAMETRY DRUKARNI - STAWKI")
    
    # Backup oryginalnych stawek
    with open('data/stawki.json', 'r', encoding='utf-8') as f:
        original_stawki = json.load(f)
    
    print_subheader("4.1. Sprawdzenie Obecnych Stawek")
    try:
        print(f"   Stawka godzinowa: {original_stawki['stawka_godzinowa_pln']} PLN/h")
        print(f"   Marża: {original_stawki['marza_procent']}%")
        print(f"   Koszty operacyjne: {original_stawki['koszty_operacyjne_procent']}%")
        print_test_result("Odczyt stawek", True)
    except Exception as e:
        print_test_result("Odczyt stawek", False, str(e))
    
    print_subheader("4.2. Test Edycji Stawek")
    try:
        # Modyfikacja
        modified_stawki = original_stawki.copy()
        modified_stawki['stawka_godzinowa_pln'] = 500.0  # Zmiana z 450 na 500
        
        with open('data/stawki.json', 'w', encoding='utf-8') as f:
            json.dump(modified_stawki, f, indent=2, ensure_ascii=False)
        
        # Weryfikacja
        with open('data/stawki.json', 'r', encoding='utf-8') as f:
            verified = json.load(f)
        
        success = verified['stawka_godzinowa_pln'] == 500.0
        print_test_result(
            "Edycja stawki",
            success,
            f"Nowa stawka: {verified['stawka_godzinowa_pln']} PLN/h"
        )
        
        # Rollback do oryginalnych wartości
        with open('data/stawki.json', 'w', encoding='utf-8') as f:
            json.dump(original_stawki, f, indent=2, ensure_ascii=False)
        
        print_test_result("Rollback stawek", True, "Przywrócono oryginalne wartości")
        
    except Exception as e:
        print_test_result("Edycja stawek", False, str(e))
        # Rollback w przypadku błędu
        with open('data/stawki.json', 'w', encoding='utf-8') as f:
            json.dump(original_stawki, f, indent=2, ensure_ascii=False)

# =============================================================================
# CZĘŚĆ 5: KALKULACJA - TESTY KOMPLEKSOWE
# =============================================================================

def test_kalkulacja():
    print_header("CZĘŚĆ 5: KALKULACJA - TESTY KOMPLEKSOWE")
    
    kalkulator = KalkulatorDruku('data/slowniki_data.json', 'data/stawki.json')
    
    # Test 5.1: Ulotka A5 - podstawowa kalkulacja
    print_subheader("5.1. ULOTKA A5 (5000 szt, 4+4, Kreda błysk 150g)")
    try:
        wynik = kalkulator.kalkuluj_zlecenie(
            format_wydruku=(148, 210),  # A5
            naklad=5000,
            rodzaj_papieru="Kreda błysk",
            gramatura=150,
            format_arkusza="B2",
            kolory_przod=4,
            kolory_tyl=4,
            kolory_specjalne=[],
            uszlachetnienia=[],
            obrobka=[],
            pakowanie="Folia stretch",
            transport="Odbior_osobisty"
        )
        
        print(f"   💰 Cena netto: {wynik['cena_netto']:.2f} PLN")
        print(f"   💳 Cena brutto: {wynik['cena_brutto']:.2f} PLN")
        print(f"   📋 Nakład: {wynik['naklad']} szt")
        print(f"   📏 Użytków na arkuszu: {wynik['uzytkow_na_arkuszu']}")
        print(f"   📦 Liczba arkuszy: {wynik['ilosc_arkuszy']}")
        
        success = wynik['cena_brutto'] > 0 and wynik['naklad'] == 5000
        print_test_result("Kalkulacja podstawowa", success)
        
    except Exception as e:
        print_test_result("Kalkulacja podstawowa", False, str(e))
        import traceback
        traceback.print_exc()
    
    # Test 5.2: Broszura A4 z uszlachetnieniami
    print_subheader("5.2. BROSZURA A4 (1000 szt, Kreda mat 200g, Folia mat, Bigowanie)")
    try:
        wynik = kalkulator.kalkuluj_zlecenie(
            format_wydruku=(210, 297),  # A4
            naklad=1000,
            rodzaj_papieru="Kreda mat",
            gramatura=200,
            format_arkusza="B2",
            kolory_przod=4,
            kolory_tyl=4,
            kolory_specjalne=[],
            uszlachetnienia=["Folia matowa"],
            obrobka=["Bigowanie"],
            pakowanie="Karton",
            transport="Kurier_do_50kg"
        )
        
        print(f"   💰 Cena netto: {wynik['cena_netto']:.2f} PLN")
        print(f"   💳 Cena brutto: {wynik['cena_brutto']:.2f} PLN")
        print(f"   ✨ Uszlachetnienia: Folia matowa")
        print(f"   🔧 Obróbka: Bigowanie")
        
        success = wynik['cena_brutto'] > 0 and len(wynik.get('szczegoly_uszlachetnien', {})) > 0
        print_test_result("Kalkulacja z uszlachetnieniami", success)
        
    except Exception as e:
        print_test_result("Kalkulacja z uszlachetnieniami", False, str(e))
        import traceback
        traceback.print_exc()
    
    # Test 5.3: Wizytówki z optymalizacją - TEST KRYTYCZNY (wcześniej crashował)
    print_subheader("5.3. WIZYTÓWKI (10000 szt, Kreda błysk 350g, Folia błysk)")
    try:
        wynik = kalkulator.kalkuluj_zlecenie(
            format_wydruku=(90, 50),  # Wizytówka
            naklad=10000,
            rodzaj_papieru="Kreda błysk",
            gramatura=350,
            format_arkusza="B2",
            kolory_przod=4,
            kolory_tyl=0,
            kolory_specjalne=[],
            uszlachetnienia=["Folia błysk"],  # TO WCZEŚNIEJ POWODOWAŁO KeyError
            obrobka=["Cięcie"],
            pakowanie="Karton",
            transport="Kurier_do_10kg"
        )
        
        print(f"   💰 Cena netto: {wynik['cena_netto']:.2f} PLN")
        print(f"   💳 Cena brutto: {wynik['cena_brutto']:.2f} PLN")
        print(f"   📏 Użytków na arkuszu: {wynik['uzytkow_na_arkuszu']} (optymalizacja!)")
        print(f"   ✨ Uszlachetnienie: Folia błysk")
        
        success = wynik['cena_brutto'] > 0 and wynik['uzytkow_na_arkuszu'] > 1
        print_test_result("Kalkulacja z optymalizacją", success)
        
    except Exception as e:
        print_test_result("Kalkulacja z optymalizacją", False, str(e))
        import traceback
        traceback.print_exc()

# =============================================================================
# MAIN - URUCHOMIENIE WSZYSTKICH TESTÓW
# =============================================================================

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "KALKULATOR DRUKU OFFSETOWEGO v1.2" + " "*30 + "║")
    print("║" + " "*20 + "TEST KOMPLETNY WSZYSTKICH KOMPONENTÓW" + " "*21 + "║")
    print("╚" + "="*78 + "╝")
    
    start_time = datetime.now()
    
    try:
        test_slowniki_papiery()
        test_slowniki_uszlachetnienia()
        test_slowniki_obrobka()
        test_parametry_drukarni()
        test_kalkulacja()
        
        # Podsumowanie
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print_header("PODSUMOWANIE TESTÓW")
        print(f"✅ Wszystkie testy zakończone")
        print(f"⏱️  Czas wykonania: {duration:.2f} s")
        print(f"📅 Data testu: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print_header("BŁĄD KRYTYCZNY")
        print(f"❌ Test przerwany: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
