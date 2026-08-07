from dataclasses import FrozenInstanceError

import pytest

from sectio_moteur.modeles import PoteauInput, ResultatPoteau


def test_poteau_input_est_immuable():

    poteau = PoteauInput(
        G=100,
        Q=50,
        fck=30,
        fyk=500,
        L0=3,
        d_prime=0.04,
        type_section="circulaire",
        diametre=500
    )

    assert poteau.diametre == 500
    assert poteau.b is None
    assert poteau.h is None
    
def test_creation_resultat_poteau():

    resultat = ResultatPoteau(
        As=12.5,
        NRd=1500,
        taux_travail=1.2,
        as_min_gouverne=False,
        NEd=1200,
        lambda_=50,
        alpha=0.8,
        kh=1,
        ks=1,
        rho=0.02,
        delta=0.1
    )

    assert resultat.As == 12.5
    assert resultat.NRd == 1500
    assert resultat.taux_travail == 1.2

def test_resultat_poteau_est_immuable():

    resultat = ResultatPoteau(
        As=12.5,
        NRd=1500,
        taux_travail=1.2,
        as_min_gouverne=False,
        NEd=1200,
        lambda_=50,
        alpha=0.8,
        kh=1,
        ks=1,
        rho=0.02,
        delta=0.1
    )

    with pytest.raises(FrozenInstanceError):
        resultat.NRd = 2000 # type: ignore
        
def test_resultat_poteau_cree_sans_armatures_transversales():

    resultat = ResultatPoteau(
        As=12.5,
        NRd=1500,
        taux_travail=1.2,
        as_min_gouverne=False,
        NEd=1200,
        lambda_=50,
        alpha=0.8,
        kh=1,
        ks=1,
        rho=0.02,
        delta=0.1
    )

    assert resultat.As == 12.5
    assert resultat.NRd == 1500
    assert resultat.taux_travail == 1.2