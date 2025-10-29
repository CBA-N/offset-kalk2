import json
import os

import pytest

from slowniki_manager import SlownikiManager


@pytest.fixture()
def manager(tmp_path):
    plik = tmp_path / "slowniki_test.json"
    mgr = SlownikiManager(str(plik))
    return mgr


def test_dodaje_nowa_kategorie(manager):
    wynik = manager.dodaj_kategorie_papieru('Premium', 'Papiery premium o wysokim połysku')

    kategorie = manager.get_kategorie_papieru()

    assert 'Premium' in kategorie
    assert wynik['nazwa'] == 'Premium'
    assert kategorie['Premium']['opis'] == 'Papiery premium o wysokim połysku'

    # Plik powinien zostać utworzony po zapisie
    assert os.path.exists(manager.plik_json)
    with open(manager.plik_json, encoding='utf-8') as f:
        dane = json.load(f)
    assert 'Premium' in dane['kategorie_papieru']


def test_edycja_kategorii_aktualizuje_papiery(manager):
    manager.dodaj_kategorie_papieru('Testowa', 'Opis testowy')
    manager.dodaj_papier('Papier testowy', [100], [5.0], 'Testowa')

    wynik = manager.edytuj_kategorie_papieru('Testowa', nowa_nazwa='Zmieniona', opis='Nowy opis')

    assert wynik['nazwa'] == 'Zmieniona'
    assert wynik['opis'] == 'Nowy opis'

    kategorie = manager.get_kategorie_papieru()
    assert 'Zmieniona' in kategorie
    assert 'Testowa' not in kategorie

    papier = manager.get_slownik('papiery')['Papier testowy']
    assert papier['kategoria'] == 'Zmieniona'


def test_usuniecie_kategorii_bez_powiazanych_papierow(manager):
    manager.dodaj_kategorie_papieru('Do usunięcia')

    assert manager.usun_kategorie_papieru('Do usunięcia') is True
    assert 'Do usunięcia' not in manager.get_kategorie_papieru()


def test_usuniecie_przypisanej_kategorii_wywoluje_blad(manager):
    manager.dodaj_kategorie_papieru('Powiazana')
    manager.dodaj_papier('Papier powiazany', [120], [6.5], 'Powiazana')

    with pytest.raises(ValueError):
        manager.usun_kategorie_papieru('Powiazana')


def test_przypisanie_nowej_kategorii_do_istniejacego_papieru(manager):
    manager.dodaj_kategorie_papieru('Specjalna', 'Nowa kategoria do testów')

    papier_przed = manager.get_slownik('papiery')['Offset']
    assert papier_przed['kategoria'] != 'Specjalna'

    manager.edytuj_papier('Offset', kategoria='Specjalna')

    papier_po = manager.get_slownik('papiery')['Offset']
    assert papier_po['kategoria'] == 'Specjalna'
