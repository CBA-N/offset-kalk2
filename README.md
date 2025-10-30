# 🖨️ KALKULATOR DRUKU OFFSETOWEGO - WERSJA 1.3

## 🆕 NOWOŚCI W WERSJI 1.3

### ✂️ Cięcie Papieru z Arkuszy B1
- Automatyczna kalkulacja kosztu cięcia papieru z formatu B1 (700×1000mm)
- Inteligentny algorytm optymalizacji orientacji cięcia
- Konfigurowalne parametry w panelu Słowniki → Cięcie Papieru

### 📐 Elastyczne Jednostki Rozliczeniowe
- 3 typy jednostek: sztukowa, metrowa, wagowa
- Dotyczy uszlachetnień i obróbki wykończeniowej
- Pełna kompatybilność wsteczna

---

## ⚡ SZYBKI START

```bash
cd backend
python3 app.py
```

Aplikacja uruchomi się na: **http://127.0.0.1:7018**

---

### 🔒 HTTPS (opcjonalnie)

Aby uruchomić aplikację z własnym certyfikatem SSL:

```bash
mkdir -p cert
cp /ścieżka/do/twojego_certyfikatu.pem cert/cert.pem
cp /ścieżka/do/twojego_klucza.pem cert/key.pem

export FLASK_SSL_CERT="$(pwd)/cert/cert.pem"
export FLASK_SSL_KEY="$(pwd)/cert/key.pem"
python3 backend/app.py
```

> 🔐 **Ważne:** zarówno certyfikat, jak i klucz muszą być w formacie `.pem`.

Jeśli obie zmienne są ustawione i wskazują na istniejące pliki `.pem`, serwer będzie dostępny pod adresem **https://127.0.0.1:7018**.

---

## 📂 STRUKTURA PROJEKTU

```
kalkulator_v1.3_clean/
├── backend/               # Logika aplikacji
│   ├── app.py
│   ├── kalkulator_druku_v2.py     # ← Nowe: cięcie + jednostki
│   ├── slowniki_manager.py        # ← Nowe: manager cięcia
│   ├── slowniki_adapter.py
│   ├── slowniki_danych.py
│   ├── historia_manager.py
│   ├── kontrahenci_manager.py
│   └── biala_lista_vat.py
│
├── frontend/              # Interfejs użytkownika
│   └── templates/
│       ├── index.html             # ← Nowe: checkbox cięcia
│       ├── slowniki.html          # ← Nowe: zakładka cięcia
│       ├── historia.html
│       ├── kontrahenci.html
│       └── base.html
│
├── data/                  # Bazy danych
│   ├── slowniki_data.json         # ← Nowe: ciecie_papieru + typ_jednostki
│   ├── historia_ofert.json
│   └── kontrahenci.json
│
└── docs/                  # Dokumentacja
    └── VERSION_V1.3.txt           # ← Nowe: informacje o wersji
```

---

## 🔧 WYMAGANIA

- Python 3.7+
- Flask >= 2.0.0
- requests >= 2.28.0

```bash
pip install -r requirements.txt
```

---

## ✨ JAK UŻYWAĆ NOWYCH FEATURES

### Cięcie Papieru:
1. Formularz → Zaznacz: ☑️ "Papier wymaga cięcia z B1"
2. Wyślij formularz
3. Koszt cięcia pojawi się w wynikach

### Konfiguracja Cięcia:
- Słowniki → Cięcie Papieru
- Edytuj: roboczogodzina, wydajność, koszt przygotowania

### Elastyczne Jednostki:
- Słowniki → Uszlachetnienia (lub Obróbka)
- Kliknij "Edytuj"
- Wybierz typ jednostki: Sztukowa / Metrowa / Wagowa

---

## 🆚 HISTORIA WERSJI

- **v1.0** - Podstawowy kalkulator
- **v1.1** - Historia ofert
- **v1.2** - Kontrahenci + Biała Lista VAT
- **v1.3** - Cięcie papieru + Elastyczne jednostki ✨

---

## 📖 DOKUMENTACJA

Pełna dokumentacja znajduje się w folderze `docs/`:
- `VERSION_V1.3.txt` - Szczegóły wersji 1.3
- `INSTRUKCJA_UZYTKOWNIKA_V1.2.md` - Instrukcja użytkownika
- `IMPLEMENTACJA_V1.2_PODSUMOWANIE.md` - Historia implementacji

---

**© 2025 - Kalkulator Druku Offsetowego v1.3**
