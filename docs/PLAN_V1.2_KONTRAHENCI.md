# Plan v1.2 - System Kontrahentów z Integracją GUS

## Cel
Dodanie pełnego systemu zarządzania kontrahentami z automatycznym pobieraniem danych z bazy REGON/GUS.

---

## Funkcje do Zaimplementowania

### 1. Model Danych Kontrahenta

**Pola wymagane:**
- `id` - unikalny identyfikator
- `nazwa` - nazwa firmy/osoby
- `nip` - NIP (10 cyfr, opcjonalny dla osób fizycznych)
- `regon` - REGON (9 lub 14 cyfr, opcjonalny)
- `adres_ulica` - ulica i numer
- `adres_kod` - kod pocztowy
- `adres_miasto` - miasto
- `adres_wojewodztwo` - województwo (z GUS)
- `email` - email kontaktowy
- `telefon` - telefon
- `osoba_kontaktowa` - imię i nazwisko
- `uwagi` - notatki
- `data_dodania` - timestamp utworzenia
- `ostatnia_modyfikacja` - timestamp ostatniej edycji

**Pola dodatkowe z GUS:**
- `forma_prawna` - np. "Spółka z o.o.", "Jednoosobowa działalność"
- `pkd_glowny` - główny kod PKD
- `data_rejestracji` - data wpisu do REGON
- `status` - aktywny/zawieszony

---

### 2. Backend - Python

#### 2.1. Moduł `kontrahenci_manager.py`

```python
class KontrahenciManager:
    def __init__(self, plik_json='kontrahenci.json'):
        self.plik_json = plik_json
        self.kontrahenci = self._zaladuj()
    
    def dodaj_kontrahenta(self, dane: dict) -> dict:
        """Dodaj nowego kontrahenta"""
        
    def edytuj_kontrahenta(self, id: int, dane: dict) -> dict:
        """Edytuj istniejącego kontrahenta"""
        
    def usun_kontrahenta(self, id: int) -> bool:
        """Usuń kontrahenta"""
        
    def pobierz_kontrahenta(self, id: int) -> dict:
        """Pobierz kontrahenta po ID"""
        
    def pobierz_wszystkich(self) -> list:
        """Pobierz listę wszystkich kontrahentów"""
        
    def szukaj(self, fraza: str) -> list:
        """Wyszukaj kontrahentów (nazwa, NIP, miasto)"""
```

#### 2.2. Moduł `gus_api_client.py`

**API GUS REGON:**
- URL: https://api.stat.gov.pl/Home/RegonApi
- Wymaga klucza API (darmowy po rejestracji)
- SOAP-based API

```python
class GUSApiClient:
    def __init__(self, klucz_api: str):
        self.klucz_api = klucz_api
        self.url = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
        self.sesja_id = None
    
    def zaloguj(self) -> bool:
        """Zaloguj się do API GUS i pobierz session ID"""
        
    def pobierz_dane_z_nip(self, nip: str) -> dict:
        """Pobierz dane podmiotu z GUS po NIP"""
        
    def pobierz_dane_z_regon(self, regon: str) -> dict:
        """Pobierz dane podmiotu z GUS po REGON"""
        
    def wyloguj(self):
        """Wyloguj sesję"""
```

**Alternatywa - API.GUS.GOV.PL (nieoficjalne, prostsze):**
```python
def pobierz_dane_nip_prosty(nip: str) -> dict:
    """
    Użyj prostszego API (bez logowania):
    GET https://wl-api.mf.gov.pl/api/search/nip/{nip}
    
    Ministerstwo Finansów - Lista Podatników VAT
    """
    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip.replace('-', '')}"
    response = requests.get(url, params={'date': datetime.now().strftime('%Y-%m-%d')})
    return response.json()
```

#### 2.3. Nowe Endpointy w `app.py`

