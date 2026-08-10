from sectio_moteur.classification.classement import proposer_types
from sectio_moteur.methode_simplifiee import MethodeSimplifiee
from sectio_moteur.modeles import PoteauInput


def poteau(reference, G):
    return PoteauInput(
        G=G,
        Q=200.0,
        fck=30.0,
        fyk=500.0,
        L0=2.83,
        d_prime=0.035,
        type_section="rectangulaire",
        b=0.30,
        h=0.30,
        reference=reference,
    )


def test_deux_poteaux_identiques_restent_distincts():
    a = poteau("1", 1209.0)
    b = poteau("2", 1209.0)

    assert a != b
    assert len({a, b}) == 2


def test_tous_les_poteaux_sont_couverts():
    poteaux = [poteau("1", 1209.0), poteau("2", 1209.0), poteau("3", 400.0)]

    types, echecs = proposer_types(poteaux, MethodeSimplifiee())

    assert echecs == []

    references_couvertes = {p.reference for t in types for p in t.poteaux_couverts}
    assert references_couvertes == {"1", "2", "3"}
