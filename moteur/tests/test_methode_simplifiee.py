from dataclasses import replace

import pytest

from sectio_moteur.exceptions import (
    DimensionsManquantesException,
    SectionInsuffisanteException,
    TypeSectionInvalideException,
)
from sectio_moteur.methode_simplifiee import MethodeSimplifiee, calculer_lambda
from sectio_moteur.modeles import (
    TAUX_TRAVAIL_MIN_DEFAUT,
    TYPE_CIRCULAIRE,
    TYPE_RECTANGULAIRE,
    PoteauInput,
)


@pytest.fixture
def creer_entree():
    def _creer(**overrides):
        entree_base = PoteauInput(
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
        return replace(entree_base, **overrides)

    return _creer


class TestCalculerLambda:
    def test_calculer_lambda_rectangulaire(self, creer_entree):
        entree = creer_entree()
        assert calculer_lambda(entree) == pytest.approx(51.96, rel=1e-3)
        # tolérance relative d'approximation

    def test_calculer_lambda_circulaire(self, creer_entree):
        entree = creer_entree(
            type_section=TYPE_CIRCULAIRE, diametre=0.50, b=None, h=None
        )
        assert calculer_lambda(entree) == pytest.approx(48.0, rel=1e-3)  # 4*6/0.5

    def test_calculer_lambda_type_section_invalide(self, creer_entree):
        entree = creer_entree(type_section="essai")
        with pytest.raises(TypeSectionInvalideException):
            calculer_lambda(entree)

    def test_calculer_lambda_dimensions_manquantes_rectangulaire(self, creer_entree):
        entree = creer_entree(b=None)
        with pytest.raises(DimensionsManquantesException):
            calculer_lambda(entree)

    def test_calculer_lambda_dimensions_manquantes_circulaire(self, creer_entree):
        entree = creer_entree(type_section=TYPE_CIRCULAIRE, diametre=None)
        with pytest.raises(DimensionsManquantesException):
            calculer_lambda(entree)


class TestCalculer:
    def test_calculer_type_section_invalide(self, creer_entree):
        entree = creer_entree(type_section="rectangualire")

        with pytest.raises(TypeSectionInvalideException):
            MethodeSimplifiee().calculer(entree)

    @pytest.mark.parametrize(
        "overrides",
        [
            # rectangulaire, branche quadratique — cas de référence Arche
            {"L0": 2.829, "b": 0.30, "h": 0.30, "G": 1209.0, "Q": 200.0},
            # circulaire, branche quadratique (D < 0,60 m)
            {
                "type_section": TYPE_CIRCULAIRE,
                "diametre": 0.40,
                "b": None,
                "h": None,
                "L0": 3.0,
                "G": 900.0,
                "Q": 200.0,
            },
            # circulaire, branche linéaire (D >= 0,60 m)
            {
                "type_section": TYPE_CIRCULAIRE,
                "diametre": 0.70,
                "b": None,
                "h": None,
                "L0": 3.0,
                "G": 2500.0,
                "Q": 500.0,
            },
        ],
    )
    def test_calculer_atteint_le_taux_de_travail_vise(self, creer_entree, overrides):
        entree = creer_entree(**overrides)
        resultat = MethodeSimplifiee().calculer(entree)
        if resultat.as_min_gouverne:
            assert resultat.taux_travail >= TAUX_TRAVAIL_MIN_DEFAUT
        else:
            assert resultat.taux_travail == pytest.approx(
                TAUX_TRAVAIL_MIN_DEFAUT, rel=1e-9
            )

    def test_cas_reference_arche_sans_marge(self, creer_entree):
        """Test officiel Arche 03-0188SSLLG_EC2 (Arche Validation Guide 2018 FR, page 119).

        Poteau carre 0,30x0,30, lambda=32,66. G=1209 kN, Q=200 kN (120,90T et 20,00T, 1T=10kN).
        Reference Arche : As=34cm2 (valeur calculee par Arche v2018 : 33,51).
        Valide les formules EC2 nues, sans marge : taux_travail_min=1,0 par defaut, donc NRd=NEd.
        """
        entree = creer_entree(L0=2.829, b=0.30, h=0.30, G=1209.0, Q=200.0)
        r = MethodeSimplifiee().calculer(entree)

        assert abs(r.As - 33.94) / 33.94 < 0.03
        assert r.NRd == pytest.approx(r.NEd, rel=1e-9)

    def test_marge_be_rejete_le_poteau_de_reference(self, creer_entree):
        """30×30 + marge 10 % → As = 42,0 cm² = 4,67 % Ac > As,max (4 %)."""
        entree = creer_entree(
            L0=2.829, b=0.30, h=0.30, G=1209.0, Q=200.0, taux_travail_min=1.1
        )
        with pytest.raises(SectionInsuffisanteException):
            MethodeSimplifiee().calculer(entree)


class TestVerifier:

    def test_verifier_reproduit_calculer(self, creer_entree):
        entree = creer_entree(L0=2.829, b=0.30, h=0.30, G=1209.0, Q=200.0)
        methode = MethodeSimplifiee()

        resultat_calcule = methode.calculer(entree)
        resultat_verifie = methode.verifier(resultat_calcule.As, entree)

        assert resultat_verifie.NRd == pytest.approx(resultat_calcule.NRd)
        assert resultat_verifie.kh == pytest.approx(resultat_calcule.kh)
        assert resultat_verifie.rho == pytest.approx(resultat_calcule.rho)


class TestEstApplicable:
    def test_est_applicable_fck_hors_plage(self, creer_entree):
        entree = creer_entree(fck=60)
        methode = MethodeSimplifiee()
        violations = methode.est_applicable(entree)

        assert violations != []
        assert any("fck" in v for v in violations)
