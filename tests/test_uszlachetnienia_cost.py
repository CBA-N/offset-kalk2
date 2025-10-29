import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from slowniki_manager import SlownikiManager  # noqa: E402
from slowniki_adapter import wstrzyknij_slowniki_do_kalkulatora  # noqa: E402
from kalkulator_druku_v2 import KalkulatorDruku  # noqa: E402


class KalkulatorUszlachetnieniaTest(unittest.TestCase):
    def setUp(self):
        self.manager = SlownikiManager(os.path.join(ROOT_DIR, 'data', 'slowniki_data.json'))
        self.kalkulator = KalkulatorDruku()
        wstrzyknij_slowniki_do_kalkulatora(self.kalkulator, self.manager)

    def test_koszt_uszlachetnien_wliczony_w_sume(self):
        dane = {
            'nazwa_produktu': 'Testowy plakat',
            'format_wydruku_mm': [210, 297],  # A4
            'naklad': 1000,
            'rodzaj_papieru': 'Digital - DigiColor',
            'gramatura': 120,
            'kolorystyka_cmyk': '4+4',
            'kolory_specjalne': [],
            'uszlachetnienia': ['Lakier UV całościowy'],
            'obrobka': [],
            'pakowanie': 'Folia stretch (standard)',
            'transport': 'Odbiór własny',
            'marza_procent': 20,
            'priorytet_optymalizacji': 'Zrównoważony'
        }

        kalkulacja = self.kalkulator.kalkuluj_zlecenie(dane)

        self.assertGreater(kalkulacja.koszt_uszlachetnien, 0, "Koszt uszlachetnień powinien być dodatni")

        suma_elementow = (
            kalkulacja.koszt_papieru +
            kalkulacja.koszt_druku +
            kalkulacja.koszt_kolorow_spec +
            kalkulacja.koszt_uszlachetnien +
            kalkulacja.koszt_obrobki +
            kalkulacja.koszt_pakowania +
            kalkulacja.koszt_transportu +
            kalkulacja.koszt_ciecia_papieru
        )

        self.assertAlmostEqual(
            kalkulacja.suma_kosztow_netto,
            suma_elementow,
            places=2,
            msg="Koszt uszlachetnień musi być doliczony do sumy kosztów"
        )

    def test_uszlachetnienie_arkuszowe_wg_slownika(self):
        wynik = self.kalkulator.kalkuluj_uszlachetnienia(
            ['Lakier UV całościowy'],
            ilosc_arkuszy=2000,
            powierzchnia_arkusza=0.5,
            naklad=0,
            waga_kg=0
        )

        self.assertAlmostEqual(wynik['koszt'], 5000.0, places=2)

    def test_uszlachetnienie_metrowe_z_slownika(self):
        self.kalkulator.uszlachetnienia['Test Metrowy'] = {
            'cena_pln': 100.0,
            'jednostka': '1 m²',
            'typ_jednostki': 'metrowa',
            'kod_jednostki': 'METRY_1'
        }
        self.addCleanup(lambda: self.kalkulator.uszlachetnienia.pop('Test Metrowy', None))

        wynik = self.kalkulator.kalkuluj_uszlachetnienia(
            ['Test Metrowy'],
            ilosc_arkuszy=4,
            powierzchnia_arkusza=0.5,
            naklad=0,
            waga_kg=0
        )

        self.assertAlmostEqual(wynik['koszt'], 200.0, places=2)

    def test_obrobka_wagowa_z_slownika(self):
        self.kalkulator.obrobka['Test Wagowy'] = {
            'cena_pln': 50.0,
            'jednostka': '1 kg',
            'typ_jednostki': 'wagowa',
            'kod_jednostki': 'KILOGRAM_1'
        }
        self.addCleanup(lambda: self.kalkulator.obrobka.pop('Test Wagowy', None))

        wynik = self.kalkulator.kalkuluj_obrobke(
            ['Test Wagowy'],
            naklad=0,
            powierzchnia_arkusza=0,
            ilosc_arkuszy=0,
            waga_kg=20
        )

        self.assertAlmostEqual(wynik['koszt'], 1000.0, places=2)


if __name__ == '__main__':
    unittest.main()