```python
# === KONTRAHENCI API ===

@app.route('/api/kontrahenci', methods=['GET'])
def lista_kontrahentow():
    """Pobierz listę wszystkich kontrahentów"""
    
@app.route('/api/kontrahenci/<int:id>', methods=['GET'])
def pobierz_kontrahenta(id):
    """Pobierz szczegóły kontrahenta"""
    
@app.route('/api/kontrahenci', methods=['POST'])
def dodaj_kontrahenta():
    """Dodaj nowego kontrahenta"""
    
@app.route('/api/kontrahenci/<int:id>', methods=['PUT'])
def edytuj_kontrahenta(id):
    """Edytuj kontrahenta"""
    
@app.route('/api/kontrahenci/<int:id>', methods=['DELETE'])
def usun_kontrahenta(id):
    """Usuń kontrahenta"""
    
@app.route('/api/kontrahenci/szukaj', methods=['GET'])
def szukaj_kontrahentow():
    """Wyszukaj kontrahentów (query param: q)"""
    
# === INTEGRACJA GUS ===

@app.route('/api/gus/nip/<nip>', methods=['GET'])
def pobierz_z_gus_nip(nip):
    """Pobierz dane z GUS po NIP"""
    
@app.route('/api/gus/regon/<regon>', methods=['GET'])
def pobierz_z_gus_regon(regon):
    """Pobierz dane z GUS po REGON"""
```

---

### 3. Frontend - HTML/JavaScript

#### 3.1. Nowy szablon `kontrahenci.html`

**Sekcje:**
1. **Lista kontrahentów** (tabela)
   - Kolumny: ID, Nazwa, NIP, Miasto, Email, Telefon, Akcje
   - Wyszukiwanie dynamiczne
   - Sortowanie (nazwa, data dodania)
   
2. **Modal dodawania/edycji**
   - Formularz z wszystkimi polami
   - Przycisk "Pobierz z GUS" obok pola NIP
   - Walidacja NIP (10 cyfr)
   - Auto-wypełnianie po pobraniu z GUS

3. **Modal szczegółów kontrahenta**
   - Pełne dane kontrahenta
   - Historia ofert dla tego kontrahenta
   - Przycisk "Nowa oferta dla kontrahenta"

**Funkcje JavaScript:**
```javascript
function pobierzDaneZGUS() {
    // Pobierz NIP z formularza
    const nip = $('#nip').val().replace(/\-/g, '');
    
    // Walidacja NIP
    if (!walidujNIP(nip)) {
        alert('Nieprawidłowy NIP!');
        return;
    }
    
    // Wywołaj API
    $('#loadingGUS').show();
    $.get('/api/gus/nip/' + nip, function(data) {
        if (data.success) {
            // Wypełnij formularz
            $('#nazwa').val(data.nazwa);
            $('#regon').val(data.regon);
            $('#adres_ulica').val(data.ulica + ' ' + data.nrNieruchomosci);
            $('#adres_kod').val(data.kodPocztowy);
            $('#adres_miasto').val(data.miejscowosc);
            $('#adres_wojewodztwo').val(data.wojewodztwo);
            $('#forma_prawna').val(data.formaPrawna);
            $('#pkd_glowny').val(data.pkd);
            
            // Komunikat sukcesu
            showAlert('success', 'Dane pobrane z GUS pomyślnie!');
        } else {
            showAlert('danger', 'Nie znaleziono podmiotu w bazie GUS!');
        }
        $('#loadingGUS').hide();
    });
}

function walidujNIP(nip) {
    // Algorytm walidacji NIP (suma kontrolna)
    if (nip.length !== 10) return false;
    
    const wagi = [6, 5, 7, 2, 3, 4, 5, 6, 7];
    let suma = 0;
    
    for (let i = 0; i < 9; i++) {
        suma += parseInt(nip[i]) * wagi[i];
    }
    
    const kontrolna = suma % 11;
    return kontrolna === parseInt(nip[9]);
}
```

#### 3.2. Modyfikacja `index.html` (kalkulator)

**Dodaj sekcję kontrahenta:**
```html
<div class="card mb-4">
    <div class="card-header bg-info text-white">
        <h5><i class="fas fa-building"></i> Kontrahent</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-8">
                <label>Wybierz kontrahenta</label>
                <select id="kontrahent_id" name="kontrahent_id" class="form-select">
                    <option value="">-- Bez kontrahenta --</option>
                    <!-- Załadowane z API -->
                </select>
            </div>
            <div class="col-md-4">
                <label>&nbsp;</label>
                <button type="button" class="btn btn-success w-100" 
                        onclick="otworzModalKontrahenta()">
                    <i class="fas fa-plus"></i> Nowy kontrahent
                </button>
            </div>
        </div>
        
        <!-- Podgląd wybranego kontrahenta -->
        <div id="kontrahent_preview" class="mt-3" style="display:none;">
            <div class="alert alert-info">
                <strong id="kontrahent_nazwa"></strong><br>
                <small>
                    NIP: <span id="kontrahent_nip"></span> | 
                    <span id="kontrahent_miasto"></span>
                </small>
            </div>
        </div>
    </div>
</div>
```

