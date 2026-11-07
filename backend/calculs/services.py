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
    """Range les poteaux par section et matériaux identiques.

    Un Calcul fige un seul fck et un seul fyk : deux poteaux de matériaux
    différents ne peuvent pas partager un même type.

    Retourne un dictionnaire : {(type, b, h, diametre, fck, fyk): [poteaux]}
    """
    groupes: dict = {}

    for poteau in poteaux:
        cle = (
            poteau.type_section,
            poteau.b,
            poteau.h,
            poteau.diametre,
            poteau.fck,
            poteau.fyk,
        )
        groupes.setdefault(cle, []).append(poteau)

    return groupes


def _ordre_section(cle: tuple) -> tuple:
    """Clé de tri d'un groupe : type de section, dimensions, puis matériaux.

    Les dimensions absentes (None) sont remplacées par 0 pour rester comparables.
    """
    return tuple(0.0 if valeur is None else valeur for valeur in cle)


def calculer_niveau(niveau: Niveau, utilisateur) -> tuple[list[TypePoteau], list]:
    """Calcule tous les poteaux d'un niveau et met à jour ses types de ferraillage.

    Les types sont numérotés « Type 1 », « Type 2 »… sur tout le niveau, dans
    l'ordre des sections puis des rôles proposés par le classement.

    Un recalcul réutilise les types existants pour conserver l'historique des
    Calcul : chaque type proposé reprend le type existant qui couvrait déjà le
    plus de ses poteaux. Les types restés sans poteau sont supprimés (le MCD
    impose au moins un poteau par type), avec leurs calculs.

    Retourne (types, echecs).
    """
    poteaux = list(Poteau.objects.filter(niveau=niveau))
    par_reference = {str(p.pk): p for p in poteaux}

    types_proposes = []
    echecs = []

    groupes = grouper_par_section(poteaux)
    for cle in sorted(groupes, key=_ordre_section):
        entrees = [poteau_vers_entree(p) for p in groupes[cle]]
        types_groupe, echecs_groupe = proposer_types(entrees, MethodeSimplifiee())
        types_proposes.extend(types_groupe)
        echecs.extend(echecs_groupe)

    types_disponibles = list(TypePoteau.objects.filter(niveau=niveau).order_by("pk"))
    # Rattachements d'avant le recalcul : la boucle ci-dessous les modifie.
    ancien_type = {p.pk: p.type_poteau_id for p in poteaux}
    types = []

    for numero, type_propose in enumerate(types_proposes, start=1):
        couverts = [par_reference[e.reference] for e in type_propose.poteaux_couverts]
        type_poteau = _reprendre_type(couverts, types_disponibles, ancien_type)
        if type_poteau is None:
            type_poteau = TypePoteau(niveau=niveau)
        else:
            types_disponibles.remove(type_poteau)

        types.append(
            _enregistrer_type(
                type_poteau,
                f"Type {numero}",
                type_propose,
                couverts,
                par_reference,
                utilisateur,
            )
        )

    # Poteaux en échec : ils ne doivent pas rester rattachés à un ancien type.
    for entree, _ in echecs:
        poteau = par_reference[entree.reference]
        if poteau.type_poteau_id is not None:
            poteau.type_poteau = None
            poteau.save(update_fields=["type_poteau"])

    TypePoteau.objects.filter(pk__in=[t.pk for t in types_disponibles]).delete()

    return types, echecs


def _reprendre_type(
    couverts: list[Poteau], types_disponibles: list[TypePoteau], ancien_type: dict
) -> TypePoteau | None:
    """Type existant qui couvrait déjà le plus de ces poteaux, ou None.

    À égalité, le plus ancien (types_disponibles est trié par pk).
    """
    meilleur, meilleur_score = None, 0
    for candidat in types_disponibles:
        score = sum(1 for p in couverts if ancien_type[p.pk] == candidat.pk)
        if score > meilleur_score:
            meilleur, meilleur_score = candidat, score
    return meilleur


def _enregistrer_type(
    type_poteau: TypePoteau,
    nom: str,
    type_propose,
    couverts: list[Poteau],
    par_reference: dict,
    utilisateur,
) -> TypePoteau:
    """Nomme le type, lui ajoute un nouveau Calcul et y rattache ses poteaux."""
    type_poteau.nom = nom
    type_poteau.save()

    poteau_representatif = par_reference[type_propose.poteau_representatif.reference]
    calcul = resultat_vers_calcul(
        type_propose.resultat, poteau_representatif, type_poteau, utilisateur
    )
    calcul.save()

    type_poteau.calcul_actuel = calcul  # type: ignore[assignment]
    type_poteau.save(update_fields=["calcul_actuel"])

    for poteau in couverts:
        if poteau.type_poteau_id != type_poteau.pk:
            poteau.type_poteau = type_poteau
            poteau.save(update_fields=["type_poteau"])

    return type_poteau
