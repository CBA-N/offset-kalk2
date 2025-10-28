# Logika Cenowa Kalkulatora Druku Offsetowego - Równania Matematyczne

## 📊 Pełny Model Kalkulacji Ceny

### Wzór Główny - Cena Finalna

```
CENA_BRUTTO = (SUMA_KOSZTÓW_NETTO × (1 + MARŻA/100)) × 1.23
```

**Gdzie:**
```
SUMA_KOSZTÓW_NETTO = K_papier + K_druk + K_kolory_spec + K_uszlachetnienia + K_obróbka + K_pakowanie + K_transport
```

---

## 🧮 KROK 1: Optymalizacja Formatu Arkusza

### 1.1. Obliczanie użytków na arkuszu

**Dane wejściowe:**
- `(W_w, H_w)` = format wydruku [mm]
- `(W_a, H_a)` = format arkusza [mm]
- `margines = 10` mm (techniczny, 5mm z każdej strony)

**Powierzchnia użyteczna arkusza:**
```
W_a_użyteczna = W_a - margines
H_a_użyteczna = H_a - margines
```

**Orientacja pionowa wydruku:**
```
użytki_pion_x = ⌊W_a_użyteczna / W_w⌋
użytki_pion_y = ⌊H_a_użyteczna / H_w⌋
użytki_pion = użytki_pion_x × użytki_pion_y
```

**Orientacja pozioma wydruku (obrót 90°):**
```
użytki_poziom_x = ⌊W_a_użyteczna / H_w⌋
użytki_poziom_y = ⌊H_a_użyteczna / W_w⌋
użytki_poziom = użytki_poziom_x × użytki_poziom_y
```

**Wybór lepszej orientacji:**
```
użytki = max(użytki_pion, użytki_poziom)
orientacja = { 'pionowa'  jeśli użytki_pion ≥ użytki_poziom
             { 'pozioma'  w przeciwnym razie
```

### 1.2. Wykorzystanie i odpady arkusza

**Powierzchnie [m²]:**
```
P_arkusza = (W_a × H_a) / 1_000_000
P_użytku = (W_w × H_w) / 1_000_000  (lub (H_w × W_w) jeśli pozioma)
P_wykorzystana = użytki × P_użytku
```

**Wskaźniki procentowe:**
```
wykorzystanie% = (P_wykorzystana / P_arkusza) × 100
odpady% = 100 - wykorzystanie%
```

### 1.3. Liczba arkuszy potrzebnych

**Podstawowa liczba arkuszy:**
```
n_arkuszy_min = ⌈nakład / użytki⌉
```

**Z zapasem na odpady technologiczne (10%):**
```
n_arkuszy = ⌈n_arkuszy_min × 1.1⌉
```

### 1.4. Scoring formatów (optymalizacja)

**Normalizacja parametrów do zakresu [0, 1]:**
```
norm_odpady = 1 - (odpady% / 100)
norm_koszt = 1 / (koszt_papieru / 1000 + 1)
norm_czas = 1 / (czas_produkcji_h + 1)
```

**Wynik formatowania wg priorytetu:**
```
score = norm_odpady × waga_odpady + norm_koszt × waga_koszt + norm_czas × waga_czas
```

**Wagi priorytetów:**
| Priorytet            | waga_odpady | waga_koszt | waga_czas |
|---------------------|-------------|------------|-----------|
| Najniższy koszt     | 0.2         | 0.7        | 0.1       |
| Najmniej odpadów    | 0.7         | 0.2        | 0.1       |
| Najszybsza produkcja| 0.2         | 0.1        | 0.7       |
| Zrównoważony        | 0.4         | 0.3        | 0.3       |

**Wybór formatu:**
```
format_wybrany = argmax(score) dla wszystkich formatów
```

---

## 💵 KROK 2: Koszt Papieru

### 2.1. Waga i koszt arkusza

**Dane:**
- `P_arkusza` = powierzchnia arkusza [m²]
- `gramatura` = gramatura papieru [g/m²]
- `cena_kg` = cena papieru [PLN/kg]
- `n_arkuszy` = liczba arkuszy (z odpadami)

**Wzory:**
```
waga_arkusza = P_arkusza × (gramatura / 1000)  [kg]

K_papier = n_arkuszy × waga_arkusza × cena_kg  [PLN]
```

**Alternatywnie (rozwiniecie):**
```
K_papier = n_arkuszy × (W_a × H_a / 1_000_000) × (gramatura / 1000) × cena_kg
```

---

## 🖨️ KROK 3: Koszt Druku

### 3.1. Składniki kosztu druku

```
K_druk = K_przygotowanie + K_formy + K_przeloty
```

### 3.2. Przygotowanie maszyny

**Dane:**
- `czas_przygotowania = 1.0` h (standard)
- `R_przygotowanie` = roboczogodzina przygotowania [PLN/h]

