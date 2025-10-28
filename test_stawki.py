#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Zapisywania Stawek Drukarni
"""

import sys
import os
import json

sys.path.insert(0, 'backend')

from slowniki_manager import SlownikiManager

print("="*80)
print("TEST ZAPISYWANIA STAWEK DRUKARNI")
print("="*80)

manager = SlownikiManager('data/slowniki_data.json')

# Backup oryginalnych stawek
stawki_orig = manager.slowniki['stawki'].copy()
print("\n1. Stawki oryginalne:")
for k, v in stawki_orig.items():
    print(f"   {k}: {v}")

# Test 1: Zapisywanie poprawnych wartości
print("\n2. TEST: Zapisywanie poprawnych wartości")
try:
    manager.edytuj_stawke('roboczogodzina_przygotowania_pln', 100.0)
    print("   ✅ roboczogodzina_przygotowania: 100.0 PLN")
    
    manager.edytuj_stawke('roboczogodzina_druku_pln', 120.0)
    print("   ✅ roboczogodzina_druku: 120.0 PLN")
    
    manager.edytuj_stawke('forma_offsetowa_pln', 50.0)
    print("   ✅ forma_offsetowa: 50.0 PLN")
    
    manager.edytuj_stawke('koszt_1000_arkuszy_pln', 60.0)
    print("   ✅ koszt_1000_arkuszy: 60.0 PLN")

    manager.edytuj_stawke('szybkosc_druku_arkuszy_h', 4500)
    print("   ✅ szybkosc_druku_arkuszy_h: 4500 ark/h")
    
except Exception as e:
    print(f"   ❌ BŁĄD: {e}")

# Weryfikacja
print("\n3. Weryfikacja zapisanych wartości:")
stawki_new = manager.slowniki['stawki']
print(f"   roboczogodzina_przygotowania: {stawki_new.get('roboczogodzina_przygotowania')}")
print(f"   koszt_formy_drukowej: {stawki_new.get('koszt_formy_drukowej')}")
print(f"   stawka_nakladu_1000_arkuszy: {stawki_new.get('stawka_nakladu_1000_arkuszy')}")
print(f"   szybkosc_druku_arkuszy_h: {stawki_new.get('szybkosc_druku_arkuszy_h')}")

# Test 2: Próba zapisania None
print("\n4. TEST: Próba zapisania None (powinno być odrzucone)")
try:
    manager.edytuj_stawke('roboczogodzina_przygotowania_pln', None)
    print("   ❌ Przyjęto None - TO BŁĄD!")
except ValueError as e:
    print(f"   ✅ Odrzucono None: {e}")

# Test 3: Próba zapisania wartości ujemnej
print("\n5. TEST: Próba zapisania wartości ujemnej (powinno być odrzucone)")
try:
    manager.edytuj_stawke('forma_offsetowa_pln', -10.0)
    print("   ❌ Przyjęto wartość ujemną - TO BŁĄD!")
except ValueError as e:
    print(f"   ✅ Odrzucono wartość ujemną: {e}")

# Test 4: Próba zapisania wartości zero
print("\n6. TEST: Próba zapisania wartości zero (powinno być odrzucone)")
try:
    manager.edytuj_stawke('koszt_1000_arkuszy_pln', 0)
    print("   ❌ Przyjęto zero - TO BŁĄD!")
except ValueError as e:
    print(f"   ✅ Odrzucono zero: {e}")

# Rollback do oryginalnych wartości
print("\n7. Rollback do oryginalnych wartości...")
for k, v in stawki_orig.items():
    # Mapowanie kluczy
    if k == 'roboczogodzina_przygotowania':
        manager.edytuj_stawke('roboczogodzina_przygotowania_pln', v)
    elif k == 'koszt_formy_drukowej':
        manager.edytuj_stawke('forma_offsetowa_pln', v)
    elif k == 'stawka_nakladu_1000_arkuszy':
        manager.edytuj_stawke('koszt_1000_arkuszy_pln', v)
    elif k == 'szybkosc_druku_arkuszy_h':
        manager.edytuj_stawke('szybkosc_druku_arkuszy_h', v)

print("   ✅ Przywrócono oryginalne wartości")

# Finalna weryfikacja
print("\n8. Finalna weryfikacja:")
stawki_final = manager.slowniki['stawki']
for k, v in stawki_final.items():
    print(f"   {k}: {v}")

print("\n" + "="*80)
print("✅ TESTY ZAKOŃCZONE")
print("="*80)
