from pathlib import Path

import pytest

from sectio_moteur.enrobage import calculer_cnom
from sectio_moteur.exceptions import ClasseExpositionInvalideException

CHEMIN_DONNEES_TEST = (
    Path(__file__).parent.parent
    / "src"
    / "sectio_moteur"
    / "data"
    / "tables_enrobage.example.json"
)


def test_calculer_cnom_xc1_s4():
    resultat = calculer_cnom(
        "TEST_XC1",
        "S4",
        chemin_table=CHEMIN_DONNEES_TEST,
    )

    assert resultat == pytest.approx(3.0)  # (20 + 10) mm = 30 mm = 3.0 cm


def test_calculer_cnom_xc4_s5():
    resultat = calculer_cnom(
        "TEST_XC4",
        "S5",
        chemin_table=CHEMIN_DONNEES_TEST,
    )

    assert resultat == pytest.approx(5.5)  # (45 + 10) mm = 55 mm = 5.5 cm


def test_calculer_cnom_classe_structurale_defaut():
    resultat = calculer_cnom(
        "TEST_XC1",
        chemin_table=CHEMIN_DONNEES_TEST,
    )

    assert resultat == pytest.approx(
        3.0
    )  # Classe S4 par défaut : (20 + 10) mm = 3.0 cm


def test_calculer_cnom_classe_exposition_inconnue():
    with pytest.raises(ClasseExpositionInvalideException):
        calculer_cnom(
            "TEST_INCONNUE",
            chemin_table=CHEMIN_DONNEES_TEST,
        )
