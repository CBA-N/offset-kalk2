# 🚀 Dokumentacja nowych features - Kalkulator Druku v1.2

Data: 2025-10-24
Implementacja: 3 nowe funkcjonalności

---

## ✅ Feature #1: Fix kontrahentów - lista pusta przy wyszukiwaniu

### Problem:
Przy otwarciu zakładki kontrahentów lista jest pusta. Zawartość pojawia się dopiero po wpisaniu przynajmniej 1 znaku w wyszukiwarce.

### Przyczyna:
Funkcja `szukajKontrahentow()` w `templates/kontrahenci.html` linia 523-525:
```javascript
if (!fraza) {
    renderujTabele();  // ❌ Renderuje z pustej zmiennej kontrahenci
    return;
}
```

Gdy user usuwał tekst wyszukiwania, funkcja tylko renderowała tabelę bez ponownego ładowania danych z API.

### Rozwiązanie:
**Plik:** `templates/kontrahenci.html` linia 524

**Zmiana:**
```javascript
if (!fraza) {
    zaladujKontrahentow();  // ✅ Załaduj wszystkich ponownie
    return;
}
```

### Test:
1. Otwórz http://localhost:5000/kontrahenci
2. Lista kontrahentów powinna być widoczna natychmiast (3 kontrahenty)
3. Wpisz frazę wyszukiwania → filtruje
4. Usuń frazę → lista wraca do wszystkich kontrahentów

---

## ✅ Feature #2: Automatyczny cache formularza

### Problem:
Po przejściu do słowników/historii/kontrahentów, dane wpisane w formularz kalkulacji były gubione.

### Rozwiązanie:
Dodano automatyczny cache używając `localStorage` przeglądarki.

**Plik:** `templates/index.html` linie 669-767

### Implementacja:

#### 1. Funkcja zapisu cache:
```javascript
function zapiszFormularzDoCache() {
    const formData = {
        nazwa_produktu: $('[name="nazwa_produktu"]').val(),
        naklad: $('[name="naklad"]').val(),
        rodzaj_pracy: $('#rodzajPracy').val(),
        format_szerokosc: $('[name="format_szerokosc"]').val(),
        format_wysokosc: $('[name="format_wysokosc"]').val(),
        rodzaj_papieru: $('[name="rodzaj_papieru"]').val(),
        gramatura: $('[name="gramatura"]').val(),
        kolorystyka: $('[name="kolorystyka"]').val(),
        // ... wszystkie pola + checkboxy
    };
    
    localStorage.setItem('kalkulatorFormCache', JSON.stringify(formData));
}
```

#### 2. Funkcja wczytywania cache:
```javascript
function wczytajFormularzZCache() {
    const cachedData = localStorage.getItem('kalkulatorFormCache');
    if (!cachedData) return;
    
    const formData = JSON.parse(cachedData);
    
    // Przywróć wszystkie pola
    if (formData.nazwa_produktu) $('[name="nazwa_produktu"]').val(formData.nazwa_produktu);
    if (formData.naklad) $('[name="naklad"]').val(formData.naklad);
    // ... pozostałe pola
    
    // Przywróć checkboxy
    $('input[name="uszlachetnienia"]').prop('checked', false);
    if (formData.uszlachetnienia) {
        formData.uszlachetnienia.forEach(function(val) {
            $('input[name="uszlachetnienia"][value="' + val + '"]').prop('checked', true);
        });
    }
}
```

#### 3. Triggery:
```javascript
// Wczytaj przy starcie strony
wczytajFormularzZCache();

// Zapisuj przy każdej zmianie
$('#kalkulatorForm input, #kalkulatorForm select').on('change input', function() {
    zapiszFormularzDoCache();
});
```