#### 3.3. Modyfikacja `historia.html`

**Dodaj kolumnę "Kontrahent":**
```javascript
// W renderujListe()
html += `
    <div class="col-md-6">
        <h5 class="card-title mb-1">
            <i class="fas fa-file-invoice"></i> Oferta #${oferta.id}
        </h5>
        ${oferta.kontrahent ? `
            <p class="text-primary mb-1">
                <i class="fas fa-building"></i> ${oferta.kontrahent.nazwa}
            </p>
        ` : ''}
        <p class="text-muted mb-1">
            <small>
                ${oferta.format_druku || 'Brak danych'} | 
                ${oferta.naklad} szt | 
                ${oferta.rodzaj_papieru || 'Brak danych'}
            </small>
        </p>
    </div>
`;
```

---

### 4. Struktura Danych

#### 4.1. Plik `kontrahenci.json`

```json
[
  {
    "id": 1,
    "nazwa": "ABC Sp. z o.o.",
    "nip": "1234567890",
    "regon": "123456789",
    "adres_ulica": "ul. Przykładowa 10",
    "adres_kod": "00-001",
    "adres_miasto": "Warszawa",
    "adres_wojewodztwo": "mazowieckie",
    "email": "kontakt@abc.pl",
    "telefon": "+48 123 456 789",
    "osoba_kontaktowa": "Jan Kowalski",
    "uwagi": "Klient stały, rabat 10%",
    "forma_prawna": "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
    "pkd_glowny": "18.12.Z",
    "data_rejestracji": "2010-05-15",
    "status": "aktywny",
    "data_dodania": "2025-10-17T22:30:00",
    "ostatnia_modyfikacja": "2025-10-17T22:30:00"
  }
]
```

#### 4.2. Rozszerzenie `KalkulacjaZlecenia`

```python
@dataclass
class KalkulacjaZlecenia:
    # ... istniejące pola ...
    
    # NOWE POLE
    kontrahent_id: int = None  # ID kontrahenta z bazy
    kontrahent: dict = None    # Pełne dane kontrahenta (zapisywane razem z ofertą)
```

---

### 5. Integracja z API GUS

#### 5.1. Ministerstwo Finansów - Biała Lista VAT

**Zalety:**
- ✅ Darmowe, bez rejestracji
- ✅ RESTful JSON API
- ✅ Proste w użyciu
- ✅ Dane aktualne
- ⚠️ Tylko podmioty VAT (nie wszystkie firmy)

**Endpoint:**
```
GET https://wl-api.mf.gov.pl/api/search/nip/{nip}?date=YYYY-MM-DD
```

**Odpowiedź:**
```json
{
  "result": {
    "subject": {
      "name": "ABC SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
      "nip": "1234567890",
      "statusVat": "Czynny",
      "regon": "123456789",
      "pesel": null,
      "krs": "0000123456",
      "residenceAddress": "ul. Przykładowa 10, 00-001 Warszawa",
      "workingAddress": "ul. Przykładowa 10, 00-001 Warszawa",
      "representatives": [...],
      "authorizedClerks": [...],
      "partners": [...],
      "registrationLegalDate": "2010-05-15",
      "registrationDenialDate": null,
      "registrationDenialBasis": null,
      "restorationDate": null,
      "restorationBasis": null,
      "removalDate": null,
      "removalBasis": null,
      "accountNumbers": ["12345678901234567890123456"]
    }
  }
}
```

#### 5.2. GUS REGON API (alternatywa)

**Zalety:**
- ✅ Pełniejsze dane (forma prawna, PKD, data rejestracji)
- ✅ Wszystkie podmioty (nie tylko VAT)
- ⚠️ Wymaga rejestracji i klucza API
- ⚠️ SOAP-based (trudniejsze)

**Proces:**
1. Rejestracja: https://api.stat.gov.pl/Home/RegonApi
2. Otrzymanie klucza testowego (ważny 90 dni)
3. Logowanie SOAP → otrzymanie sessionId
4. Zapytanie SOAP z NIP/REGON
5. Parsowanie XML

---

### 6. Harmonogram Implementacji

#### Faza 1: Backend (1.5h)
1. **kontrahenci_manager.py** - CRUD kontrahentów (30 min)
2. **gus_api_client.py** - integracja z Białą Listą VAT (30 min)
3. **app.py** - nowe endpointy API (30 min)

