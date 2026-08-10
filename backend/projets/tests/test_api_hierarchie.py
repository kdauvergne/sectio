import pytest

from projets.models import Batiment, Niveau, Poteau, Projet


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


@pytest.fixture
def projet(utilisateur):
    projet = Projet.objects.create(nom="Résidence Garonne", classe_exposition="XC1")
    projet.membres.add(utilisateur)
    return projet


@pytest.fixture
def niveau(projet):
    batiment = Batiment.objects.create(projet=projet, nom="Bâtiment A")
    return Niveau.objects.create(batiment=batiment, nom="R+1")


def ligne_poteau(niveau, repere):
    return {
        "niveau": niveau.pk,
        "repere": repere,
        "type_section": "rectangulaire",
        "b": 0.30,
        "h": 0.30,
        "L0": 3.0,
        "d_prime": 0.035,
        "G": 1209.0,
        "Q": 200.0,
    }


@pytest.mark.django_db
def test_creation_batiment_herite_des_hypotheses(client, utilisateur, projet):
    client.force_login(utilisateur)

    reponse = client.post(
        "/api/batiments/",
        {"nom": "Bâtiment A", "projet": projet.pk},
        content_type="application/json",
    )

    assert reponse.status_code == 201
    assert reponse.json()["fck"] == projet.fck
    assert reponse.json()["classe_exposition"] == "XC1"


@pytest.mark.django_db
def test_creation_refusee_sur_un_projet_etranger(
    client, utilisateur, autre_utilisateur
):
    projet_etranger = Projet.objects.create(nom="Privé", classe_exposition="XC1")
    projet_etranger.membres.add(autre_utilisateur)

    client.force_login(utilisateur)
    reponse = client.post(
        "/api/batiments/",
        {"nom": "Intrus", "projet": projet_etranger.pk},
        content_type="application/json",
    )

    assert reponse.status_code == 400
    assert Batiment.objects.count() == 0


@pytest.mark.django_db
def test_detail_projet_contient_ses_batiments(client, utilisateur, projet):
    Batiment.objects.create(projet=projet, nom="Bâtiment A")

    client.force_login(utilisateur)
    reponse = client.get(f"/api/projets/{projet.pk}/")

    assert reponse.status_code == 200
    assert len(reponse.json()["batiments"]) == 1


@pytest.mark.django_db
def test_filtrage_par_parametre(client, utilisateur, projet):
    batiment = Batiment.objects.create(projet=projet, nom="Bâtiment A")
    Niveau.objects.create(batiment=batiment, nom="R+1")

    autre = Batiment.objects.create(projet=projet, nom="Bâtiment B")
    Niveau.objects.create(batiment=autre, nom="R+2")

    client.force_login(utilisateur)
    reponse = client.get(f"/api/niveaux/?batiment={batiment.pk}")

    assert reponse.json()["count"] == 1


@pytest.mark.django_db
def test_poteau_rectangulaire_sans_dimensions_refuse(client, utilisateur, projet):
    batiment = Batiment.objects.create(projet=projet, nom="Bâtiment A")
    niveau = Niveau.objects.create(batiment=batiment, nom="R+1")

    client.force_login(utilisateur)
    reponse = client.post(
        "/api/poteaux/",
        {
            "niveau": niveau.pk,
            "repere": "P1",
            "type_section": "rectangulaire",
            "L0": 3.0,
            "d_prime": 0.035,
            "G": 1209.0,
            "Q": 200.0,
        },
        content_type="application/json",
    )

    assert reponse.status_code == 400


@pytest.mark.django_db
def test_creation_en_lot(client, utilisateur, niveau):
    client.force_login(utilisateur)

    reponse = client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1"), ligne_poteau(niveau, "P2")],
        content_type="application/json",
    )

    assert reponse.status_code == 201
    assert Poteau.objects.count() == 2


@pytest.mark.django_db
def test_lot_atomique_rien_enregistre_si_une_ligne_invalide(
    client, utilisateur, niveau
):
    client.force_login(utilisateur)

    invalide = ligne_poteau(niveau, "P2")
    invalide["b"] = None  # rectangulaire sans b

    reponse = client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1"), invalide],
        content_type="application/json",
    )

    assert reponse.status_code == 400
    assert Poteau.objects.count() == 0
    assert "1" in reponse.json()  # la seconde ligne est en faute
    assert "0" not in reponse.json()  # la première ne l'est pas


@pytest.mark.django_db
def test_lot_herite_des_hypotheses(client, utilisateur, niveau):
    client.force_login(utilisateur)

    client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1"), ligne_poteau(niveau, "P2")],
        content_type="application/json",
    )

    for poteau in Poteau.objects.all():
        assert poteau.fck == niveau.fck
        assert poteau.classe_exposition == niveau.classe_exposition


@pytest.mark.django_db
def test_repere_en_double_dans_le_lot_refuse(client, utilisateur, niveau):
    client.force_login(utilisateur)

    reponse = client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1"), ligne_poteau(niveau, "P1")],
        content_type="application/json",
    )

    assert reponse.status_code == 400
    assert Poteau.objects.count() == 0


@pytest.mark.django_db
def test_repere_en_double_avec_la_base_refuse(client, utilisateur, niveau):
    client.force_login(utilisateur)
    client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1")],
        content_type="application/json",
    )

    reponse = client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1")],
        content_type="application/json",
    )

    assert reponse.status_code == 400
    assert Poteau.objects.count() == 1


@pytest.mark.django_db
def test_meme_repere_dans_deux_niveaux_accepte(client, utilisateur, niveau):
    autre_niveau = Niveau.objects.create(batiment=niveau.batiment, nom="R+2")

    client.force_login(utilisateur)
    reponse = client.post(
        "/api/poteaux/",
        [ligne_poteau(niveau, "P1"), ligne_poteau(autre_niveau, "P1")],
        content_type="application/json",
    )

    assert reponse.status_code == 201
    assert Poteau.objects.count() == 2