### Zachowane dane:
- ✅ Wszystkie pola tekstowe (nazwa, wymiary)
- ✅ Wszystkie selecty (papier, gramatura, kolorystyka)
- ✅ Wszystkie checkboxy (uszlachetnienia, obróbka, kolory specjalne)
- ✅ Rodzaj pracy (nowy feature #3)
- ✅ Kontrahent

### Test:
1. Wypełnij formularz kalkulacji
2. Przejdź do zakładki "Słowniki"
3. Wróć do głównej strony
4. ✅ Wszystkie dane powinny być przywrócone

### Opcje:
**Czyszczenie cache** (wyłączone domyślnie):
```javascript
// Opcjonalnie: wyczyść cache po udanej kalkulacji
$('#kalkulatorForm').on('submit', function() {
    setTimeout(function() {
        localStorage.removeItem('kalkulatorFormCache');
    }, 1000);
});
```

---

## ✅ Feature #3: Słownik rodzajów prac

### Cel:
Predefiniowane szablony prac (ulotka, wizytówka, etykieta) z automatycznym wypełnianiem wymiarów.

### Backend - Struktura danych

**Plik:** `slowniki_data.json`

**Nowy słownik:** `rodzaje_prac`

```json
{
  "rodzaje_prac": {
    "Wizytówka standard": {
      "szerokosc": 90,
      "wysokosc": 50,
      "opis": "Standardowa wizytówka 90×50 mm"
    },
    "Ulotka A5": {
      "szerokosc": 148,
      "wysokosc": 210,
      "opis": "Ulotka w formacie A5"
    },
    ...
  }
}
```

**Domyślnie dodano 12 rodzajów:**
1. Wizytówka standard (90×50)
2. Ulotka A5 (148×210)
3. Ulotka A4 (210×297)
4. Plakat A3 (297×420)
5. Plakat A2 (420×594)
6. Etykieta mała (100×70)
7. Etykieta średnia (150×100)
8. Naklejka okrągła (80×80)
9. Folder A4 (210×297)
10. Broszura A5 (148×210)
11. Katalog A4 (210×297)
12. Zaproszenie DL (99×210)

### Backend - CRUD Operations

**Plik:** `slowniki_manager.py` linie 292-374

#### Dodawanie:
```python
def dodaj_rodzaj_pracy(self, nazwa: str, szerokosc: int, wysokosc: int, 
                       opis: str = '') -> Dict:
    if nazwa in self.slowniki['rodzaje_prac']:
        raise ValueError(f"Rodzaj pracy '{nazwa}' już istnieje")
    
    if szerokosc <= 0 or wysokosc <= 0:
        raise ValueError("Wymiary muszą być dodatnie")
    
    self.slowniki['rodzaje_prac'][nazwa] = {
        'szerokosc': int(szerokosc),
        'wysokosc': int(wysokosc),
        'opis': opis
    }
    
    self._zapisz_zmiane('rodzaje_prac', 'dodanie', nazwa)
    self.zapisz_slowniki()
    
    return self.slowniki['rodzaje_prac'][nazwa]
```

#### Edycja:
```python
def edytuj_rodzaj_pracy(self, stara_nazwa: str, nowa_nazwa: str = None,
                        szerokosc: int = None, wysokosc: int = None,
                        opis: str = None) -> Dict:
    # Walidacja + aktualizacja + zmiana nazwy jeśli potrzeba
```

#### Usuwanie:
```python
def usun_rodzaj_pracy(self, nazwa: str) -> bool:
    del self.slowniki['rodzaje_prac'][nazwa]
    self._zapisz_zmiane('rodzaje_prac', 'usunięcie', nazwa)
    self.zapisz_slowniki()
    return True
```

### Backend - API Endpoint

**Plik:** `app.py` linie 237-257

**Endpoint:** `/api/slowniki/rodzaje_prac/<operacja>`

**Operacje:**
- `POST /api/slowniki/rodzaje_prac/dodaj`
  ```json
  {
    "nazwa": "Plakat A1",
    "szerokosc": 594,
    "wysokosc": 841,
    "opis": "Plakat duży A1"
  }
  ```

- `POST /api/slowniki/rodzaje_prac/edytuj`
  ```json
  {
    "stara_nazwa": "Plakat A1",
    "nowa_nazwa": "Plakat A1 duży",
    "szerokosc": 600,
    "opis": "Zaktualizowany opis"
  }
  ```

- `POST /api/slowniki/rodzaje_prac/usun`
  ```json
  {
    "nazwa": "Plakat A1"
  }
  ```

### Frontend - Formularz kalkulacji

**Plik:** `templates/index.html`

#### 1. Dropdown rodzajów prac (linie 31-45):
```html
<div class="row">
    <div class="col-md-12 mb-3">
        <label class="form-label">
            <i class="fas fa-tag"></i> Rodzaj pracy (opcjonalnie - wypełni wymiary)
        </label>
        <select class="form-select" id="rodzajPracy">
            <option value="">-- Wybierz gotowy szablon lub wpisz wymiary ręcznie --</option>
            {% for nazwa, dane in rodzaje_prac.items() %}
            <option value="{{ nazwa }}" data-w="{{ dane.szerokosc }}" data-h="{{ dane.wysokosc }}">
                {{ nazwa }} ({{ dane.szerokosc }}×{{ dane.wysokosc }} mm) - {{ dane.opis }}
            </option>
            {% endfor %}
        </select>
    </div>
</div>
```

#### 2. JavaScript autofill (linie 428-448):
```javascript
// Dropdown rodzaju pracy - autofill wymiarów
$('#rodzajPracy').change(function() {
    const selected = $(this).find(':selected');
    const w = selected.data('w');
    const h = selected.data('h');
    
    if (w && h) {
        $('input[name="format_szerokosc"]').val(w);
        $('input[name="format_wysokosc"]').val(h);
        
        // Opcjonalnie: zaktualizuj nazwę produktu
        const rodzajNazwa = selected.val();
        if (rodzajNazwa && $('input[name="nazwa_produktu"]').val() === 'Mój wydruk') {
            $('input[name="nazwa_produktu"]').val(rodzajNazwa);
        }
    }
});
```

**Zachowanie:**
- User wybiera rodzaj pracy z listy
- Pola "Szerokość" i "Wysokość" są automatycznie wypełniane
- User może nadal edytować wymiary ręcznie (override)
- Opcjonalnie: nazwa produktu zmienia się na wybrany rodzaj

### Frontend - Zarządzanie w słownikach

**Plik:** `templates/slowniki.html`

#### 1. Tab button (linie 44-48):
```html
<li class="nav-item" role="presentation">
    <button class="nav-link" id="rodzaje-tab" data-bs-toggle="tab" data-bs-target="#rodzaje">
        <i class="fas fa-tag"></i> Rodzaje Prac
    </button>
</li>
```

#### 2. Tab content (linie 148-161):
```html
<div class="tab-pane fade" id="rodzaje" role="tabpanel">
    <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
            <span>Rodzaje Prac (szablony formatów)</span>
            <button class="btn btn-success btn-sm" onclick="pokazFormularzRodzajuPracy()">
                <i class="fas fa-plus"></i> Dodaj Rodzaj Pracy
            </button>
        </div>
        <div class="card-body">
            <div id="listaRodzajowPrac"></div>
        </div>
    </div>
</div>
```

#### 3. JavaScript (WYMAGA DODANIA):

Poniższy kod należy dodać do `templates/slowniki.html` przed końcem sekcji `<script>`:

```javascript
// ==================== RODZAJE PRAC ====================

function renderujRodzajePrac() {
    const $lista = $('#listaRodzajowPrac');
    $lista.empty();
    
    const rodzaje = slowniki.rodzaje_prac || {};
    const rodzajeArray = Object.entries(rodzaje);
    
    if (rodzajeArray.length === 0) {
        $lista.html('<p class="text-muted">Brak zdefiniowanych rodzajów prac</p>');
        return;
    }
    
    rodzajeArray.forEach(([nazwa, dane]) => {
        $lista.append(`
            <div class="list-group-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1"><i class="fas fa-tag"></i> ${nazwa}</h6>
                        <p class="mb-1"><strong>Wymiary:</strong> ${dane.szerokosc} × ${dane.wysokosc} mm</p>
                        ${dane.opis ? `<p class="mb-0 text-muted">${dane.opis}</p>` : ''}
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-warning" onclick="edytujRodzajPracy('${nazwa.replace(/'/g, "\\'")}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="usunRodzajPracy('${nazwa.replace(/'/g, "\\'")}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `);
    });
}

