from dataclasses import replace
import pytest
from sectio_moteur.methode_simplifiee import calculer_lambda, TAUX_TRAVAIL_MIN
from sectio_moteur.modeles import PoteauInput, TYPE_RECTANGULAIRE, TYPE_CIRCULAIRE
from sectio_moteur.exceptions import (
    TypeSectionInvalideException,
    DimensionsManquantesException,
)

from sectio_moteur.methode_simplifiee import MethodeSimplifiee

"""définition des entrées constantes avec des valeurs valides pour tous les tests"""
_ENTREE_BASE = PoteauInput(
    type_section=TYPE_RECTANGULAIRE,
    L0=6,
    b=0.60,
    h=0.40,
    diametre=None,
    fck=30,
    fyk=500,
    d_prime=0.035,
    G=120.9,
    Q=20.0,
)


def _entree(**overrides):
    """copie de _ENTREE_BASE avec certains champs modifiés."""
    return replace(_ENTREE_BASE, **overrides)


def test_calculer_lambda_rectangulaire():
    entree = _entree()
    assert calculer_lambda(entree) == pytest.approx(51.96, rel=1e-3)
    # tolérance relative d'approximation


def test_calculer_lambda_circulaire():
    entree = _entree(type_section=TYPE_CIRCULAIRE, diametre=0.50, b=None, h=None)
    assert calculer_lambda(entree) == pytest.approx(48.0, rel=1e-3)  # 4*6/0.5


def test_calculer_lambda_type_section_invalide():
    entree = _entree(type_section="essai")
    with pytest.raises(TypeSectionInvalideException):
        calculer_lambda(entree)


def test_calculer_lambda_dimensions_manquantes_rectangulaire():
    entree = _entree(b=None)
    with pytest.raises(DimensionsManquantesException):
        calculer_lambda(entree)


def test_calculer_lambda_dimensions_manquantes_circulaire():
    entree = _entree(type_section=TYPE_CIRCULAIRE, diametre=None)
    with pytest.raises(DimensionsManquantesException):
        calculer_lambda(entree)


def test_calculer_type_section_invalide():
    entree = _entree(type_section="rectangualire")

    with pytest.raises(TypeSectionInvalideException):
        MethodeSimplifiee().calculer(entree)


def test_verifier_reproduit_calculer():
    entree = _entree(L0=2.829, b=0.30, h=0.30, G=1209.0, Q=200.0)
    methode = MethodeSimplifiee()

    resultat_calcule = methode.calculer(entree)
    resultat_verifie = methode.verifier(resultat_calcule.As, entree)

    assert resultat_verifie.NRd == pytest.approx(resultat_calcule.NRd)
    assert resultat_verifie.kh == pytest.approx(resultat_calcule.kh)
    assert resultat_verifie.rho == pytest.approx(resultat_calcule.rho)


""" Tests est_applicable() """


def test_est_applicable_fck_hors_plage():
    entree = _entree(fck=60)
    methode = MethodeSimplifiee()
    violations = methode.est_applicable(entree)

    assert violations != []
    assert any("fck" in v for v in violations)


def test_cas_reference_arche():
    """Test officiel Arche 03-0188SSLLG_EC2 issu du PDF Arche Validation Guide 2018 FR page 119.
    Poteau carre 0,30x0,30, lambda=32,66. G=1209 kN, Q=200 kN (120,90T et 20,00T, 1T=10kN).
    Reference Arche (SANS marge BE, NRd=NEd) : As=34cm2 (v2018 Arche: 33,51).
    Notre calculer() applique TAUX_TRAVAIL_MIN=1,1 (marge BE confirmee Pierre) :
    valeurs ci-dessous recalculees avec cette marge -- pas comparables au 34cm2 du guide.
    """
    entree = _entree(L0=2.829, b=0.30, h=0.30, G=1209.0, Q=200.0)
    r = MethodeSimplifiee().calculer(entree)

    assert abs(r.As - 42.02) / 42.02 < 0.03
    assert abs(r.NRd - 2125.37) / 2125.37 < 0.03
    assert abs(r.kh - 0.8706) < 0.01


@pytest.mark.parametrize(
    "entree",
    [
        # rectangulaire, branche quadratique — cas de référence Arche
        _entree(L0=2.829, b=0.30, h=0.30, G=1209.0, Q=200.0),
        # circulaire, branche quadratique (D < 0,60 m)
        _entree(
            type_section=TYPE_CIRCULAIRE,
            diametre=0.40,
            b=None,
            h=None,
            L0=3.0,
            G=900.0,
            Q=200.0,
        ),
        # circulaire, branche linéaire (D >= 0,60 m)
        _entree(
            type_section=TYPE_CIRCULAIRE,
            diametre=0.70,
            b=None,
            h=None,
            L0=3.0,
            G=2500.0,
            Q=500.0,
        ),
    ],
)
def test_calculer_atteint_le_taux_de_travail_vise(entree):
    resultat = MethodeSimplifiee().calculer(entree)
    assert resultat.taux_travail == pytest.approx(TAUX_TRAVAIL_MIN, rel=1e-9)