```
K_przygotowanie = czas_przygotowania × R_przygotowanie
```

### 3.3. Formy drukowe

**Dane:**
- `n_form` = liczba form drukowych (domyślnie 4 dla CMYK)
- `cena_formy` = koszt jednej formy [PLN/forma]

```
K_formy = n_form × cena_formy
```

### 3.4. Przeloty maszyny

**Liczba przelotów w zależności od kolorystyki:**
```
przeloty = { n_arkuszy       dla '4+0' (jednostronny)
           { n_arkuszy × 2   dla '4+4' (dwustronny)
           { n_arkuszy × 1.25 dla '4+1' (4 kolory + 1 kolor czarny)
```

**Koszt przelotów:**
```
K_przeloty = (przeloty / 1000) × stawka_1000_arkuszy
```

### 3.5. Czas produkcji druku

```
czas_druku = czas_przygotowania + (n_arkuszy / szybkość_druku_arkuszy_h)
```

**Przykładowe wartości:**
- `szybkość_druku_arkuszy_h = 3000` arkuszy/h

---

## 🎨 KROK 4: Kolory Specjalne (Pantone/Spot)

### 4.1. Koszt kolorów specjalnych

**Dla każdego koloru specjalnego:**
```
K_kolor_i = koszt_za_kolor + koszt_preparatu + (czas_przygotowania_min / 60) × R_godzinowa
```

**Całkowity koszt kolorów specjalnych:**
```
K_kolory_spec = Σ K_kolor_i  dla i=1 do liczba_kolorów_spec
```

**Czas przygotowania kolorów:**
```
czas_kolory = Σ (czas_przygotowania_min_i / 60)  [h]
```

---

## ✨ KROK 5: Uszlachetnienia

### 5.1. Koszt uszlachetnienia

**Dla każdego uszlachetnienia (np. folia mat, lakier UV):**

**Typ 1: Uszlachetnienie za m²**
```
K_uszlachetnienie_i = n_arkuszy × P_arkusza × cena_za_m2
```

**Typ 2: Z matrycą**
```
K_uszlachetnienie_i = n_arkuszy × P_arkusza × cena_za_m2 + koszt_matrycy
```

**Całkowity koszt uszlachetnienia:**
```
K_uszlachetnienia = Σ K_uszlachetnienie_i  dla wszystkich uszlachetnień
```

**Czas przygotowania:**
```
czas_uszlachetnienia = Σ (czas_przygotowania_min_i / 60)  [h]
```

---

## 🔧 KROK 6: Obróbka Wykończeniowa

### 6.1. Typy obróbki

**Typ A: Obróbka arkuszowa** (np. cięcie)
```
czas_operacji = nakład / wydajność_arkuszy_h  [h]
K_obróbka = czas_operacji × stawka_godzinowa + koszt_przygotowania
```

**Typ B: Obróbka sztukowa** (np. oprawa)

**Wariant 1: Koszt za sztukę**
```
K_obróbka = nakład × koszt_za_sztuke + koszt_przygotowania
```

**Wariant 2: Czas za sztukę**
```
czas_operacji = nakład / wydajność_sztuk_h  [h]
K_obróbka = czas_operacji × stawka_godzinowa + koszt_przygotowania
```

### 6.2. Całkowity koszt obróbki

```
K_obróbka = Σ K_obróbka_i  dla wszystkich operacji obróbki
```

**Całkowity czas obróbki:**
```
czas_obróbki = Σ czas_operacji_i  [h]
```

---

## 📦 KROK 7: Pakowanie i Transport

### 7.1. Koszt pakowania

**Stałe ceny w zależności od opcji:**
```
K_pakowanie = cena_pakowania[rodzaj]
```

**Przykłady:**
- Folia stretch (standard): 50 PLN
- Karton + folia: 120 PLN
- Paleta EUR + folia: 250 PLN

### 7.2. Koszt transportu

**Stałe ceny w zależności od opcji:**
```
K_transport = cena_transportu[rodzaj]
```

**Przykłady:**
- Odbiór własny: 0 PLN
- Kurier standardowy (do 30 kg): 30 PLN
- Kurier standardowy (30-50 kg): 50 PLN
- Transport dedykowany (50-500 kg): 150 PLN

**Czas dostawy:**
```
czas_transportu = czas_dni[rodzaj]  [dni]
```

---

## 💰 KROK 8: Suma Kosztów Netto

### 8.1. Agregacja wszystkich kosztów

```
SUMA_KOSZTÓW_NETTO = K_papier 
                    + K_druk 
                    + K_kolory_spec 
                    + K_uszlachetnienia 
                    + K_obróbka 
                    + K_pakowanie 
                    + K_transport
```

