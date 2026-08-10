import pytest
from sectio_moteur.methode_simplifiee import MethodeSimplifiee

from calculs.services import (
    VERSION_MOTEUR,
    calculer_poteau,
    poteau_vers_entree,
)
from projets.models import Batiment, Niveau, Poteau, Projet, TypePoteau


@pytest.fixture
def utilisateur(django_user_model):
    return django_user_model.objects.create_user(
        email="pierre@exemple.fr",
        first_name="Pierre",
        last_name="Dupont",
        password="motdepasse",
    )


@pytest.fixture
def niveau(utilisateur):
    projet = Projet.objects.create(
        nom="Résidence Garonne", fck=30.0, fyk=500.0, classe_exposition="XC1"
    )
    projet.membres.add(utilisateur)
    batiment = Batiment.objects.create(projet=projet, nom="Bâtiment A")
    return Niveau.objects.create(batiment=batiment, nom="R+1")


@pytest.fixture
def poteau_reference(niveau):
    """Cas de référence Arche 03-0188SSLLG_EC2 (1 T = 10 kN)."""
    return Poteau.objects.create(
        niveau=niveau,
        repere="P1",
        type_section="rectangulaire",
        b=0.30,
        h=0.30,
        L0=2.83,
        d_prime=0.035,
        G=1209.0,
        Q=200.0,
        taux_travail_min=1.0,
    )


@pytest.mark.django_db
def test_traduction_des_entrees(poteau_reference):
    entree = poteau_vers_entree(poteau_reference)

    assert entree.fck == 30.0  # hérité du projet
    assert entree.type_section == "rectangulaire"
    assert entree.duree_resistance_feu is None  # "" traduit en None


@pytest.mark.django_db
def test_calcul_reference_arche(poteau_reference, niveau, utilisateur):
    type_poteau = TypePoteau.objects.create(niveau=niveau, nom="Type 1")

    calcul = calculer_poteau(poteau_reference, type_poteau, utilisateur)

    assert calcul.As == pytest.approx(33.94, rel=1e-2)
    assert calcul.version_moteur == VERSION_MOTEUR
    assert calcul.pk is None  # construit, pas enregistré


@pytest.mark.django_db
def test_les_entrees_sont_figees(poteau_reference, niveau, utilisateur):
    type_poteau = TypePoteau.objects.create(niveau=niveau, nom="Type 1")
    calcul = calculer_poteau(poteau_reference, type_poteau, utilisateur)
    calcul.save()

    poteau_reference.L0 = 6.0
    poteau_reference.save()

    calcul.refresh_from_db()
    assert calcul.L0 == 2.83  # la note ne bouge pas


@pytest.mark.django_db
def test_ferraillage_impossible_est_archive(poteau_reference, niveau, utilisateur):
    """Le champ traverse la traduction, quelle que soit sa valeur."""
    type_poteau = TypePoteau.objects.create(niveau=niveau, nom="Type 1")
    resultat = MethodeSimplifiee().calculer(poteau_vers_entree(poteau_reference))

    calcul = calculer_poteau(poteau_reference, type_poteau, utilisateur)

    assert calcul.ferraillage_impossible == resultat.ferraillage_impossible
