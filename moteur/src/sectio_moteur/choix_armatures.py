from .modeles import TYPE_CIRCULAIRE, TYPE_RECTANGULAIRE
from .modeles import PoteauInput
from .exceptions import (
    DimensionsManquantesException,
    TypeSectionInvalideException,
    FerraillageImpossibleException,
)
from .geometrie import plus_petite_dimension
from math import pi, floor, ceil

# Constantes utilisées dans le choix d'armatures
DIAMETRES_NORMALISES = [
    8,
    10,
    12,
    14,
    16,
    20,
    25,
    32,
    40,
]  # Diamètres de barre à tester, normalisés dans le métier

ESPACEMENT_MIN_BARRES_MM = 30.0  # EC2 art.8.2(2)
M_VERS_MM = 1000.0  # convertit b/h/diametre (m, PoteauInput) en mm

# Constantes normées par l'EC2 pour les cadres
DIAMETRE_CADRE_MIN_MM = 6.0
ESPACEMENT_CADRES_MAX_MM = 400.0
FACTEUR_ESPACEMENT_DIAMETRE = 20
FACTEUR_ESPACEMENT_EXTREMITES = 0.6
FACTEUR_DIAMETRE_CADRE = 4


def choix_armatures(
    as_theorique: float,  # cm2
    as_max: float,  # cm2
    entree: PoteauInput,  # geometrie + type_section + d_prime
) -> list[tuple[int, int]]:
    """Combinaisons (n, Øl) reellement constructibles pour un As theorique.

    Balaie les diamètres normalisés (DIAMETRES_NORMALISES).
    Pour chacun, calcule le nombre de barres nécessaire (arrondi et
    ajusté par ajuster_nombre_barres), puis ne retient la combinaison
    que si elle passe deux filtres indépendants :
    - la quantité d'acier reste sous as_max (filtre réglementaire),
    - et le nombre de barres tient physiquement dans le périmètre utile
    de la section (filtre géométrique, calculer_n_max_geometrique).
    Hypothese V1 actée : cnom = d'.

    Paramètres:
        as_theorique: aire d'acier théorique visée, en cm².
        as_max: aire d'acier maximale réglementaire, en cm² (calculer_as_max).
        entree: géométrie, type_section et d_prime du poteau.

    Retourne :
        Liste de couples (n, diametre_mm), un par diamètre normalisé qui
        passe les deux filtres. Peut contenir plusieurs alternatives.

    Erreurs:
        FerraillageImpossibleException: si aucun diamètre normalisé ne
        passe les deux filtres.
    """

    combinaisons = []

    for diametre in DIAMETRES_NORMALISES:
        aire = calculer_aire_barre(diametre)
        n = ceil(as_theorique / aire)
        n = ajuster_nombre_barres(n, entree.type_section)
        as_reel = n * aire
        if as_reel > as_max:
            continue
        if n > calculer_n_max_geometrique(entree, diametre):
            continue

        combinaisons.append((n, diametre))

    if not combinaisons:
        raise FerraillageImpossibleException(as_theorique, as_max)

    return combinaisons


def choisir_combinaison_par_defaut(
    combinaisons: list[tuple[int, int]],
) -> tuple[int, int]:
    """Retient la combinaison par défaut parmi celles proposées par choix_armatures.

    Utilisée par calculer(): parmi toutes les combinaisons constructibles,
    retient celle qui a le moins de barres — en cas d'égalité du nombre de
    barres, retient le plus petit diamètre parmi les ex-aequo (évite le
    surdimensionnement inutile).

    Paramètres:
        combinaisons: liste de couples (n, diametre_mm) déjà validés par
        choix_armatures (filtres réglementaire et géométrique passés).

    Retourne:
        Le couple (n, diametre_mm) avec n minimal ; en cas d'égalité de n,
        celui avec le diametre_mm le plus petit.
    """

    return min(combinaisons, key=lambda c: (c[0], c[1]))


def calculer_aire_barre(diametre_mm: float) -> float:
    """
    Calcule l'aire de la section d'une barre d'armature. Avec Aφ l'aire de la section et  Øl le diamètre nominal.
    Formule : Aφ = π × Øl² / 4
    """
    return (pi * diametre_mm**2 / 4) / 100


