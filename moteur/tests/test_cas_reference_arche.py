import pytest

from sectio_moteur.methode_simplifiee import MethodeSimplifiee
from sectio_moteur.modeles import TYPE_CIRCULAIRE, TYPE_RECTANGULAIRE, PoteauInput

"""Tests de bout en bout du moteur de calcul avec des cas référence Arche."""


@pytest.fixture
def poteau_circulaire_d_50cm():
    """Cas A — poteau circulaire D=0,50m. Branche quadratique (D<0,60m)."""
    return PoteauInput(
        type_section=TYPE_CIRCULAIRE,
        L0=3.10,
        b=None,
        h=None,
        diametre=0.50,
        fck=45,
        fyk=500,
        d_prime=0.033,
        G=1514.9,
        Q=1000.0,
    )


@pytest.fixture
def poteau_carre_60_x_60_11m():
    """Cas B — poteau carré 0,60×0,60m, L0=11m. Branche linéaire (h>=0,50m)."""
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        L0=11.00,
        b=0.60,
        h=0.60,
        diametre=None,
        fck=45,
        fyk=500,
        d_prime=0.032,
        G=1597.1,
        Q=1000.0,
    )


@pytest.fixture
def poteau_carre_44cm():
    """Cas C — poteau carré 0,44×0,44m. Branche quadratique (h<0,50m)."""
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        L0=3.10,
        b=0.44,
        h=0.44,
        diametre=None,
        fck=45,
        fyk=500,
        d_prime=0.036,
        G=2014.7,
        Q=1000.0,
    )


@pytest.fixture
def poteau_carre_50cm():
    """Cas D — poteau carré 0.50x0.50."""
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        L0=5.00,
        b=0.50,
        h=0.50,
        diametre=None,
        fck=45,
        fyk=500,
        d_prime=0.045,
        G=2530.7,
        Q=2000.0,
    )


@pytest.fixture
def cas_E_poteau_circulaire_50cm():
    """Cas E — poteau circulaire 0.50m"""
    return PoteauInput(
        type_section=TYPE_CIRCULAIRE,
        L0=5.00,
        diametre=0.50,
        fck=45,
        fyk=500,
        d_prime=0.041,
        G=1524.1,
        Q=1000.0,
    )


@pytest.fixture
def cas_F_poteau_50x40_fck45():
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        b=0.50,
        h=0.40,
        fck=45,
        fyk=500,
        L0=5.00,
        d_prime=0.045,
        G=1524.5,
        Q=1500.0,
    )


@pytest.fixture
def cas_G_poteau_50x40_fck25():
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        b=0.50,
        h=0.40,
        fck=25,
        fyk=500,
        L0=5.00,
        d_prime=0.045,
        G=1524.5,
        Q=1000.0,
    )


@pytest.fixture
def cas_H_circulaire_60cm():
    return PoteauInput(
        type_section=TYPE_CIRCULAIRE,
        diametre=0.60,
        fck=45,
        fyk=500,
        L0=3.00,
        d_prime=0.038,
        G=4520.8,
        Q=1500.0,
    )


@pytest.fixture
def cas_I_circulaire_70cm():
    return PoteauInput(
        type_section=TYPE_CIRCULAIRE,
        diametre=0.70,
        fck=45,
        fyk=500,
        L0=5.00,
        d_prime=0.041,
        G=5547.2,
        Q=1800.0,
    )


@pytest.fixture
def cas_J_circulaire_40cm_elance():
    return PoteauInput(
        type_section=TYPE_CIRCULAIRE,
        diametre=0.40,
        fck=45,
        fyk=500,
        L0=6.50,
        d_prime=0.036,
        G=820.0,
        Q=300.0,
    )


@pytest.fixture
def cas_K_carre_30cm_elance():
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        b=0.30,
        h=0.30,
        fck=45,
        fyk=500,
        L0=6.00,
        d_prime=0.036,
        G=663.2,
        Q=200.0,
    )


@pytest.fixture
def cas_L_poteau_50x40_fck20():
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        b=0.50,
        h=0.40,
        fck=20,
        fyk=500,
        L0=5.00,
        d_prime=0.040,
        G=1424.5,
        Q=450.0,
    )


