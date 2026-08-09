import pytest

from projets.models import Projet


@pytest.fixture
def utilisateur(django_user_model):
    return django_user_model.objects.create_user(
        username="pierre",
        email="pierre@exemple.fr",
        password="motdepasse",
    )


@pytest.mark.django_db
def test_liste_refusee_si_non_connecte(client):
    reponse = client.get("/api/projets/")
    assert reponse.status_code == 403


@pytest.mark.django_db
def test_creation_projet(client, utilisateur):
    client.force_login(utilisateur)

    reponse = client.post(
        "/api/projets/",
        {
            "nom": "Résidence Garonne",
            "classe_exposition": "XC1",
            "membres": [utilisateur.pk],
        },
        content_type="application/json",
    )

    assert reponse.status_code == 201
    assert Projet.objects.count() == 1
    assert reponse.json()["fck"] == 45.0