**Rozwiniecie pełne:**
```
SUMA_KOSZTÓW_NETTO = 
    [n_arkuszy × waga_arkusza × cena_kg]                          // Papier
  + [K_przygotowanie + K_formy + K_przeloty]                      // Druk
  + [Σ(koszt_kolor_i + koszt_preparatu_i)]                       // Kolory spec
  + [Σ(n_arkuszy × P_arkusza × cena_m2_i + koszt_matrycy_i)]    // Uszlachetnienia
  + [Σ(czas_i × stawka_i + przygotowanie_i)]                     // Obróbka
  + [cena_pakowania]                                               // Pakowanie
  + [cena_transportu]                                              // Transport
```

---

## 📈 KROK 9: Marża

### 9.1. Cena z marżą (netto)

**Dane:**
- `marża%` = marża procentowa (np. 20%)

```
CENA_Z_MARŻĄ_NETTO = SUMA_KOSZTÓW_NETTO × (1 + marża% / 100)
```

**Kwota marży:**
```
kwota_marży = CENA_Z_MARŻĄ_NETTO - SUMA_KOSZTÓW_NETTO
            = SUMA_KOSZTÓW_NETTO × (marża% / 100)
```

---

## 💳 KROK 10: VAT

### 10.1. Cena brutto (z VAT 23%)

```
CENA_BRUTTO = CENA_Z_MARŻĄ_NETTO × 1.23
```

**Kwota VAT:**
```
kwota_VAT = CENA_BRUTTO - CENA_Z_MARŻĄ_NETTO
          = CENA_Z_MARŻĄ_NETTO × 0.23
```

---

## ⏱️ KROK 11: Czas Realizacji

### 11.1. Całkowity czas produkcji

```
CZAS_REALIZACJI = czas_przygotowanie_druku
                + czas_druku
                + czas_kolory_spec
                + czas_uszlachetnienia
                + czas_obróbki
```

**Rozwiniecie:**
```
CZAS_REALIZACJI = 1.0  // przygotowanie standard
                + (n_arkuszy / szybkość_druku)
                + Σ(czas_kolor_i / 60)
                + Σ(czas_uszlachetnienie_i / 60)
                + Σ(nakład / wydajność_obróbki_i)   [godziny]
```

**Czas dostawy (osobno):**
```
czas_dostawy = czas_transportu_dni  [dni]
```

---

## ⚖️ KROK 12: Waga Produktu

### 12.1. Całkowita waga zlecenia

```
WAGA = n_arkuszy × P_arkusza × (gramatura / 1000)  [kg]
```

**Rozwiniecie:**
```
WAGA = n_arkuszy × (W_a × H_a / 1_000_000) × (gramatura / 1000)  [kg]
```

---

## 📐 PRZYKŁAD NUMERYCZNY

### Dane wejściowe:
- **Produkt:** Plakat A2 (420×594 mm)
- **Nakład:** 2000 szt
- **Papier:** Kreda błysk 150 g/m²
- **Kolorystyka:** 4+0 (jednostronny CMYK)
- **Uszlachetnienia:** Folia mat
- **Obróbka:** Cięcie formatowe
- **Pakowanie:** Karton + folia
- **Transport:** Kurier standardowy (30-50 kg)
- **Marża:** 20%

### Krok 1: Optymalizacja formatu

**Wybrany format:** B1 (700×1000 mm)

**Użytki:**
```
W_a_użyteczna = 700 - 10 = 690 mm
H_a_użyteczna = 1000 - 10 = 990 mm

użytki_pion_x = ⌊690 / 420⌋ = 1
użytki_pion_y = ⌊990 / 594⌋ = 1
użytki_pion = 1 × 1 = 1

użytki_poziom_x = ⌊690 / 594⌋ = 1
użytki_poziom_y = ⌊990 / 420⌋ = 2
użytki_poziom = 1 × 2 = 2 ✅ (lepsze!)

użytki = 2 (orientacja pozioma)
```

**Liczba arkuszy:**
```
n_arkuszy_min = ⌈2000 / 2⌉ = 1000
n_arkuszy = ⌈1000 × 1.1⌉ = 1100 arkuszy
```

**Powierzchnia i wykorzystanie:**
```
P_arkusza = (700 × 1000) / 1_000_000 = 0.7 m²
P_użytku = (420 × 594) / 1_000_000 = 0.24948 m²
P_wykorzystana = 2 × 0.24948 = 0.49896 m²

wykorzystanie% = (0.49896 / 0.7) × 100 = 71.3%
odpady% = 100 - 71.3 = 28.7%
```

### Krok 2: Koszt papieru

**Założenia:**
- Cena kredy błysk 150g: 4.50 PLN/kg

```
waga_arkusza = 0.7 × (150 / 1000) = 0.105 kg
K_papier = 1100 × 0.105 × 4.50 = 519.75 PLN
```