@pytest.fixture
def cas_M_poteau_50x40_fck50():
    return PoteauInput(
        type_section=TYPE_RECTANGULAIRE,
        b=0.50,
        h=0.40,
        fck=50,
        fyk=500,
        L0=5.00,
        d_prime=0.040,
        G=2624.5,
        Q=900.0,
    )


class TestCasReferenceArcheA:
    """Circulaire D=0,50m — ferraillage réel Arche : 6HA14, cadres HA6/14."""

    def test_as_theorique(self, poteau_circulaire_d_50cm):
        r = MethodeSimplifiee().calculer(poteau_circulaire_d_50cm)
        assert r.As == pytest.approx(8.15, rel=1e-3)
        assert r.as_min_gouverne is True

    def test_ferraillage_reel_arche_dans_combinaisons(self, poteau_circulaire_d_50cm):
        r = MethodeSimplifiee().calculer(poteau_circulaire_d_50cm)
        assert r.combinaisons_possibles is not None
        assert (6, 14) in r.combinaisons_possibles

    def test_nrd_avec_ferraillage_reel(self, poteau_circulaire_d_50cm):
        r = MethodeSimplifiee().verifier(9.24, poteau_circulaire_d_50cm)
        assert r.NRd == pytest.approx(4080.5708, rel=1e-4)

    def test_cadres_diametre(self, poteau_circulaire_d_50cm):
        r = MethodeSimplifiee().calculer(poteau_circulaire_d_50cm)
        assert r.diametre_cadres == pytest.approx(6.0)


class TestCasReferenceArcheB:
    """Carré 0,60×0,60m — ferraillage réel Arche : 8HA12, cadres HA6/49 + 98 épingles.

    <!> Épingles non modélisées par calculer_armatures_transversales() —
    aucune assertion sur les cadres pour ce cas.
    """

    def test_as_theorique(self, poteau_carre_60_x_60_11m):
        r = MethodeSimplifiee().calculer(poteau_carre_60_x_60_11m)
        assert r.As == pytest.approx(8.41, rel=1e-3)
        assert r.as_min_gouverne is True

    def test_ferraillage_reel_arche_dans_combinaisons(self, poteau_carre_60_x_60_11m):
        r = MethodeSimplifiee().calculer(poteau_carre_60_x_60_11m)
        assert r.combinaisons_possibles is not None
        assert (8, 12) in r.combinaisons_possibles

    def test_nrd_avec_ferraillage_reel(self, poteau_carre_60_x_60_11m):
        r = MethodeSimplifiee().verifier(9.05, poteau_carre_60_x_60_11m)
        assert r.NRd == pytest.approx(4591.7513, rel=1e-4)


class TestCasReferenceArcheC:
    """Carré 0,44×0,44m — ferraillage réel Arche : 4HA20, cadres HA6/10."""

    def test_as_theorique(self, poteau_carre_44cm):
        r = MethodeSimplifiee().calculer(poteau_carre_44cm)
        assert r.As == pytest.approx(9.71, rel=1e-3)
        assert r.as_min_gouverne is True

    def test_ferraillage_reel_arche_dans_combinaisons(self, poteau_carre_44cm):
        r = MethodeSimplifiee().calculer(poteau_carre_44cm)
        assert r.combinaisons_possibles is not None
        assert (4, 20) in r.combinaisons_possibles

    def test_nrd_avec_ferraillage_reel(self, poteau_carre_44cm):
        r = MethodeSimplifiee().verifier(12.57, poteau_carre_44cm)
        assert r.NRd == pytest.approx(4575.0953, rel=1e-4)

    def test_cadres_diametre(self, poteau_carre_44cm):
        r = MethodeSimplifiee().calculer(poteau_carre_44cm)
        assert r.diametre_cadres == pytest.approx(6.0)