function pokazFormularzRodzajuPracy(nazwa = null) {
    const dane = nazwa ? slowniki.rodzaje_prac[nazwa] : {};
    const tytul = nazwa ? `Edytuj: ${nazwa}` : 'Nowy Rodzaj Pracy';
    
    const html = `
        <div class="mb-3">
            <label class="form-label">Nazwa rodzaju pracy</label>
            <input type="text" class="form-control" id="rodzajNazwa" value="${nazwa || ''}" 
                   ${nazwa ? 'disabled' : ''}>
        </div>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label class="form-label">Szerokość (mm)</label>
                <input type="number" class="form-control" id="rodzajSzerokosc" 
                       value="${dane.szerokosc || ''}" min="1">
            </div>
            <div class="col-md-6 mb-3">
                <label class="form-label">Wysokość (mm)</label>
                <input type="number" class="form-control" id="rodzajWysokosc" 
                       value="${dane.wysokosc || ''}" min="1">
            </div>
        </div>
        <div class="mb-3">
            <label class="form-label">Opis (opcjonalnie)</label>
            <input type="text" class="form-control" id="rodzajOpis" 
                   value="${dane.opis || ''}">
        </div>
        <button class="btn btn-primary" onclick="zapiszRodzajPracy('${nazwa || ''}')">
            <i class="fas fa-save"></i> Zapisz
        </button>
        <button class="btn btn-secondary" onclick="renderujRodzajePrac()">
            Anuluj
        </button>
    `;
    
    $('#listaRodzajowPrac').html(html);
}