### Krok 3: Koszt druku

**Założenia:**
- R_przygotowanie = 150 PLN/h
- cena_formy = 80 PLN/forma
- n_form = 4 (CMYK)
- stawka_1000_ark = 200 PLN
- szybkość_druku = 3000 ark/h

```
K_przygotowanie = 1.0 × 150 = 150 PLN
K_formy = 4 × 80 = 320 PLN

przeloty = 1100  (dla 4+0)
K_przeloty = (1100 / 1000) × 200 = 220 PLN

K_druk = 150 + 320 + 220 = 690 PLN

czas_druku = 1.0 + (1100 / 3000) = 1.37 h
```

### Krok 4: Kolory specjalne

```
K_kolory_spec = 0 PLN  (brak kolorów specjalnych)
```

### Krok 5: Uszlachetnienia

**Folia mat:**
- Cena: 2.50 PLN/m²
- Koszt matrycy: 0 PLN

```
K_uszlachetnienia = 1100 × 0.7 × 2.50 = 1925 PLN

czas_uszlachetnienia = 45 / 60 = 0.75 h
```

### Krok 6: Obróbka

**Cięcie formatowe:**
- Wydajność: 1500 ark/h
- Stawka: 100 PLN/h
- Przygotowanie: 30 PLN

```
czas_operacji = 2000 / 1500 = 1.33 h
K_obróbka = 1.33 × 100 + 30 = 163 PLN
```

### Krok 7: Pakowanie i transport

```
K_pakowanie = 120 PLN  (karton + folia)
K_transport = 50 PLN   (kurier 30-50 kg)
```

### Krok 8: Suma kosztów netto

```
SUMA_KOSZTÓW_NETTO = 519.75 + 690 + 0 + 1925 + 163 + 120 + 50
                    = 3467.75 PLN
```

### Krok 9: Marża

```
CENA_Z_MARŻĄ_NETTO = 3467.75 × 1.20 = 4161.30 PLN
kwota_marży = 4161.30 - 3467.75 = 693.55 PLN
```

### Krok 10: VAT

```
CENA_BRUTTO = 4161.30 × 1.23 = 5118.40 PLN
kwota_VAT = 5118.40 - 4161.30 = 957.10 PLN
```

### Krok 11: Czas realizacji

```
CZAS_REALIZACJI = 1.0 + 1.37 + 0 + 0.75 + 1.33 = 4.45 h
```

### Krok 12: Waga

```
WAGA = 1100 × 0.7 × 0.15 = 115.5 kg
```

---

## 📋 PODSUMOWANIE WZORÓW - QUICK REFERENCE

### Wzór Master (Cena Finalna)
```
CENA_BRUTTO = (K_papier + K_druk + K_kolory + K_uszlach + K_obróbka + K_pak + K_trans) × (1 + m/100) × 1.23
```

### Kluczowe Równania

**1. Użytki na arkuszu:**
```
użytki = max(⌊W_a_użyt / W_w⌋ × ⌊H_a_użyt / H_w⌋,  
             ⌊W_a_użyt / H_w⌋ × ⌊H_a_użyt / W_w⌋)
```

**2. Liczba arkuszy:**
```
n_arkuszy = ⌈(⌈nakład / użytki⌉) × 1.1⌉
```

**3. Koszt papieru:**
```
K_papier = n_arkuszy × (W_a × H_a / 10⁶) × (gramatura / 1000) × cena_kg
```

**4. Koszt druku:**
```
K_druk = (czas_przygot × R_h) + (n_form × cena_formy) + (przeloty/1000 × stawka_1000)
```

**5. Czas realizacji:**
```
T = t_przygot + n_ark/v_druku + Σt_uszlach + Σ(nakład/v_obróbka)
```

**6. Waga:**
```
W = n_arkuszy × P_arkusza × gramatura/1000
```

---

## 🔬 Zmienne i Stałe

### Zmienne wejściowe
- `W_w, H_w` - wymiary wydruku [mm]
- `nakład` - liczba sztuk
- `gramatura` - gramatura papieru [g/m²]
- `marża%` - marża procentowa

### Parametry słowników
- `cena_kg` - cena papieru [PLN/kg]
- `R_przygotowanie` - stawka przygotowania [PLN/h]
- `cena_formy` - koszt formy drukowej [PLN/forma]
- `stawka_1000_ark` - stawka druku [PLN/1000 ark]
- `szybkość_druku` - wydajność maszyny [ark/h]

### Stałe techniczne
- `margines = 10` mm
- `odpady_technologiczne = 1.1` (10%)
- `VAT = 1.23` (23%)

---

**Dokument wygenerowany:** 2024-10-17  
**Wersja kalkulatora:** v1.2.1  
**Plik źródłowy:** `backend/kalkulator_druku_v2.py`