def ajuster_nombre_barres(n: int, type_section: str) -> int:
    """
    Ajuste le nombre de barres longitudinales selon le type de section.

    Pour une section rectangulaire, le nombre de barres est rendu pair afin
    de permettre une disposition symétrique des armatures.

    Pour une section circulaire, un minimum de 6 barres est imposé afin de
    respecter les dispositions constructives courantes des armatures.

    Paramètres:
        n (int): Nombre de barres calculé après dimensionnement.
        type_section (str): Type de section du poteau (rectangulaire ou circulaire).

    Retourne:
        int: Nombre de barres ajusté selon les règles de disposition.

    Erreur:
        Lève TypSectionInvalideException si le type de section n'est pas rectangulaire ou circulaire.
    """

    if type_section == TYPE_RECTANGULAIRE:
        if n < 4:
            n = 4
        elif n % 2 != 0:
            n += 1
    elif type_section == TYPE_CIRCULAIRE:
        n = max(n, 6)
    else:
        raise TypeSectionInvalideException
    return n


def calculer_n_max_geometrique(entree: PoteauInput, diametre_mm: float) -> int:
    """
    Calcule le nombre maximal de barres pouvant être disposées dans la section.

    Le périmètre utile (intérieur, après enrobage d') est divisé par
    l'entraxe minimal entre deux barres — la distance axe à axe, égale
    au diamètre d'une barre plus l'espacement libre minimal entre elles
    (ESPACEMENT_MIN_BARRES_MM, art. 8.2(2)).

    Paramètres:
        entree: Données géométriques de la section.
        diametre_mm (float): Diamètre des armatures longitudinales en mm.

    Retourne:
        Nombre maximal de barres admissible géométriquement arrondi à l'entier inférieur.

    Erreurs:
        DimensionsManquantesException: si b/h ou diametre valent None.
        TypeSectionInvalideException: si type_section est inconnu.
    """
    if entree.type_section == TYPE_RECTANGULAIRE:
        if entree.b is None or entree.h is None:
            raise DimensionsManquantesException()
        perimetre_utile = 2 * (
            (entree.b * M_VERS_MM - 2 * entree.d_prime * M_VERS_MM)
            + (entree.h * M_VERS_MM - 2 * entree.d_prime * M_VERS_MM)
        )
    elif entree.type_section == TYPE_CIRCULAIRE:
        if entree.diametre is None:
            raise DimensionsManquantesException()
        perimetre_utile = pi * (
            entree.diametre * M_VERS_MM - 2 * entree.d_prime * M_VERS_MM
        )
    else:
        raise TypeSectionInvalideException()

    entraxe = diametre_mm + max(diametre_mm, ESPACEMENT_MIN_BARRES_MM)
    n_max = floor(perimetre_utile / entraxe)
    return n_max


def calculer_armatures_transversales(
    diametre_long_mm: float, entree: PoteauInput
) -> tuple[float, float, float]:
    """Calcule les cadres (armatures transversales) qui ceinturent
    les barres longitudinales — leur diamètre, et l'espacement entre eux.
    Art. 9.5.3.(Øt, e_central, e_extremites), les 3 en mm.

    Paramètres :
        diametre_long_mm : diamètre des barres longitudinales, en mm.
        entree : géométrie du poteau (pour plus_petite_dimension, en mètres,
        convertie en mm via M_VERS_MM avant comparaison)

    Retourne:
        (diametre_cadre, e_central, e_extremites), les 3 en mm :
            diametre_cadre = max(6 ; Øl/4)
            e_central       = min(20·Øl ; plus petite dimension ; 400)
            e_extremites     = 0,6 · e_central
    """
    diametre_cadre = max(
        DIAMETRE_CADRE_MIN_MM, diametre_long_mm / FACTEUR_DIAMETRE_CADRE
    )
    e_central = min(
        FACTEUR_ESPACEMENT_DIAMETRE * diametre_long_mm,
        plus_petite_dimension(entree) * M_VERS_MM,
        ESPACEMENT_CADRES_MAX_MM,
    )
    e_extremites = FACTEUR_ESPACEMENT_EXTREMITES * e_central

    return diametre_cadre, e_central, e_extremites
