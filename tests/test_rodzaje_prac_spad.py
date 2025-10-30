import json

import pytest

from slowniki_manager import SlownikiManager


@pytest.fixture()
def manager(tmp_path):
    """Zwraca menedżera słowników działającego na pliku tymczasowym."""
    plik = tmp_path / "slowniki.json"
    return SlownikiManager(str(plik))


def test_migracja_dodaje_domyslny_spad(tmp_path):
    """Podczas migracji brakujący spad powinien zostać ustawiony na 2.5 mm."""
    dane = {
        "rodzaje_prac": {
            "Test": {
                "szerokosc": 100,
                "wysokosc": 200,
                "opis": "Bez spadu"
            }
        }
    }

    plik = tmp_path / "slowniki.json"
    with open(plik, "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False)

    mgr = SlownikiManager(str(plik))
    rodzaje = mgr.get_slownik("rodzaje_prac")

    assert pytest.approx(rodzaje["Test"]["spad"], rel=0) == 2.5


def test_dodawanie_i_edycja_spadu(manager):
    """Można ustawić spad przy dodawaniu i edycji rodzaju pracy."""
    manager.dodaj_rodzaj_pracy("Specjalny", 150, 210, "Opis", spad=3.1)

    rodzaje = manager.get_slownik("rodzaje_prac")
    assert pytest.approx(rodzaje["Specjalny"]["spad"], rel=0) == 3.1

    manager.edytuj_rodzaj_pracy("Specjalny", spad=1.8)
    rodzaje = manager.get_slownik("rodzaje_prac")
    assert pytest.approx(rodzaje["Specjalny"]["spad"], rel=0) == 1.8
