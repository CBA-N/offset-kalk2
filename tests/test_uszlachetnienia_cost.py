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


if __name__ == '__main__':
    unittest.main()