class TestCasReferenceArcheD:
    """Carré 0,50×0,50m, L0=5,00m — ferraillage réel Arche : 12HA25
    Cas limite h=0,50m"""

    def test_as_theorique(self, poteau_carre_50cm):
        r = MethodeSimplifiee().calculer(poteau_carre_50cm)
        assert r.As == pytest.approx(55.40, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_ferraillage_reel_arche_dans_combinaisons(self, poteau_carre_50cm):
        r = MethodeSimplifiee().calculer(poteau_carre_50cm)
        assert r.combinaisons_possibles is not None
        assert (12, 25) in r.combinaisons_possibles

    def test_nrd_avec_ferraillage_reel(self, poteau_carre_50cm):
        r = MethodeSimplifiee().verifier(58.90, poteau_carre_50cm)
        assert r.NRd == pytest.approx(6510.0, rel=1e-4)

    def test_cadres_diametre(self, poteau_carre_50cm):
        r = MethodeSimplifiee().calculer(poteau_carre_50cm)
        assert r.diametre_cadres == pytest.approx(8.0)


class TestCasReferenceArcheE:
    """Circulaire D=0,50m, L0=5,00m — ferraillage réel Arche : 12HA20"""

    def test_as_theorique(self, cas_E_poteau_circulaire_50cm):
        r = MethodeSimplifiee().calculer(cas_E_poteau_circulaire_50cm)
        assert r.As == pytest.approx(29.34, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_nrd_avec_ferraillage_reel(self, cas_E_poteau_circulaire_50cm):
        r = MethodeSimplifiee().verifier(37.70, cas_E_poteau_circulaire_50cm)
        assert r.NRd == pytest.approx(3727.4, rel=1e-4)


class TestCasReferenceArcheF:
    """Rectangulaire 0,50×0,40m, fck=45 — ferraillage réel Arche : 8HA25+2HA20"""

    def test_as_theorique(self, cas_F_poteau_50x40_fck45):
        r = MethodeSimplifiee().calculer(cas_F_poteau_50x40_fck45)
        assert r.As == pytest.approx(45.23, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_nrd_avec_ferraillage_reel(self, cas_F_poteau_50x40_fck45):
        r = MethodeSimplifiee().verifier(45.55, cas_F_poteau_50x40_fck45)
        assert r.NRd == pytest.approx(4315.0, rel=1e-4)


class TestCasReferenceArcheG:
    """Rectangulaire 0,50×0,40m, fck=25 — ferraillage réel Arche : 12HA25+6HA20"""

    def test_as_theorique(self, cas_G_poteau_50x40_fck25):
        r = MethodeSimplifiee().calculer(cas_G_poteau_50x40_fck25)
        assert r.As == pytest.approx(76.30, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_nrd_avec_ferraillage_reel(self, cas_G_poteau_50x40_fck25):
        r = MethodeSimplifiee().verifier(77.75, cas_G_poteau_50x40_fck25)
        assert r.NRd == pytest.approx(3590.1, rel=1e-4)


class TestCasReferenceArcheH:
    """Circulaire D=0,60m — ferraillage réel Arche : 14HA25, cadres HA6.

    <!> CAS FRONTIÈRE — NE PAS "SYMÉTRISER" AVEC LE RECTANGULAIRE.
    """

    def test_as_theorique(self, cas_H_circulaire_60cm):
        r = MethodeSimplifiee().calculer(cas_H_circulaire_60cm)
        assert r.As == pytest.approx(67.46, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_branche_lineaire_a_la_frontiere(self, cas_H_circulaire_60cm):
        r = MethodeSimplifiee().calculer(cas_H_circulaire_60cm)
        assert r.kh == pytest.approx(1.0)

    def test_ferraillage_reel_arche_dans_combinaisons(self, cas_H_circulaire_60cm):
        r = MethodeSimplifiee().calculer(cas_H_circulaire_60cm)
        assert r.combinaisons_possibles is not None
        assert (14, 25) in r.combinaisons_possibles

    def test_nrd_avec_ferraillage_reel(self, cas_H_circulaire_60cm):
        r = MethodeSimplifiee().verifier(68.72, cas_H_circulaire_60cm)
        assert r.NRd == pytest.approx(8393.2944, rel=1e-4)


class TestCasReferenceArcheI:
    """Circulaire D=0,70m — ferraillage réel Arche : 24HA25, cadres HA8.

    Seul cas exerçant la branche linéaire en circulaire.
    """

    def test_as_theorique(self, cas_I_circulaire_70cm):
        r = MethodeSimplifiee().calculer(cas_I_circulaire_70cm)
        assert r.As == pytest.approx(97.66, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_kh_vaut_un(self, cas_I_circulaire_70cm):
        r = MethodeSimplifiee().calculer(cas_I_circulaire_70cm)
        assert r.kh == pytest.approx(1.0)

    def test_nrd_avec_ferraillage_reel(self, cas_I_circulaire_70cm):
        r = MethodeSimplifiee().verifier(117.81, cas_I_circulaire_70cm)
        assert r.NRd == pytest.approx(10754.1030, rel=1e-4)


class TestCasReferenceArcheJ:
    """Circulaire D=0,40m, L0=6,50m — ferraillage réel Arche : 12HA20, cadres HA6.

    λ=65 : seul cas exerçant α = (27/λ)^1,24 (circulaire, λ>60).
    """

    def test_as_theorique(self, cas_J_circulaire_40cm_elance):
        r = MethodeSimplifiee().calculer(cas_J_circulaire_40cm_elance)
        assert r.As == pytest.approx(33.91, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_lambda_declenche_seconde_branche_alpha(self, cas_J_circulaire_40cm_elance):
        r = MethodeSimplifiee().calculer(cas_J_circulaire_40cm_elance)
        assert r.lambda_ == pytest.approx(65.0, rel=1e-3)
        assert r.alpha == pytest.approx((27 / 65.0) ** 1.24, rel=1e-6)

    def test_nrd_avec_ferraillage_reel(self, cas_J_circulaire_40cm_elance):
        r = MethodeSimplifiee().verifier(37.70, cas_J_circulaire_40cm_elance)
        assert r.NRd == pytest.approx(1602.3506, rel=1e-4)


class TestCasReferenceArcheK:
    """Carré 0,30×0,30m, L0=6,00m — ferraillage réel Arche : 6HA20+2HA16, cadres HA6.

    <!> Ferraillage panaché (deux diamètres) : non modélisé par
    choix_armatures(), aucune assertion sur combinaisons_possibles.
    """

    def test_as_theorique(self, cas_K_carre_30cm_elance):
        r = MethodeSimplifiee().calculer(cas_K_carre_30cm_elance)
        assert r.As == pytest.approx(22.84, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_lambda_declenche_seconde_branche_alpha(self, cas_K_carre_30cm_elance):
        r = MethodeSimplifiee().calculer(cas_K_carre_30cm_elance)
        assert r.lambda_ == pytest.approx(69.28, rel=1e-3)
        assert r.alpha == pytest.approx((32 / r.lambda_) ** 1.3, rel=1e-6)

    def test_nrd_avec_ferraillage_reel(self, cas_K_carre_30cm_elance):
        r = MethodeSimplifiee().verifier(22.87, cas_K_carre_30cm_elance)
        assert r.NRd == pytest.approx(1195.7738, rel=1e-4)


class TestCasReferenceArcheL:
    """Rectangulaire 0,50×0,40m, fck=20 — ferraillage réel Arche : 4HA25+10HA20.

    Borne basse du domaine d'application (20 ≤ fck ≤ 50).
    """

    def test_as_theorique(self, cas_L_poteau_50x40_fck20):
        r = MethodeSimplifiee().calculer(cas_L_poteau_50x40_fck20)
        assert r.As == pytest.approx(49.13, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_methode_applicable_a_la_borne_basse(self, cas_L_poteau_50x40_fck20):
        assert MethodeSimplifiee().est_applicable(cas_L_poteau_50x40_fck20) == []

    def test_nrd_avec_ferraillage_reel(self, cas_L_poteau_50x40_fck20):
        r = MethodeSimplifiee().verifier(51.05, cas_L_poteau_50x40_fck20)
        assert r.NRd == pytest.approx(2642.1455, rel=1e-4)


class TestCasReferenceArcheM:
    """Rectangulaire 0,50×0,40m, fck=50 — ferraillage réel Arche : 10HA25+4HA20.

    Borne haute du domaine d'application (20 ≤ fck ≤ 50).
    """

    def test_as_theorique(self, cas_M_poteau_50x40_fck50):
        r = MethodeSimplifiee().calculer(cas_M_poteau_50x40_fck50)
        assert r.As == pytest.approx(55.10, rel=1e-3)
        assert r.as_min_gouverne is False

    def test_methode_applicable_a_la_borne_haute(self, cas_M_poteau_50x40_fck50):
        assert MethodeSimplifiee().est_applicable(cas_M_poteau_50x40_fck50) == []

    def test_nrd_avec_ferraillage_reel(self, cas_M_poteau_50x40_fck50):
        r = MethodeSimplifiee().verifier(61.65, cas_M_poteau_50x40_fck50)
        assert r.NRd == pytest.approx(5037.9611, rel=1e-4)
