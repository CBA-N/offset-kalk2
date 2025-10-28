# 📖 Instrukcja Użytkownika - Kalkulator Druku v1.2

## 🎯 Moduł Kontrahentów - Przewodnik Użytkownika

---

## 📚 Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Zarządzanie Kontrahentami](#zarządzanie-kontrahentami)
3. [Pobieranie Danych z Białej Listy VAT](#pobieranie-danych-z-białej-listy-vat)
4. [Kalkulacja Oferty z Kontrahentem](#kalkulacja-oferty-z-kontrahentem)
5. [Historia Ofert](#historia-ofert)
6. [FAQ](#faq)

---

## 1. Wprowadzenie

### Co nowego w v1.2?

Wersja 1.2 wprowadza **system zarządzania kontrahentami**, który pozwala:

✅ Przechowywać dane kontrahentów (nazwa, NIP, adres, kontakt)  
✅ Automatycznie pobierać dane firm z rejestru VAT  
✅ Powiązać oferty z konkretnymi kontrahentami  
✅ Śledzić historię współpracy  

### Dostęp do modułu

Kliknij **"Kontrahenci"** w menu górnym:

```
[Kalkulator] [Słowniki] [Historia] [Kontrahenci] ← TUTAJ
```

---

## 2. Zarządzanie Kontrahentami

### 2.1. Strona Główna Kontrahentów

Po wejściu na `/kontrahenci` zobaczysz:

#### A) Statystyki (4 karty na górze)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 📊 Wszyscy │ ✅ Z NIP    │ ❌ Bez NIP  │ 🌍 Miasta   │
│     3       │     3       │     0       │     3       │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### B) Wyszukiwanie i Filtry
```
[🔍 Szukaj...] [Województwo ▼] [Sortowanie ▼] [+ Nowy] [🗑️ Wyczyść]
```

#### C) Tabela Kontrahentów
```
ID | Nazwa              | NIP            | Miasto   | Email           | Akcje
───┼────────────────────┼────────────────┼──────────┼─────────────────┼──────
1  | Drukarnia TEST     | 123-456-32-18  | Warszawa | kontakt@...     | 👁️📝🗑️
2  | Wydawnictwo DEMO   | 987-654-32-10  | Kraków   | biuro@...       | 👁️📝🗑️
```

**Legenda akcji:**
- 👁️ **Szczegóły** - wyświetl pełne dane kontrahenta
- 📝 **Edytuj** - modyfikuj dane
- 🗑️ **Usuń** - usuń kontrahenta (wymaga potwierdzenia)

---

### 2.2. Dodawanie Nowego Kontrahenta

#### Metoda 1: Ręczne Wprowadzanie

1. Kliknij przycisk **[+ Nowy kontrahent]**
2. Wypełnij formularz:

**DANE PODSTAWOWE (wymagane: nazwa)**
```
Nazwa firmy*:     [_________________________]
NIP:              [___-___-__-__]
REGON:            [_________]
KRS:              [__________]
Forma prawna:     [Sp. z o.o. ▼]
```

**ADRES**
```
Ulica:            [_________________________]
Kod pocztowy:     [__-___]
Miasto:           [_________________________]
Województwo:      [mazowieckie ▼]
```

**KONTAKT**
```
Email:            [@________________________]
Telefon:          [+48 __ ___ __ __]
Osoba kontaktowa: [_________________________]
Uwagi:            [_________________________]
```

3. Kliknij **[💾 Zapisz]**
4. Kontrahent zostanie dodany do bazy

---

#### Metoda 2: Pobieranie z Białej Listy VAT ⭐ NOWOŚĆ

**Znacznie szybsza!** System automatycznie pobierze wszystkie dane po NIP.

1. Kliknij **[+ Nowy kontrahent]**
2. Wpisz **tylko NIP** (10 cyfr lub z myślnikami)
   ```
   NIP: [123-456-32-18]
   ```
3. Kliknij **[🔄 Pobierz z VAT]** obok pola NIP
4. **Poczekaj 2-5 sekund** (pojawi się spinner ⏳)
5. System automatycznie wypełni:
   - ✅ Nazwa firmy
   - ✅ REGON
   - ✅ KRS (jeśli dostępny)
   - ✅ Forma prawna
   - ✅ Pełny adres (ulica, kod, miasto, województwo)
   - ✅ Status VAT
   - ✅ Konta bankowe (w uwagach)
6. **Uzupełnij tylko dane kontaktowe:**
   - Email
   - Telefon
   - Osoba kontaktowa
7. Kliknij **[💾 Zapisz]**

**Przykład:**
```
Wpisujesz:        1234563218
System pobiera:   
  ✓ Nazwa:        "ACME PRINTING Sp. z o.o."
  ✓ REGON:        "123456789"
  ✓ Adres:        "ul. Główna 10, 00-001 Warszawa"
  ✓ Województwo:  "mazowieckie"
  ✓ Forma prawna: "Sp. z o.o."
```

---

### 2.3. Edycja Kontrahenta

1. Znajdź kontrahenta w tabeli
2. Kliknij ikonę **📝 Edytuj**
3. Modal otworzy się z wypełnionymi danymi
4. Zmień wybrane pola
5. Kliknij **[💾 Zapisz]**
6. Data "Ostatnia modyfikacja" zostanie zaktualizowana

**Uwaga:** Możesz ponownie użyć **[🔄 Pobierz z VAT]** aby zaktualizować dane z rejestru.

---

### 2.4. Szczegóły Kontrahenta

1. Kliknij ikonę **👁️ Szczegóły**
2. Zobaczysz wszystkie dane w trybie readonly:
   ```
   ┌─ Szczegóły Kontrahenta ─────────────────────┐
   │                                              │
   │  ID: 1                                       │
   │  Nazwa: Drukarnia TEST Sp. z o.o.            │
   │  NIP: 123-456-32-18                          │
   │  REGON: 123456789                            │
   │  KRS: 0000123456                             │
   │  Forma prawna: Sp. z o.o.                    │
   │                                              │
   │  === Adres ===                               │
   │  ul. Przykładowa 10                          │
   │  00-001 Warszawa                             │
   │  Województwo: mazowieckie                    │
   │                                              │
   │  === Kontakt ===                             │
   │  Email: kontakt@drukarnia-test.pl            │
   │  Telefon: +48 22 123 45 67                   │
   │  Osoba kontaktowa: Jan Kowalski              │
   │                                              │
   │  === Uwagi ===                               │
   │  Stały klient - rabat 10%                    │
   │                                              │
   │  === Metadata ===                            │
   │  Data dodania: 2025-10-17 10:30              │
   │  Ostatnia modyfikacja: 2025-10-17 10:30      │
   │                                              │
   │  [Edytuj] [Zamknij]                          │
   └──────────────────────────────────────────────┘
   ```

---

### 2.5. Usuwanie Kontrahenta

1. Kliknij ikonę **🗑️ Usuń**
2. Pojawi się komunikat potwierdzenia:
   ```
   ⚠️ Czy na pewno usunąć kontrahenta "Drukarnia TEST"?
   
   [Anuluj] [Usuń]
   ```
3. Kliknij **[Usuń]** aby potwierdzić
4. Kontrahent zostanie usunięty z bazy

**Uwaga:** Usunięcie kontrahenta **NIE** usuwa ofert, które były z nim powiązane. Dane kontrahenta są zapisane w ofercie jako kopia.

---

### 2.6. Wyszukiwanie Kontrahentów

#### Wyszukiwanie tekstowe
```
[🔍 Szukaj po nazwie, NIP, mieście, email...]
```

**Wpisz np.:**
- `TEST` → znajdzie "Drukarnia TEST"
- `123` → znajdzie NIP "123-456-32-18"
- `Warszawa` → znajdzie wszystkich z Warszawy
- `kontakt@` → znajdzie email "kontakt@drukarnia-test.pl"

**Wyniki są filtrowane na żywo** (dynamicznie podczas pisania).

#### Filtrowanie po województwie
```
[Województwo ▼]
  - Wszystkie
  - mazowieckie
  - małopolskie
  - wielkopolskie
  ...
```

#### Sortowanie
```
[Sortowanie ▼]
  - Alfabetycznie A-Z
  - Alfabetycznie Z-A
  - Najnowsze
  - Najstarsze
  - Po NIP rosnąco
```

---

## 3. Pobieranie Danych z Białej Listy VAT

### 3.1. Czym jest Biała Lista VAT?

**Biała Lista VAT** to oficjalny rejestr Ministerstwa Finansów zawierający:
- Wszystkie firmy zarejestrowane jako podatnicy VAT w Polsce
- Aktualny status VAT (aktywny/nieaktywny)
- Pełne dane rejestrowe (nazwa, NIP, REGON, KRS)
- Adres siedziby
- Zweryfikowane numery kont bankowych

### 3.2. Jak Korzystać?

**Krok 1:** Wejdź w dodawanie/edycję kontrahenta  
**Krok 2:** Wpisz NIP w formacie:
- `1234563218` (10 cyfr)
- `123-456-32-18` (z myślnikami)
- `123 456 32 18` (ze spacjami)

**Krok 3:** Kliknij **[🔄 Pobierz z VAT]**

**Krok 4:** Poczekaj na spinner ⏳ (2-5 sekund)

**Krok 5:** Dane zostaną automatycznie wypełnione!

### 3.3. Co Zostanie Pobrane?

| Pole | Przykład |
|------|----------|
| **Nazwa** | "ACME PRINTING Spółka z ograniczoną odpowiedzialnością" |
| **NIP** | "1234563218" |
| **REGON** | "123456789" |
| **KRS** | "0000123456" |
| **Forma prawna** | "Sp. z o.o." (automatyczna detekcja) |
| **Ulica** | "ul. Główna 10" |
| **Kod pocztowy** | "00-001" |
| **Miasto** | "Warszawa" |
| **Województwo** | "mazowieckie" (wyliczone z kodu) |
| **Status VAT** | "Aktywny" (w uwagach) |
| **Konta bankowe** | Lista kont (w uwagach) |

### 3.4. Obsługa Błędów

#### Błąd: "NIP nie znaleziony w rejestrze VAT"
**Przyczyny:**
- NIP nie istnieje w bazie MF
- Firma wykreślona z rejestru VAT
- Błędnie wpisany NIP

**Rozwiązanie:**
1. Sprawdź poprawność NIP
2. Zweryfikuj NIP na stronie MF: https://www.podatki.gov.pl/wykaz-podatnikow-vat
3. Wprowadź dane ręcznie

#### Błąd: "Błąd połączenia z API"
**Przyczyny:**
- Brak internetu
- API MF tymczasowo niedostępne
- Timeout połączenia

**Rozwiązanie:**
1. Sprawdź połączenie internetowe
2. Spróbuj ponownie za chwilę
3. W ostateczności wprowadź dane ręcznie

#### Błąd: "Nieprawidłowa suma kontrolna NIP"
**Przyczyny:**
- Błędnie przepisany NIP
- Literówka w numerze

**Rozwiązanie:**
1. Sprawdź NIP ponownie (cyfra po cyfrze)
2. System waliduje NIP algorytmem sumy kontrolnej
3. NIP musi spełniać matematyczne kryteria

---

## 4. Kalkulacja Oferty z Kontrahentem

### 4.1. Wybór Kontrahenta w Kalkulatorze

1. Wejdź na stronę główną **[Kalkulator]**
2. Znajdź sekcję **"Kontrahent (opcjonalnie)"** (przed sekcją Materiał):
   ```
   ┌─ Kontrahent (opcjonalnie) ──────────────────┐
   │                                              │
   │  Wybierz kontrahenta:                        │
   │  [-- Bez kontrahenta -- ▼]                   │
   │                                              │
   │  [📋 Zarządzaj kontrahentami]                │
   └──────────────────────────────────────────────┘
   ```

3. Rozwiń dropdown i wybierz kontrahenta:
   ```
   [Wybierz kontrahenta... ▼]
     - Bez kontrahenta
     - Drukarnia TEST (123-456-32-18)
     - Wydawnictwo DEMO (987-654-32-10)
     - ABC Print House (555-555-55-55)
   ```

4. **Po wyborze** zobaczysz podgląd:
   ```
   ✓ Wybrany kontrahent:
   
   Nazwa:    Wydawnictwo DEMO
   NIP:      987-654-32-10
   Miasto:   Kraków
   Email:    biuro@wydawnictwo-demo.pl
   Telefon:  +48 12 987 65 43
   ```

5. Wypełnij resztę formularza jak zwykle
6. Kliknij **[Oblicz Cenę]**

### 4.2. Kalkulacja Bez Kontrahenta

Możesz pominąć wybór kontrahenta - system zadziała normalnie:
```
[-- Bez kontrahenta --]
↓
Oferta utworzona bez powiązania z kontrahentem
```

### 4.3. Dodanie Kontrahenta Podczas Kalkulacji

Jeśli kontrahenta nie ma w bazie:
1. Kliknij **[📋 Zarządzaj kontrahentami]** (otworzy się w nowej karcie)
2. Dodaj kontrahenta (patrz sekcja 2.2)
3. Wróć do karty z kalkulatorem
4. **Odśwież dropdown** (lub przeładuj stronę F5)
5. Nowy kontrahent pojawi się na liście

---

## 5. Historia Ofert

### 5.1. Wyświetlanie Kontrahenta w Ofercie

**W liście ofert** zobaczysz badge kontrahenta:
```
┌─ Oferta #4 ────────────────────────────────────┐
│                                                 │
│  📄 Oferta #4                                   │
│  A5 | 1000 szt | Kreda mat                      │
│                                                 │
│  [ℹ️ Wydawnictwo DEMO] ← BADGE KONTRAHENTA     │
│                                                 │
│  🕐 2025-10-17 22:33                            │
│  💰 448.97 PLN                                  │
│                                                 │
│  [Szczegóły] [Duplikuj] [Usuń]                 │
└─────────────────────────────────────────────────┘
```

### 5.2. Szczegóły Oferty z Kontrahentem

Po kliknięciu **[Szczegóły]**:
```
┌─ Szczegóły Oferty ──────────────────────────────┐
│                                                  │
│  Oferta #4 [v1.2]                                │
│  Data: 2025-10-17 22:33                          │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ ℹ️ Kontrahent:                           │   │
│  │                                          │   │
│  │  Nazwa:    Wydawnictwo DEMO              │   │
│  │  NIP:      987-654-32-10                 │   │
│  │  Adres:    ul. Testowa 5                 │   │
│  │            31-000 Kraków                 │   │
│  │  Email:    biuro@wydawnictwo-demo.pl     │   │
│  │  Telefon:  +48 12 987 65 43              │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  === Dane podstawowe ===                         │
│  Format: 148 × 210 mm                            │
│  Nakład: 1000 szt                                │
│  Papier: Kreda mat 170g                          │
│  ...                                             │
│                                                  │
│  === Kalkulacja kosztów ===                      │
│  ...                                             │
│                                                  │
│  [Zamknij] [Drukuj]                              │
└──────────────────────────────────────────────────┘
```

### 5.3. Duplikowanie Oferty z Kontrahentem

**Funkcja duplikowania zachowuje kontrahenta!**

1. W historii kliknij **[Duplikuj]** przy ofercie #4
2. Zostaniesz przekierowany do kalkulatora
3. **Wszystkie pola będą wypełnione**, w tym:
   - ✅ Wszystkie parametry produktu
   - ✅ **Wybrany kontrahent** (Wydawnictwo DEMO)
4. Możesz:
   - Zmienić parametry
   - Zmienić kontrahenta
   - Lub zostawić jak jest
5. Kliknij **[Oblicz Cenę]**
6. Zostanie utworzona nowa oferta z tymi samymi danymi

**Przykład użycia:**
```
Oferta #4: Ulotki A5, 1000 szt, dla Wydawnictwa DEMO
           ↓ [Duplikuj]
Oferta #5: Ulotki A5, 2000 szt, dla Wydawnictwa DEMO ← zmieniony nakład
```

---

## 6. FAQ

### Ogólne

**Q: Czy muszę dodawać kontrahentów?**  
A: Nie, to opcjonalne. System działa normalnie bez kontrahentów.

**Q: Czy mogę edytować dane kontrahenta później?**  
A: Tak, w dowolnym momencie. Edycja NIE wpłynie na stare oferty (są tam kopie danych).

**Q: Czy mogę usunąć kontrahenta?**  
A: Tak, ale oferty z tym kontrahentem pozostaną (mają kopię danych).

---

### Biała Lista VAT

**Q: Czy potrzebuję konta w API VAT?**  
A: Nie, API jest darmowe i nie wymaga rejestracji.

**Q: Jak często dane w API VAT są aktualizowane?**  
A: Dane są aktualizowane codziennie przez Ministerstwo Finansów.

**Q: Co jeśli API VAT nie działa?**  
A: Możesz wprowadzić dane ręcznie. Spróbuj pobierania z VAT później.

**Q: Czy pobieranie z VAT nadpisze moje dane?**  
A: Tak, wszystkie pola zostaną nadpisane danymi z rejestru. Zapisz ważne informacje przed użyciem.

---

### Kalkulacja

**Q: Czy mogę zmienić kontrahenta w istniejącej ofercie?**  
A: Nie, oferty są niezmienne. Użyj funkcji **Duplikuj** i zmień kontrahenta w nowej ofercie.

**Q: Co się stanie jeśli usunę kontrahenta?**  
A: Nic. Oferty mają kopię danych kontrahenta, więc będą nadal poprawne.

**Q: Czy mogę dodać kontrahenta do starej oferty?**  
A: Nie bezpośrednio. Użyj **Duplikuj**, wybierz kontrahenta i utwórz nową ofertę.

---

### Dane

**Q: Gdzie są przechowywane dane kontrahentów?**  
A: W pliku `kontrahenci.json` w folderze aplikacji.

**Q: Czy mogę eksportować kontrahentów?**  
A: Obecnie nie (planowane w v1.3). Możesz skopiować plik `kontrahenci.json`.

**Q: Czy mogę importować kontrahentów z pliku?**  
A: Obecnie nie (planowane w v1.3).

---

### Bezpieczeństwo

**Q: Czy dane kontrahentów są bezpieczne?**  
A: Tak, dane są przechowywane lokalnie w pliku JSON. Brak dostępu z zewnątrz.

**Q: Czy mogę anonimizować dane (RODO)?**  
A: Tak, funkcja dostępna w API: `/api/kontrahenci/<id>/anonimizuj`

**Q: Czy system loguje historię zmian?**  
A: Obecnie tylko data ostatniej modyfikacji. Pełny audit log planowany w v1.3.

---

### Wsparcie

**Q: Gdzie zgłaszać błędy?**  
A: Skontaktuj się z administratorem systemu.

**Q: Czy będą kolejne wersje?**  
A: Tak! Planowana jest v1.3 z dodatkowymi funkcjami (eksport, raporty, etc.)

---

## 📞 Pomoc Techniczna

W razie problemów:
1. Sprawdź tę instrukcję
2. Sprawdź FAQ powyżej
3. Skontaktuj się z administratorem

---

**Miłego Korzystania!** 🎉

*Wersja dokumentacji: 1.2*  
*Data: 2025-10-17*