#### Faza 2: Frontend (2h)
1. **kontrahenci.html** - strona zarządzania (1h)
2. **Modyfikacja index.html** - wybór kontrahenta w kalkulatorze (30 min)
3. **Modyfikacja historia.html** - wyświetlanie kontrahenta (30 min)

#### Faza 3: Testy i Integracja (30 min)
1. Test dodawania kontrahenta
2. Test pobierania z GUS
3. Test kalkulacji z kontrahentem
4. Test historii z kontrahentami

**Szacowany czas total:** ~4 godziny

---

### 7. Kryteria Akceptacji

✅ **Kontrahenci:**
- [ ] Dodawanie nowego kontrahenta (formularz)
- [ ] Edycja istniejącego kontrahenta
- [ ] Usuwanie kontrahenta
- [ ] Lista wszystkich kontrahentów
- [ ] Wyszukiwanie kontrahentów (nazwa, NIP, miasto)

✅ **Integracja GUS:**
- [ ] Walidacja NIP (suma kontrolna)
- [ ] Przycisk "Pobierz z GUS" w formularzu
- [ ] Automatyczne wypełnianie pól po pobraniu
- [ ] Obsługa błędów (NIP nie znaleziony, błąd API)

✅ **Kalkulator:**
- [ ] Select kontrahenta w formularzu
- [ ] Przycisk "Nowy kontrahent" (modal)
- [ ] Podgląd wybranego kontrahenta
- [ ] Zapisywanie kontrahenta razem z ofertą

✅ **Historia:**
- [ ] Wyświetlanie nazwy kontrahenta w liście ofert
- [ ] Filtrowanie ofert po kontrahencie
- [ ] Pełne dane kontrahenta w szczegółach oferty

---

### 8. Bezpieczeństwo i Prywatność

**RODO - Dane osobowe:**
- ⚠️ NIP, REGON, adres, email, telefon = dane osobowe
- ✅ Informacja o administratorze danych
- ✅ Podstawa prawna przetwarzania (umowa, zgoda)
- ✅ Prawo do usunięcia danych

**Implementacja:**
```python
# W kontrahenci_manager.py
def anonimizuj_kontrahenta(self, id: int):
    """Anonimizuj dane kontrahenta (RODO - prawo do usunięcia)"""
    kontrahent = self.pobierz_kontrahenta(id)
    kontrahent['nazwa'] = f"[USUNIĘTY #{id}]"
    kontrahent['nip'] = "XXXXXXXXXX"
    kontrahent['email'] = "usuniete@example.com"
    kontrahent['telefon'] = "XXX XXX XXX"
    kontrahent['uwagi'] = "[Dane usunięte zgodnie z RODO]"
    # Zachowaj tylko ID dla integralności historii ofert
```

---

### 9. Opcjonalne Rozszerzenia (v1.3+)

- [ ] Import kontrahentów z CSV/Excel
- [ ] Eksport listy kontrahentów do PDF
- [ ] Historia ofert dla kontrahenta (statystyki)
- [ ] Automatyczne rabaty dla stałych klientów
- [ ] Integracja z e-faktura (KSeF)
- [ ] Synchronizacja z systemem księgowym

---

## Podsumowanie

**Nowe funkcje v1.2:**
1. ✅ Pełny system zarządzania kontrahentami (CRUD)
2. ✅ Integracja z Białą Listą VAT (Ministerstwo Finansów)
3. ✅ Automatyczne pobieranie danych firmy po NIP
4. ✅ Walidacja NIP (suma kontrolna)
5. ✅ Przypisywanie kontrahenta do oferty
6. ✅ Filtrowanie ofert po kontrahencie

**Nowe pliki:**
- `kontrahenci_manager.py` (~200 linii)
- `gus_api_client.py` (~150 linii)
- `templates/kontrahenci.html` (~400 linii)
- `kontrahenci.json` (dane)

**Modyfikacje:**
- `app.py` (+150 linii - nowe endpointy)
- `templates/index.html` (+50 linii - wybór kontrahenta)
- `templates/historia.html` (+30 linii - wyświetlanie kontrahenta)
- `kalkulator_druku_v2.py` (+2 pola w dataclass)

**Szacowana złożoność:** Średnia  
**Szacowany czas:** 4 godziny  
**Zależności:** `requests` (do API)

---

**Wersja planu:** 1.0  
**Data:** 2025-10-17  
**Status:** Gotowy do implementacji  
