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
