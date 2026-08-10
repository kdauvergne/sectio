"""Seul point de contact entre Django et sectio_moteur.

Aucun autre module du backend ne doit importer sectio_moteur.
"""

from importlib.metadata import version

from sectio_moteur.exceptions import (  # noqa: F401
    MethodeNonApplicableException,
    SectioException,
)
from sectio_moteur.methode_simplifiee import MethodeSimplifiee
from sectio_moteur.modeles import PoteauInput, ResultatPoteau
from sectio_moteur.classification.classement import proposer_types

from projets.models import Niveau, Poteau, TypePoteau

from .models import Calcul

VERSION_MOTEUR = version("sectio-moteur")


def poteau_vers_entree(poteau: Poteau) -> PoteauInput:
    """Traduit un Poteau Django en PoteauInput du moteur."""
    return PoteauInput(
        G=poteau.G,
        Q=poteau.Q,
        fck=poteau.fck,
        fyk=poteau.fyk,
        L0=poteau.L0,
        d_prime=poteau.d_prime,
        type_section=poteau.type_section,
        b=poteau.b,
        h=poteau.h,
        diametre=poteau.diametre,
        taux_travail_min=poteau.taux_travail_min,
        duree_resistance_feu=poteau.duree_resistance_feu or None,
        expose_un_seul_cote=poteau.expose_un_seul_cote,
        reference=str(poteau.pk),
    )


def resultat_vers_calcul(
    resultat: ResultatPoteau,
    poteau: Poteau,
    type_poteau,
    utilisateur,
) -> Calcul:
    """Archive un ResultatPoteau en Calcul immuable.

    Recopie les entrées ET les sorties : une note
    de calcul doit rester reconstituable même si le Poteau
    est modifié ensuite.
    """
    return Calcul(
        type_poteau=type_poteau,
        calcule_par=utilisateur,
        methode="methode_simplifiee",
        version_moteur=VERSION_MOTEUR,
        # Entrées figées
        type_section=poteau.type_section,
        b=poteau.b,
        h=poteau.h,
        diametre=poteau.diametre,
        L0=poteau.L0,
        d_prime=poteau.d_prime,
        G=poteau.G,
        Q=poteau.Q,
        fck=poteau.fck,
        fyk=poteau.fyk,
        classe_exposition=poteau.classe_exposition,
        taux_travail_min=poteau.taux_travail_min,
        # Résultats
        As=resultat.As,
        NRd=resultat.NRd,
        NEd=resultat.NEd,
        as_min_gouverne=resultat.as_min_gouverne,
        # Valeurs intermédiaires
        lambda_elancement=resultat.lambda_,
        alpha=resultat.alpha,
        kh=resultat.kh,
        ks=resultat.ks,
        rho=resultat.rho,
        delta=resultat.delta,
        taux_travail=resultat.taux_travail,
        # Armatures
        nombre_barres_longitudinales=resultat.nombre_barres_longitudinales,
        diametre_longitudinal=resultat.diametre_longitudinal,
        diametre_cadres=resultat.diametre_cadres,
        espacement_central=resultat.espacement_central,
        espacement_extremites=resultat.espacement_extremites,
        ferraillage_impossible=resultat.ferraillage_impossible,
    )


def calculer_poteau(poteau: Poteau, type_poteau, utilisateur) -> Calcul:
    """Calcule un poteau et retourne le Calcul correspondant (non enregistré).

    Laisse remonter les exceptions du moteur : leur traduction en réponse
    HTTP appartient à la couche vue.
    """
    entree = poteau_vers_entree(poteau)
    resultat = MethodeSimplifiee().calculer(entree)
    return resultat_vers_calcul(resultat, poteau, type_poteau, utilisateur)


def verifier_poteau(
    poteau: Poteau, as_propose: float, type_poteau, utilisateur
) -> Calcul:
    """Vérifie qu'un As choisi convient, sans résoudre l'équation.

    Sert à la réaffectation manuelle d'un poteau vers un autre type :
    signale sans jamais corriger.
    """
    entree = poteau_vers_entree(poteau)
    resultat = MethodeSimplifiee().verifier(as_propose, entree)
    return resultat_vers_calcul(resultat, poteau, type_poteau, utilisateur)


def grouper_par_section(poteaux: list[Poteau]) -> dict:
    """Range les poteaux par section identique.

    Retourne un dictionnaire : {(type, b, h, diametre): [poteaux]}
    """
    groupes: dict = {}

    for poteau in poteaux:
        cle = (poteau.type_section, poteau.b, poteau.h, poteau.diametre)
        groupes.setdefault(cle, []).append(poteau)

    return groupes


def calculer_niveau(niveau: Niveau, utilisateur) -> tuple[list[TypePoteau], list]:
    """Calcule tous les poteaux d'un niveau et crée les types de ferraillage.

    Retourne (types_crees, echecs).
    """
    poteaux = list(Poteau.objects.filter(niveau=niveau))
    par_reference = {str(p.pk): p for p in poteaux}

    types_crees = []
    echecs = []

    for groupe in grouper_par_section(poteaux).values():
        entrees = [poteau_vers_entree(p) for p in groupe]
        types_proposes, echecs_groupe = proposer_types(entrees, MethodeSimplifiee())
        echecs.extend(echecs_groupe)

        for numero, type_propose in enumerate(types_proposes, start=1):
            type_poteau = _enregistrer_type(
                type_propose, numero, niveau, par_reference, utilisateur
            )
            types_crees.append(type_poteau)

    return types_crees, echecs


def _enregistrer_type(
    type_propose, numero: int, niveau: Niveau, par_reference: dict, utilisateur
) -> TypePoteau:
    """Crée un TypePoteau, son Calcul, et y rattache les poteaux couverts."""
    poteau_representatif = par_reference[type_propose.poteau_representatif.reference]

    type_poteau = TypePoteau.objects.create(niveau=niveau, nom=f"Type {numero}")

    calcul = resultat_vers_calcul(
        type_propose.resultat, poteau_representatif, type_poteau, utilisateur
    )
    calcul.save()

    type_poteau.calcul_actuel = calcul  # type: ignore[assignment]
    type_poteau.save(update_fields=["calcul_actuel"])

    for entree in type_propose.poteaux_couverts:
        poteau = par_reference[entree.reference]
        poteau.type_poteau = type_poteau
        poteau.save(update_fields=["type_poteau"])

    return type_poteau
