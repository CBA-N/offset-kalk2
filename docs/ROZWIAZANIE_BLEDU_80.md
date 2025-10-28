# ✅ Rozwiązanie błędu "błąd kalkulacji: 80"

## 🔍 Diagnoza problemu

**Problem:** User zgłasza "błąd kalkulacji: 80" przy domyślnych wartościach formularza.

**Przyczyna:** User prawdopodobnie ma **STARĄ WERSJĘ plików backend** - przed naprawą Problemu #7 (konflikt typów kluczy w słowniku cen).

**Potwierdzenie:**
- ✅ Mój backend (localhost:5000) DZIAŁA - test curl zwraca `success: true`
- ❌ Backend użytkownika POKAZUJE BŁĄD - frontend wyświetla "błąd kalkulacji: 80"
- ⚠️ Folder `kalkulator_v1.2_clean` miał **starą datę** plików (przed 11:20, kiedy naprawiono Problem #7)

---

## 🚀 ROZWIĄZANIE: Pobierz najnowsze pliki

### Opcja A: Pobierz pełny zaktualizowany projekt

**Z AI Drive:** `/kalkulator_v1.2_clean`

Zawiera:
- ✅ Wszystkie 7 napraw (w tym kluczową naprawę #7)
- ✅ Zaktualizowane pliki backend z dzisiejszą datą (Oct 24 11:18-11:20)
- ✅ Pełną dokumentację napraw w folderze `docs/`
- ✅ Testy regresyjne

**Instalacja:**
1. Usuń stary folder `webapp` na swoim komputerze
2. Pobierz `/kalkulator_v1.2_clean` z AI Drive
3. Skopiuj swoje pliki danych (jeśli były modyfikowane):
   - `backend/data/slowniki_data.json`
   - `backend/data/historia_ofert.json`
   - `backend/data/kontrahenci.json`
4. Uruchom:
   ```bash
   cd kalkulator_v1.2_clean
   pip install -r requirements.txt
   cd backend
   python3 app.py
   ```

### Opcja B: Zaktualizuj tylko kluczowe pliki

Jeśli chcesz zachować obecną strukturę, skopiuj **tylko 4 naprawione pliki**:

**Pliki do aktualizacji** (w folderze `backend/`):
1. `slowniki_adapter.py` ← KLUCZOWY (naprawa #7)
2. `kalkulator_druku_v2.py` ← naprawy #4, #5, #7
3. `slowniki_manager.py` ← naprawa #6
4. `app.py` ← integracja wszystkich napraw

**Po skopiowaniu:**
1. Zrestartuj serwer Flask (Ctrl+C, potem `python3 app.py`)
2. Wyczyść cache przeglądarki (Ctrl+Shift+Del lub Ctrl+F5)
3. Spróbuj ponownie kalkulacji

---

## ✅ Weryfikacja poprawności plików

### Sprawdź czy masz poprawną wersję:

**1. slowniki_adapter.py - linia 22:**
```python
'ceny': {str(k): v for k, v in dane['ceny'].items()},  # Zachowaj jako String!
```
❌ STARA (błędna): `{int(k): v ...}` 
✅ NOWA (poprawna): `{str(k): v ...}`

**2. kalkulator_druku_v2.py - linia 144:**
```python
cena_kg = self.papiery[rodzaj_papieru]['ceny'][str(gramatura)]
```
✅ Musi zawierać `[str(gramatura)]`

**3. Data modyfikacji plików:**
Wszystkie 4 pliki powinny mieć **dzisiejszą datę (Oct 24 2025)**:
```bash
ls -lh backend/*.py | grep "Oct 24"
```

---

## 🧪 Test po aktualizacji

### Test 1: Backend API (terminal)
```bash
curl -X POST http://localhost:5000/api/kalkuluj \
  -H "Content-Type: application/json" \
  -d '{
    "nazwa_produktu": "Test 80g",
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

**Oczekiwany wynik:**
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

### Test 2: Frontend (przeglądarka)
1. Otwórz http://localhost:5000/
2. Wypełnij formularz:
   - Nazwa: "Test"
   - Nakład: 1000
   - Format: 210x297 (A4)
   - Papier: "Kreda błysk"
   - Gramatura: 80
   - Kolorystyka: 4+0
3. Kliknij "Oblicz kalkulację"

**Oczekiwany wynik:**
- ✅ Wyświetla się oferta z ceną około 451.79 PLN brutto
- ✅ Brak błędów w konsoli (F12 → Console)

---

## 🐛 Jeśli nadal nie działa

### Diagnostyka zaawansowana:

**1. Sprawdź DevTools w przeglądarce:**
- Naciśnij F12
- Zakładka **Network**
- Kliknij "Oblicz kalkulację"
- Znajdź request `/api/kalkuluj`
- Sprawdź:
  - **Request Payload** - co wysyła frontend
  - **Response** - co zwraca backend
  - **Status code** - powinien być 200

**2. Sprawdź logi serwera Flask:**
W terminalu gdzie działa `python3 app.py` powinny pojawić się logi:
```
POST /api/kalkuluj
```

Jeśli jest błąd, pojawi się stacktrace z dokładną linią problemu.

**3. Sprawdź strukturę JSON:**
```bash
python3 -c "
import json
d = json.load(open('backend/data/slowniki_data.json'))
p = d['papiery']['Kreda błysk']
print('Typ cen:', type(p['ceny']))
print('Klucze:', list(p['ceny'].keys())[:5])
print('Typy:', [type(k) for k in list(p['ceny'].keys())[:3]])
"
```

**Oczekiwany wynik:**
```
Typ cen: <class 'dict'>
Klucze: ['80', '90', '100', '115', '130']
Typy: [<class 'str'>, <class 'str'>, <class 'str'>]
```

---

## 📋 Podsumowanie wszystkich napraw

### Problem #7 (KLUCZOWY dla tego błędu):
**Symptom:** KeyError '80', KeyError '115' przy kalkulacji
**Przyczyna:** Adapter konwertował klucze na `int`, kalkulator używał `str`
**Rozwiązanie:** Zmiana w `slowniki_adapter.py` linia 22: `{str(k): v ...}`

### Problem #4:
**Symptom:** KeyError 'cena_za_m2' przy uszlachetnieniach
**Rozwiązanie:** Konwersja `cena_za_m2 = cena_pln / 1000` w `kalkulator_druku_v2.py`

### Problem #5:
**Symptom:** KeyError 'czas_przygotowania_min' przy uszlachetnieniach
**Rozwiązanie:** Regex parsing `r'Czas:\s*(\d+)\s*min'` z opisu

### Problem #6:
**Symptom:** TypeError przy zapisywaniu stawek drukarni
**Rozwiązanie:** Walidacja `None`, mapowanie kluczy JSON, walidacja frontendowa

### Problemy #1-3:
- Struktura ceny papieru (LIST → DICT)
- Klucze ceny (naprawione w #7)
- Parametr kategoria

---

## 📞 Kontakt

Jeśli problem nadal występuje po wykonaniu powyższych kroków, proszę o:
1. ✅ Screenshot błędu z przeglądarki
2. ✅ Screenshot DevTools → Network → /api/kalkuluj
3. ✅ Output terminala gdzie działa Flask
4. ✅ Wynik komendy `ls -lh backend/*.py | grep "Oct 24"`

---

## 📚 Dokumentacja

Pełna dokumentacja wszystkich napraw znajduje się w folderze `docs/`:
- `AUDYT_KODU_I_POPRAWKI.md` - szczegółowy raport wszystkich 7 problemów
- `NAPRAWA_USZLACHETNIEN_I_TESTY.md` - problemy #4 i #5
- `NAPRAWA_STAWEK_DRUKARNI.md` - problem #6
- `PODSUMOWANIE_SESJI_TESTOW.md` - wyniki testów 14/14 PASS
