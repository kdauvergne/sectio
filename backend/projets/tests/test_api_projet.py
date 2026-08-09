import pytest

from projets.models import Projet


@pytest.fixture
def utilisateur(django_user_model):
    return django_user_model.objects.create_user(
        email="pierre@exemple.fr",
        first_name="Pierre",
        last_name="Dupont",
        password="motdepasse",
    )


@pytest.fixture
def autre_utilisateur(django_user_model):
    return django_user_model.objects.create_user(
        email="marie@exemple.fr",
        first_name="Marie",
        last_name="Lefebvre",
        password="motdepasse",
    )


@pytest.mark.django_db
def test_liste_refusee_si_non_connecte(client):
    reponse = client.get("/api/projets/")
    assert reponse.status_code == 401


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


@pytest.mark.django_db
def test_createur_est_membre(client, utilisateur):
    client.force_login(utilisateur)

    reponse = client.post(
        "/api/projets/",
        {"nom": "Résidence Garonne", "classe_exposition": "XC1"},
        content_type="application/json",
    )

    assert reponse.status_code == 201
    projet = Projet.objects.get(nom="Résidence Garonne")
    assert utilisateur in projet.membres.all()


@pytest.mark.django_db
def test_projet_autrui_prive(client, utilisateur, autre_utilisateur):
    projet = Projet.objects.create(nom="Privé", classe_exposition="XC1")
    projet.membres.add(autre_utilisateur)

    client.force_login(utilisateur)
    reponse = client.get("/api/projets/")

    assert reponse.json()["count"] == 0


@pytest.mark.django_db
def test_detail_projet_etranger_renvoie_404(client, utilisateur, autre_utilisateur):
    projet = Projet.objects.create(nom="Privé", classe_exposition="XC1")
    projet.membres.add(autre_utilisateur)

    client.force_login(utilisateur)
    reponse = client.get(f"/api/projets/{projet.pk}/")

    assert reponse.status_code == 404


@pytest.mark.django_db
def test_obtention_jeton(client, utilisateur):
    reponse = client.post(
        "/api/token/",
        {"email": "pierre@exemple.fr", "password": "motdepasse"},
        content_type="application/json",
    )

    assert reponse.status_code == 200
    assert "access" in reponse.json()
    assert "refresh" in reponse.json()


@pytest.mark.django_db
def test_acces_avec_jeton(client, utilisateur):
    jeton = client.post(
        "/api/token/",
        {"email": "pierre@exemple.fr", "password": "motdepasse"},
        content_type="application/json",
    ).json()["access"]

    reponse = client.get(
        "/api/projets/",
        headers={"Authorization": f"Bearer {jeton}"},
    )

    assert reponse.status_code == 200


@pytest.mark.django_db
def test_deconnexion_invalide_le_refresh(client, utilisateur):
    jetons = client.post(
        "/api/token/",
        {"email": "pierre@exemple.fr", "password": "motdepasse"},
        content_type="application/json",
    ).json()

    deconnexion = client.post(
        "/api/token/blacklist/",
        {"refresh": jetons["refresh"]},
        content_type="application/json",
    )
    assert deconnexion.status_code == 200

    # Le refresh mis en liste noire ne doit plus rien produire
    renouvellement = client.post(
        "/api/token/refresh/",
        {"refresh": jetons["refresh"]},
        content_type="application/json",
    )
    assert renouvellement.status_code == 401