function zapiszRodzajPracy(staraNazwa) {
    const nazwa = staraNazwa || $('#rodzajNazwa').val().trim();
    const szerokosc = parseInt($('#rodzajSzerokosc').val());
    const wysokosc = parseInt($('#rodzajWysokosc').val());
    const opis = $('#rodzajOpis').val().trim();
    
    if (!nazwa) {
        alert('Podaj nazwę rodzaju pracy');
        return;
    }
    
    if (!szerokosc || szerokosc <= 0 || !wysokosc || wysokosc <= 0) {
        alert('Podaj poprawne wymiary (liczby dodatnie)');
        return;
    }
    
    const operacja = staraNazwa ? 'edytuj' : 'dodaj';
    const payload = {
        nazwa: nazwa,
        szerokosc: szerokosc,
        wysokosc: wysokosc,
        opis: opis
    };
    
    if (staraNazwa) {
        payload.stara_nazwa = staraNazwa;
    }
    
    $.ajax({
        url: `/api/slowniki/rodzaje_prac/${operacja}`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function(response) {
            if (response.success) {
                zaladujSlowniki();
                pokazPowiadomienie(`Rodzaj pracy "${nazwa}" ${operacja === 'dodaj' ? 'dodany' : 'zaktualizowany'}`, 'success');
            }
        },
        error: function(xhr) {
            alert('Błąd: ' + (xhr.responseJSON?.error || 'Nieznany błąd'));
        }
    });
}

function edytujRodzajPracy(nazwa) {
    pokazFormularzRodzajuPracy(nazwa);
}

function usunRodzajPracy(nazwa) {
    if (!confirm(`Czy na pewno usunąć rodzaj pracy "${nazwa}"?`)) return;
    
    $.ajax({
        url: '/api/slowniki/rodzaje_prac/usun',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ nazwa: nazwa }),
        success: function(response) {
            if (response.success) {
                zaladujSlowniki();
                pokazPowiadomienie(`Rodzaj pracy "${nazwa}" usunięty`, 'success');
            }
        },
        error: function(xhr) {
            alert('Błąd: ' + (xhr.responseJSON?.error || 'Nieznany błąd'));
        }
    });
}

