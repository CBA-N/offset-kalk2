# 🔍 Diagnostyka błędu "błąd kalkulacji: 80"

## Status backendów

### ✅ Backend na moim serwerze (DZIAŁA):
```bash
curl -X POST http://localhost:5000/api/kalkuluj \
  -H "Content-Type: application/json" \
  -d '{"gramatura": 80, "rodzaj_papieru": "Kreda błysk", ...}'
  
Response: {"success": true, "cena_brutto_vat23": 451.79}
```

### ❌ Backend użytkownika (POKAZUJE BŁĄD):
User zgłasza: "ciągle kalkulacja wali 'błąd kalkulacji: 80' na defaultowych wartościach"

---

## Możliwe przyczyny

### 1. Stare pliki (najprawdopodobniejsze)
User może nie mieć zaktualizowanego `slowniki_adapter.py` z naprawą #7:

**Sprawdzenie:**
```python
# W pliku slowniki_adapter.py linia 22 MUSI być:
'ceny': {str(k): v for k, v in dane['ceny'].items()},  # String!

# STARA wersja (błędna):
'ceny': {int(k): v for k, v in dane['ceny'].items()},  # Int! ❌
```

### 2. Cache przeglądarki
Przeglądarka może ładować stary JavaScript z cache.

**Rozwiązanie:**
- Ctrl+Shift+Del → Wyczyść cache
- Lub Ctrl+F5 (hard refresh)

### 3. Niewłaściwy serwer/port
User może łączyć się z innym serwerem.

**Sprawdzenie:**
- Sprawdź URL w przeglądarce: http://localhost:5000/
- Sprawdź w DevTools → Network → Request URL

### 4. Problem struktury JSON
Jeśli user edytował `slowniki_data.json` ręcznie.

**Sprawdzenie:**
```python
import json
d = json.load(open('slowniki_data.json'))
p = d['papiery']['Kreda błysk']
print('Typ cen:', type(p['ceny']))  # Musi być: <class 'dict'>
print('Klucze:', list(p['ceny'].keys())[:5])  # Musi być: ['80', '90', ...]
print('Typy:', [type(k) for k in list(p['ceny'].keys())[:3]])  # Wszystkie <class 'str'>
```

---

## Plan diagnostyczny dla usera

### Krok 1: Sprawdź Network request w przeglądarce
1. Otwórz aplikację w przeglądarce
2. Naciśnij F12 (otwórz DevTools)
3. Zakładka **Network**
4. Wypełnij formularz domyślnymi wartościami
5. Kliknij "Oblicz kalkulację"
6. Znajdź request `/api/kalkuluj`
7. **SCREENSHOT:**
   - Request Headers
   - Request Payload (co wysyła frontend)
   - Response (co zwraca backend)

### Krok 2: Sprawdź Console errors
W DevTools → zakładka **Console**
- Czy są czerwone błędy JavaScript?
- Czy są ostrzeżenia?

### Krok 3: Sprawdź aktualną wersję plików
```bash
# W folderze webapp:
grep -n "str(k)" slowniki_adapter.py
# Linia 22 MUSI zawierać: {str(k): v for k, v in dane['ceny'].items()}

grep -n "str(gramatura)" kalkulator_druku_v2.py
# Linia 144 MUSI zawierać: ceny[str(gramatura)]
```

### Krok 4: Zrestartuj serwer
```bash
# Zatrzymaj obecny serwer (Ctrl+C)
# Uruchom ponownie:
cd webapp
python3 app.py
```

### Krok 5: Wyczyść cache przeglądarki
- Chrome/Edge: Ctrl+Shift+Del → "Cached images and files"
- Lub: Ctrl+F5 (hard refresh)

---

## Pliki które MUSZĄ być zaktualizowane

### slowniki_adapter.py (Problem #7 - KLUCZOWY!)
```python
# Linia 22 - POPRAWNA wersja:
'ceny': {str(k): v for k, v in dane['ceny'].items()},
```

### kalkulator_druku_v2.py (Problemy #4, #5, #7)
```python
# Linia 144 - dostęp do cen:
cena_kg = self.papiery[rodzaj_papieru]['ceny'][str(gramatura)]

# Linia 267 - konwersja ceny:
cena_za_m2 = cena_pln / 1000

# Linia 274-284 - parsing czasu:
import re
match = re.search(r'Czas:\s*(\d+)\s*min', opis)
```

### slowniki_manager.py (Problem #6)
```python
# Linia 481-510 - walidacja None w edytuj_stawke()
if wartosc is None or not isinstance(wartosc, (int, float)):
    raise ValueError(...)
```

---

## Jeśli nadal nie działa

### Test backend bezpośrednio:
```bash
# W terminalu (z folderu webapp):
curl -X POST http://localhost:5000/api/kalkuluj \
  -H "Content-Type: application/json" \
  -d '{
    "nazwa_produktu": "Test",
    "format_szerokosc": 210,
    "format_wysokosc": 297,
    "naklad": 1000,
    "rodzaj_papieru": "Kreda błysk",
    "gramatura": 80,
    "kolorystyka": "4+0",
    "ilosc_form": 4,
    "kolory_specjalne": [],
    "uszlachetnienia": [],
    "obrobka": [],
    "pakowanie": "",
    "transport": "",
    "marza_procent": 20,
    "priorytet_optymalizacji": "Zrównoważony"
  }'
```

**Oczekiwany result:**
```json
{
  "success": true,
  "wynik": {
    "cena_brutto_vat23": 451.79,
    "gramatura": 80,
    ...
  }
}
```

Jeśli ten test **DZIAŁA**, problem jest w **frontendzie** (JavaScript/cache).
Jeśli ten test **NIE DZIAŁA**, problem jest w **backendzie** (stare pliki).

---

## Szybkie rozwiązanie (nuclear option)

Jeśli nic nie pomaga:

1. **Backup obecnych danych:**
   ```bash
   cp webapp/slowniki_data.json ~/backup_slowniki.json
   cp webapp/historia_ofert.json ~/backup_historia.json
   cp webapp/kontrahenci.json ~/backup_kontrahenci.json
   ```

2. **Usuń folder webapp:**
   ```bash
   rm -rf webapp
   ```

3. **Skopiuj naprawiony folder:**
   ```bash
   cp -r kalkulator_v1.2_clean webapp
   ```

4. **Przywróć dane:**
   ```bash
   cp ~/backup_slowniki.json webapp/slowniki_data.json
   cp ~/backup_historia.json webapp/historia_ofert.json
   cp ~/backup_kontrahenci.json webapp/kontrahenci.json
   ```

5. **Uruchom serwer:**
   ```bash
   cd webapp
   python3 app.py
   ```

---

## Kontakt

Jeśli problem nadal występuje, proszę o:
1. Screenshot błędu z przeglądarki
2. Screenshot DevTools → Network → /api/kalkuluj (Request + Response)
3. Screenshot DevTools → Console
4. Output z terminalu gdzie działa serwer Flask
