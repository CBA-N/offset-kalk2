"""
Aplikacja webowa Flask - Kalkulator Druku Offsetowego
"""

from flask import Flask, render_template, request, jsonify, send_file
import sys
import os
import json
from datetime import datetime
import io

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kalkulator_druku_v2 import KalkulatorDruku, drukuj_oferte, KalkulacjaZlecenia
from slowniki_danych import *
from dataclasses import asdict
from slowniki_manager import SlownikiManager
from slowniki_adapter import wstrzyknij_slowniki_do_kalkulatora
from historia_manager import HistoriaManager
from kontrahenci_manager import KontrahenciManager
from biala_lista_vat import BialaListaVATClient

app = Flask(__name__, template_folder='../frontend/templates')
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'twoj-sekretny-klucz-zmien-w-produkcji'

# Inicjalizacja kalkulatora
kalkulator = KalkulatorDruku()

# Menedżer słowników z trwałym zapisem
slowniki_mgr = SlownikiManager(plik_json='../data/slowniki_data.json')

# Wstrzyknij aktualne słowniki do kalkulatora
kalkulator = wstrzyknij_slowniki_do_kalkulatora(kalkulator, slowniki_mgr)

# Manager historii ofert z trwałym zapisem
historia_mgr = HistoriaManager(plik_json='../data/historia_ofert.json', limit=50)

# Manager kontrahentów
kontrahenci_mgr = KontrahenciManager(plik_json='../data/kontrahenci.json')

# Klient API Białej Listy VAT
vat_api = BialaListaVATClient()


def odswiez_kalkulator():
    """Odśwież słowniki w kalkulatorze po edycji"""
    global kalkulator
    kalkulator = wstrzyknij_slowniki_do_kalkulatora(kalkulator, slowniki_mgr)


@app.route('/')
def index():
    """Strona główna - formularz kalkulacji"""
    # Pobierz nową strukturę i przekonwertuj na starą (dla szablonu)
    from slowniki_adapter import adapter_nowy_do_starego
    slowniki_nowe = slowniki_mgr.get_wszystkie()
    slowniki_stare = adapter_nowy_do_starego(slowniki_nowe)
    
    return render_template('index.html',
                         papiery=slowniki_stare['papiery'],
                         formaty=slowniki_stare['formaty'],
                         uszlachetnienia=slowniki_stare['uszlachetnienia'],
                         obrobka=slowniki_stare['obrobka'],
                         kolory_spec=slowniki_stare['kolory_specjalne'],
                         kolorystyki=slowniki_nowe.get('kolorystyki', {}),
                         pakowanie=slowniki_stare['pakowanie'],
                         transport=slowniki_stare['transport'],
                         priorytety=slowniki_stare.get('priorytety', {}),
                         marze=slowniki_stare.get('marza', {}),
                         rodzaje_prac=slowniki_nowe.get('rodzaje_prac', {}))


@app.route('/slowniki')
def slowniki():
    """Edytor słowników"""
    return render_template('slowniki.html')


@app.route('/historia')
def historia():
    """Historia ofert"""
    return render_template('historia.html', oferty=historia_mgr.pobierz_wszystkie())


@app.route('/api/slowniki', methods=['GET'])
def get_slowniki():
    """API: Pobierz wszystkie słowniki"""
    return jsonify(slowniki_mgr.get_wszystkie())


@app.route('/api/slowniki/<kategoria>', methods=['GET'])
def get_slownik(kategoria):
    """API: Pobierz konkretny słownik"""
    slownik = slowniki_mgr.get_slownik(kategoria)
    if slownik is not None:
        return jsonify(slownik)
    else:
        return jsonify({"error": "Nieznana kategoria"}), 404