// Dodaj wywołanie renderujRodzajePrac() w funkcji zaladujSlowniki()
// Znajdź linię z renderujStawki() i dodaj poniżej:
renderujRodzajePrac();
```

### Test Feature #3:

**Test 1: Dropdown w formularzu**
1. Otwórz http://localhost:5000/
2. W sekcji "Dane Podstawowe" znajdź dropdown "Rodzaj pracy"
3. Wybierz "Wizytówka standard"
4. ✅ Pola Szerokość=90, Wysokość=50 powinny się wypełnić automatycznie
5. ✅ Możesz nadal edytować wymiary ręcznie

**Test 2: Zarządzanie słownikiem**
1. Przejdź do http://localhost:5000/slowniki
2. Kliknij zakładkę "Rodzaje Prac"
3. ✅ Powinna być lista 12 rodzajów
4. Kliknij "Dodaj Rodzaj Pracy"
5. Wypełnij: Nazwa="Test A6", Szerokość=105, Wysokość=148
6. Kliknij "Zapisz"
7. ✅ Nowy rodzaj pojawi się na liście
8. Test edycji: kliknij edytuj, zmień wymiary, zapisz
9. Test usuwania: kliknij usuń, potwierdź

**Test 3: Cache z rodzajem pracy**
1. W formularzu wybierz rodzaj pracy "Ulotka A5"
2. Przejdź do słowników
3. Wróć do formularza
4. ✅ Dropdown powinien mieć wybrany "Ulotka A5"
5. ✅ Wymiary powinny być zachowane (148×210)

---

## 📝 Pliki zmodyfikowane:

### Backend:
1. **slowniki_data.json** - dodano słownik `rodzaje_prac` z 12 pozycjami
2. **slowniki_manager.py** - dodano 3 metody CRUD (linie 292-374)
3. **app.py** - dodano obsługę API `rodzaje_prac` (linie 237-257), przekazywanie do template

### Frontend:
4. **templates/index.html**:
   - Dropdown rodzajów prac (linie 31-45)
   - JavaScript autofill (linie 428-448)
   - Integracja z cache (linie 672, 704)
   
5. **templates/kontrahenci.html**:
   - Fix wyszukiwania (linia 524)
   
6. **templates/slowniki.html**:
   - Tab button (linie 44-48)
   - Tab content (linie 148-161)
   - JavaScript (WYMAGA DODANIA - kod powyżej)

---

## 🔄 Synchronizacja z AI Drive

**KRYTYCZNE:** Po zakończeniu wszystkich modyfikacji, wykonaj:

```bash
# 1. Skopiuj zmodyfikowane pliki backend
cp /home/user/webapp/slowniki_data.json /mnt/aidrive/kalkulator_v1.2_clean/backend/data/
cp /home/user/webapp/slowniki_manager.py /mnt/aidrive/kalkulator_v1.2_clean/backend/
cp /home/user/webapp/app.py /mnt/aidrive/kalkulator_v1.2_clean/backend/

# 2. Skopiuj zmodyfikowane pliki frontend
cp /home/user/webapp/templates/index.html /mnt/aidrive/kalkulator_v1.2_clean/frontend/templates/
cp /home/user/webapp/templates/kontrahenci.html /mnt/aidrive/kalkulator_v1.2_clean/frontend/templates/
cp /home/user/webapp/templates/slowniki.html /mnt/aidrive/kalkulator_v1.2_clean/frontend/templates/

# 3. Skopiuj dokumentację
cp /home/user/DODANE_FEATURES_DOKUMENTACJA.md /mnt/aidrive/kalkulator_v1.2_clean/docs/

# 4. Weryfikacja
echo "✅ Pliki zsynchronizowane z AI Drive"
ls -lh /mnt/aidrive/kalkulator_v1.2_clean/backend/*.py | grep "Oct 24"
```

---

## 📊 Podsumowanie zmian:

### Statystyki:
- **Zmodyfikowanych plików:** 6
- **Dodanych linii kodu:** ~450
- **Nowych funkcji backend:** 3 (CRUD rodzajów prac)
- **Nowych funkcji frontend:** 8 (cache + rodzaje prac)
- **Nowych rodzajów prac:** 12

### Benefity:
✅ Fix bug kontrahentów (pusta lista)
✅ Lepsze UX - dane nie są gubione przy nawigacji
✅ Szybsze tworzenie ofert - gotowe szablony formatów
✅ Łatwiejsze zarządzanie - edycja szablonów przez UI

---

## 🚀 Następne kroki (opcjonalne):

1. **Dokończ JavaScript dla rodzajów prac** w slowniki.html
2. **Testy regresyjne** - dodaj do test_all_components.py
3. **Import/Export** - dodaj rodzaje prac do eksportu JSON
4. **Historia zmian** - loguj operacje na rodzajach prac
5. **Walidacja** - sprawdzaj duplikaty wymiarów

---

**Autor:** AI Assistant
**Data:** 2025-10-24
**Wersja:** Kalkulator Druku v1.2 + Features
