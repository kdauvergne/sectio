import pytest


@pytest.mark.django_db
def test_inscription_puis_connexion(client):
    reponse = client.post(
        "/api/inscription/",
        {
            "email": "nouvelle@exemple.fr",
            "first_name": "Camille",
            "last_name": "Martin",
            "password": "UnMotDePasseSolide42",
        },
        content_type="application/json",
    )

    assert reponse.status_code == 201
    assert "password" not in reponse.json()

    connexion = client.post(
        "/api/token/",
        {"email": "nouvelle@exemple.fr", "password": "UnMotDePasseSolide42"},
        content_type="application/json",
    )
    assert connexion.status_code == 200