@app.route('/api/slowniki/<kategoria>/<operacja>', methods=['POST'])
def manage_slownik(kategoria, operacja):
    """API: Zarządzaj słownikiem (dodaj/edytuj/usuń)"""
    try:
        dane = request.json
        
        # PAPIERY
        if kategoria == 'papiery':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_papier(
                    dane['nazwa'],
                    dane['gramatury'],
                    dane['ceny'],
                    dane.get('kategoria', 'niepowlekany')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_papier(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('gramatury'),
                    dane.get('ceny'),
                    dane.get('kategoria')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_papier(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400

        # KATEGORIE PAPIERU
        elif kategoria == 'kategorie_papieru':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_kategorie_papieru(
                    dane['nazwa'],
                    dane.get('opis', '')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_kategorie_papieru(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('opis')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_kategorie_papieru(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400

        # USZLACHETNIENIA
        elif kategoria == 'uszlachetnienia':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_uszlachetnienie(
                    dane['nazwa'],
                    dane['typ'],
                    dane['cena_pln'],
                    dane.get('jednostka', '1000 ark'),
                    dane.get('opis', ''),
                    dane.get('typ_jednostki', 'sztukowa'),
                    dane.get('kod_jednostki')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_uszlachetnienie(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('typ'),
                    dane.get('cena_pln'),
                    dane.get('jednostka'),
                    dane.get('opis'),
                    dane.get('typ_jednostki'),
                    dane.get('kod_jednostki')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_uszlachetnienie(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400

        # OBRÓBKA
        elif kategoria == 'obrobka':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_obrobke(
                    dane['nazwa'],
                    dane['cena_pln'],
                    dane.get('jednostka', '1000 szt'),
                    dane.get('opis', ''),
                    dane.get('typ_jednostki', 'sztukowa'),
                    dane.get('kod_jednostki')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_obrobke(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('cena_pln'),
                    dane.get('jednostka'),
                    dane.get('opis'),
                    dane.get('typ_jednostki'),
                    dane.get('kod_jednostki')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_obrobke(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400

        # JEDNOSTKI
        elif kategoria == 'jednostki':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_jednostke(
                    dane['kod'],
                    dane['etykieta'],
                    dane['typ_jednostki'],
                    dane['mnoznik_domyslny'],
                    dane.get('slowa_kluczowe', []),
                    dane.get('zrodlo_bazowej_ilosci')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_jednostke(
                    dane['stary_kod'],
                    dane.get('nowy_kod'),
                    dane.get('etykieta'),
                    dane.get('typ_jednostki'),
                    dane.get('mnoznik_domyslny'),
                    dane.get('slowa_kluczowe'),
                    dane.get('zrodlo_bazowej_ilosci')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_jednostke(dane['kod'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400

        # KOLORYSTYKI DRUKU
        elif kategoria == 'kolorystyki':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_kolorystyke(
                    dane['nazwa'],
                    dane.get('kolory_przod', 0),
                    dane.get('kolory_tyl', 0),
                    dane.get('mnoznik_przelotow', 1.0),
                    dane.get('domyslna_ilosc_form', 1),
                    dane.get('etykieta'),
                    dane.get('opis', '')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_kolorystyke(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('kolory_przod'),
                    dane.get('kolory_tyl'),
                    dane.get('mnoznik_przelotow'),
                    dane.get('domyslna_ilosc_form'),
                    dane.get('etykieta'),
                    dane.get('opis')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_kolorystyke(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400

        # KOLORY SPECJALNE
        elif kategoria == 'kolory_specjalne':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_kolor_specjalny(
                    dane['nazwa'],
                    dane['cena_pln'],
                    dane.get('cena_preperatu_pln', 50.0),
                    dane.get('opis', '')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_kolor_specjalny(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('cena_pln'),
                    dane.get('cena_preperatu_pln'),
                    dane.get('opis')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_kolor_specjalny(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400
        
        # PAKOWANIE
        elif kategoria == 'pakowanie':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_pakowanie(
                    dane['nazwa'],
                    dane['cena_pln'],
                    dane.get('opis', '')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_pakowanie(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('cena_pln'),
                    dane.get('opis')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_pakowanie(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400
        
        # TRANSPORT
        elif kategoria == 'transport':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_transport(
                    dane['nazwa'],
                    dane['cena_pln'],
                    dane.get('opis', '')
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_transport(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('cena_pln'),
                    dane.get('opis')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_transport(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400
        
        # RODZAJE PRAC
        elif kategoria == 'rodzaje_prac':
            if operacja == 'dodaj':
                wynik = slowniki_mgr.dodaj_rodzaj_pracy(
                    dane['nazwa'],
                    dane['szerokosc'],
                    dane['wysokosc'],
                    dane.get('opis', ''),
                    dane.get('spad', 2.5)
                )
            elif operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_rodzaj_pracy(
                    dane['stara_nazwa'],
                    dane.get('nowa_nazwa'),
                    dane.get('szerokosc'),
                    dane.get('wysokosc'),
                    dane.get('opis'),
                    dane.get('spad')
                )
            elif operacja == 'usun':
                wynik = slowniki_mgr.usun_rodzaj_pracy(dane['nazwa'])
            else:
                return jsonify({"error": "Nieznana operacja"}), 400
        
        # STAWKI
        elif kategoria == 'stawki':
            if operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_stawke(
                    dane['klucz'],
                    dane['wartosc']
                )
            else:
                return jsonify({"error": "Dla stawek dostępna tylko edycja"}), 400
        
        # CIĘCIE PAPIERU
        elif kategoria == 'ciecie':
            if operacja == 'edytuj':
                wynik = slowniki_mgr.edytuj_ciecie_papieru(
                    dane['koszt_roboczogodziny_pln'],
                    dane['wydajnosc_arkuszy_h'],
                    dane['wymiary_zakupu_mm'],
                    dane['koszt_przygotowania_pln']
                )
            else:
                return jsonify({"error": "Dla cięcia dostępna tylko edycja"}), 400
        
        else:
            return jsonify({"error": "Nieznana kategoria"}), 404
        
        # Odśwież słowniki w kalkulatorze po każdej zmianie
        odswiez_kalkulator()
        
        return jsonify({
            "success": True,
            "message": f"Operacja '{operacja}' wykonana pomyślnie",
            "data": wynik
        })
        
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Błąd serwera: {str(e)}"}), 500


@app.route('/api/papiery-kategorie', methods=['GET'])
def get_papiery_kategorie():
    """API: Pobierz papiery pogrupowane według kategorii"""
    papiery = slowniki_mgr.get_slownik('papiery')
    kategorie = slowniki_mgr.get_slownik('kategorie_papieru')

    # Grupuj według kategorii
    pogrupowane = {}
    for nazwa, dane in papiery.items():
        kat = dane.get('kategoria', 'inne')
        rekord_kategorii = kategorie.get(kat, {}) if isinstance(kategorie, dict) else {}
        kat_nazwa = rekord_kategorii.get('nazwa') if isinstance(rekord_kategorii, dict) else None
        if not kat_nazwa:
            kat_nazwa = kat.capitalize()

        if kat_nazwa not in pogrupowane:
            pogrupowane[kat_nazwa] = []

        pogrupowane[kat_nazwa].append({
            'nazwa': nazwa,
            'gramatury': dane['gramatury'],
            'kategoria_id': kat
        })

    # Sortuj kategorie alfabetycznie
    posortowane = sorted(pogrupowane.items(), key=lambda item: item[0].lower())

    return jsonify({
        'kategorie': [nazwa for nazwa, _ in posortowane],
        'papiery': {nazwa: lista for nazwa, lista in posortowane}
    })


@app.route('/api/gramatury/<rodzaj_papieru>', methods=['GET'])
def get_gramatury(rodzaj_papieru):
    """API: Pobierz dostępne gramatury dla rodzaju papieru"""
    papiery = slowniki_mgr.get_slownik('papiery')
    if rodzaj_papieru in papiery:
        return jsonify({
            "gramatury": papiery[rodzaj_papieru]['gramatury'],
            "ceny": papiery[rodzaj_papieru]['ceny']
        })
    else:
        return jsonify({"error": "Nieznany rodzaj papieru"}), 404


@app.route('/api/historia-zmian', methods=['GET'])
def get_historia_zmian():
    """API: Pobierz historię zmian słowników"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(slowniki_mgr.get_historia_zmian(limit))


@app.route('/api/backup', methods=['POST'])
def utworz_backup():
    """API: Utwórz backup słowników"""
    try:
        backup_file = slowniki_mgr.utworz_backup()
        return jsonify({
            "success": True,
            "message": "Backup utworzony pomyślnie",
            "file": backup_file
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/backup/przywroc', methods=['POST'])
def przywroc_backup():
    """API: Przywróć backup słowników"""
    try:
        dane = request.json
        backup_file = dane.get('backup_file')
        
        if not backup_file:
            return jsonify({"error": "Brak nazwy pliku backupu"}), 400
        
        slowniki_mgr.przywroc_backup(backup_file)
        return jsonify({
            "success": True,
            "message": "Backup przywrócony pomyślnie"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kalkuluj', methods=['POST'])
def kalkuluj():
    """API: Wykonaj kalkulację"""
    try:
        dane = request.json
        
        # Przygotuj dane wejściowe
        zlecenie = {
            'nazwa_produktu': dane.get('nazwa_produktu', 'Bez nazwy'),
            'format_wydruku_mm': (int(dane['format_szerokosc']), int(dane['format_wysokosc'])),
            'spad_mm': float(dane.get('spad_mm', 2.5)),
            'naklad': int(dane['naklad']),
            'rodzaj_papieru': dane['rodzaj_papieru'],
            'gramatura': int(dane['gramatura']),
            'kolorystyka_cmyk': dane['kolorystyka'],
            'ilosc_form': int(dane.get('ilosc_form', 4)),
            'kolory_specjalne': dane.get('kolory_specjalne', []),
            'uszlachetnienia': dane.get('uszlachetnienia', []),
            'obrobka': dane.get('obrobka', []),
            'pakowanie': dane.get('pakowanie', ''),
            'transport': dane.get('transport', ''),
            'marza_procent': float(dane.get('marza_procent', 20)),
            'priorytet_optymalizacji': dane.get('priorytet_optymalizacji', 'Zrównoważony')
        }
        
        # Obsługa kontrahenta
        kontrahent_id = dane.get('kontrahent_id')
        if kontrahent_id:
            kontrahent = kontrahenci_mgr.pobierz_kontrahenta(int(kontrahent_id))
            zlecenie['kontrahent_id'] = int(kontrahent_id)
            zlecenie['kontrahent'] = kontrahent
        
        # Wykonaj kalkulację
        wynik = kalkulator.kalkuluj_zlecenie(zlecenie)
        
        # Konwertuj do dict
        wynik_dict = asdict(wynik)
        
        # Dodaj do historii (manager automatycznie doda timestamp i ID)
        wynik_dict = historia_mgr.dodaj_oferte(wynik_dict)
        
        return jsonify({
            "success": True,
            "wynik": wynik_dict
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/oferta/<int:oferta_id>/pdf', methods=['GET'])
def generuj_pdf(oferta_id):
    """API: Generuj PDF oferty (placeholder)"""
    # W pełnej wersji użyj reportlab lub weasyprint
    return jsonify({
        "success": False,
        "message": "Funkcja generowania PDF będzie dostępna w przyszłej wersji"
    }), 501


@app.route('/api/historia', methods=['GET'])
def get_historia():
    """API: Pobierz historię ofert"""
    oferty = historia_mgr.pobierz_wszystkie()

    kontrahent_id = request.args.get('kontrahent_id')
    kontrahent_nazwa = request.args.get('kontrahent_nazwa')

    if kontrahent_id:
        oferty = [
            oferta for oferta in oferty
            if str(oferta.get('kontrahent_id')) == str(kontrahent_id)
        ]

    if kontrahent_nazwa:
        nazwa_normalized = kontrahent_nazwa.strip().lower()
        oferty = [
            oferta for oferta in oferty
            if oferta.get('kontrahent')
            and oferta['kontrahent'].get('nazwa')
            and oferta['kontrahent']['nazwa'].strip().lower() == nazwa_normalized
        ]

    return jsonify(oferty)


@app.route('/api/historia/<int:oferta_id>', methods=['GET'])
def get_oferta(oferta_id):
    """API: Pobierz konkretną ofertę"""
    oferta = historia_mgr.pobierz_oferte(oferta_id)
    if oferta:
        return jsonify(oferta)
    else:
        return jsonify({"error": "Nie znaleziono oferty"}), 404


@app.route('/api/historia/<int:oferta_id>', methods=['DELETE'])
def usun_oferta(oferta_id):
    """API: Usuń ofertę z historii"""
    historia_mgr.usun_oferte(oferta_id)
    return jsonify({"success": True})


@app.route('/api/eksport/json', methods=['GET'])
def eksport_json():
    """API: Eksportuj słowniki do JSON (pobierz plik)"""
    # Pobierz aktualne dane z managera
    slowniki = slowniki_mgr.get_wszystkie()
    
    # Utwórz plik w pamięci
    buffer = io.BytesIO()
    buffer.write(json.dumps(slowniki, indent=2, ensure_ascii=False).encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=f'slowniki_druku_{datetime.now().strftime("%Y%m%d")}.json'
    )


@app.route('/api/statystyki', methods=['GET'])
def statystyki():
    """API: Statystyki ofert"""
    stats = historia_mgr.pobierz_statystyki()
    return jsonify(stats)


# Obsługa błędów
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500




# === KONTRAHENCI API ===

@app.route('/kontrahenci')
def strona_kontrahentow():
    """Strona zarządzania kontrahentami"""
    return render_template('kontrahenci.html')


@app.route('/api/kontrahenci', methods=['GET'])
def lista_kontrahentow():
    """API: Pobierz listę wszystkich kontrahentów"""
    try:
        kontrahenci = kontrahenci_mgr.pobierz_wszystkich()
        return jsonify({
            "success": True,
            "kontrahenci": kontrahenci,
            "liczba": len(kontrahenci)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kontrahenci/<int:id>', methods=['GET'])
def pobierz_kontrahenta(id):
    """API: Pobierz szczegóły kontrahenta"""
    try:
        kontrahent = kontrahenci_mgr.pobierz_kontrahenta(id)
        
        if not kontrahent:
            return jsonify({"success": False, "error": "Nie znaleziono kontrahenta"}), 404
        
        return jsonify({
            "success": True,
            "kontrahent": kontrahent
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kontrahenci', methods=['POST'])
def dodaj_kontrahenta():
    """API: Dodaj nowego kontrahenta"""
    try:
        dane = request.json
        
        # Walidacja wymaganych pól
        if not dane.get('nazwa'):
            return jsonify({"success": False, "error": "Brak nazwy kontrahenta"}), 400
        
        # Dodaj kontrahenta
        kontrahent = kontrahenci_mgr.dodaj_kontrahenta(dane)
        
        return jsonify({
            "success": True,
            "message": "Kontrahent dodany pomyślnie",
            "kontrahent": kontrahent
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kontrahenci/<int:id>', methods=['PUT'])
def edytuj_kontrahenta(id):
    """API: Edytuj kontrahenta"""
    try:
        dane = request.json
        
        # Walidacja
        if not dane.get('nazwa'):
            return jsonify({"success": False, "error": "Brak nazwy kontrahenta"}), 400
        
        # Edytuj
        kontrahent = kontrahenci_mgr.edytuj_kontrahenta(id, dane)
        
        if not kontrahent:
            return jsonify({"success": False, "error": "Nie znaleziono kontrahenta"}), 404
        
        return jsonify({
            "success": True,
            "message": "Kontrahent zaktualizowany pomyślnie",
            "kontrahent": kontrahent
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kontrahenci/<int:id>', methods=['DELETE'])
def usun_kontrahenta(id):
    """API: Usuń kontrahenta"""
    try:
        usuniety = kontrahenci_mgr.usun_kontrahenta(id)
        
        if not usuniety:
            return jsonify({"success": False, "error": "Nie znaleziono kontrahenta"}), 404
        
        return jsonify({
            "success": True,
            "message": "Kontrahent usunięty pomyślnie"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kontrahenci/szukaj', methods=['GET'])
def szukaj_kontrahentow():
    """API: Wyszukaj kontrahentów"""
    try:
        fraza = request.args.get('q', '')
        kontrahenci = kontrahenci_mgr.szukaj(fraza)
        
        return jsonify({
            "success": True,
            "kontrahenci": kontrahenci,
            "liczba": len(kontrahenci),
            "fraza": fraza
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/kontrahenci/statystyki', methods=['GET'])
def statystyki_kontrahentow():
    """API: Pobierz statystyki kontrahentów"""
    try:
        stats = kontrahenci_mgr.pobierz_statystyki()
        return jsonify({
            "success": True,
            "statystyki": stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# === INTEGRACJA BIAŁA LISTA VAT ===

@app.route('/api/vat/waliduj-nip/<nip>', methods=['GET'])
def waliduj_nip(nip):
    """API: Waliduj NIP (suma kontrolna)"""
    try:
        czy_poprawny = vat_api.waliduj_nip(nip)
        
        return jsonify({
            "success": True,
            "nip": nip,
            "poprawny": czy_poprawny,
            "nip_sformatowany": vat_api.formatuj_nip(nip) if czy_poprawny else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/vat/pobierz/<nip>', methods=['GET'])
def pobierz_z_vat(nip):
    """API: Pobierz dane z Białej Listy VAT"""
    try:
        # Pobierz dane z API
        dane = vat_api.pobierz_dane_z_nip(nip)
        
        return jsonify(dane)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    # Utwórz folder templates jeśli nie istnieje
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    cert_path = os.getenv('FLASK_SSL_CERT')
    key_path = os.getenv('FLASK_SSL_KEY')
    ssl_context = None

    if cert_path or key_path:
        if not cert_path or not key_path:
            print("\n⚠️  Podano tylko jeden z plików certyfikatu SSL. Ustaw zarówno FLASK_SSL_CERT jak i FLASK_SSL_KEY, aby uruchomić HTTPS.")
        else:
            cert_abspath = os.path.abspath(cert_path)
            key_abspath = os.path.abspath(key_path)
            if not os.path.isfile(cert_abspath):
                print(f"\n⚠️  Nie znaleziono pliku certyfikatu SSL: {cert_abspath}")
            elif not os.path.isfile(key_abspath):
                print(f"\n⚠️  Nie znaleziono pliku klucza SSL: {key_abspath}")
            elif not cert_abspath.lower().endswith('.pem'):
                print(f"\n⚠️  Certyfikat SSL musi być w formacie .pem (aktualnie: {cert_abspath})")
            elif not key_abspath.lower().endswith('.pem'):
                print(f"\n⚠️  Klucz SSL musi być w formacie .pem (aktualnie: {key_abspath})")
            else:
                ssl_context = (cert_abspath, key_abspath)

    protokol = 'https' if ssl_context else 'http'
    bazowy_adres = f"{protokol}://127.0.0.1:7018"

    print("\n" + "="*60)
    print("🖨️  KALKULATOR DRUKU OFFSETOWEGO - WERSJA WEBOWA")
    print("="*60)
    print(f"\n📍 Serwer działa na: {bazowy_adres}")
    print("\n🔗 Dostępne strony:")
    print(f"   • Kalkulator:  {bazowy_adres}/")
    print(f"   • Słowniki:    {bazowy_adres}/slowniki")
    print(f"   • Historia:    {bazowy_adres}/historia")
    if ssl_context:
        print("\n🔐 HTTPS aktywny (użyto wartości z FLASK_SSL_CERT i FLASK_SSL_KEY)")
    else:
        print("\nℹ️  HTTPS nieaktywne. Aby włączyć, ustaw zmienne środowiskowe FLASK_SSL_CERT i FLASK_SSL_KEY wskazujące na pliki w formacie PEM.")
    print("\n💡 Naciśnij Ctrl+C aby zatrzymać serwer\n")

    app.run(debug=True, host='0.0.0.0', port=7018, ssl_context=ssl_context)
