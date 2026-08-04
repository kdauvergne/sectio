from .modeles import TYPE_CIRCULAIRE, TYPE_RECTANGULAIRE
from .modeles import PoteauInput
from .exceptions import DimensionsManquantesException, TypeSectionInvalideException
from math import pi, floor

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


#! TODO
def choix_armatures(
    as_theorique: float,  # cm2
    as_max: float,  # cm2
    entree: PoteauInput,  # geometrie + type_section + d_prime
) -> list[tuple[int, int]]:
    """Combinaisons (n, Øl) constructibles pour un As théorique donné.

    Hypothèse V1 actée : cnom = d' en m, converti en mm ici,
    car les diamètres de barres sont en mm.
    """
    cnom_mm = entree.d_prime * M_VERS_MM  # M_VERS_MM = 1000.0

    raise NotImplementedError


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
    """
    if type_section == TYPE_RECTANGULAIRE:
        if n % 2 != 0:
            n += 1
    elif type_section == TYPE_CIRCULAIRE:
        n = max(n, 6)
    return n


def calculer_n_max_geometrique(entree: PoteauInput, diametre_mm: float) -> int:
    """
    Calcule le nombre maximal de barres pouvant être disposées dans la section.

    Paramètres:
        entree: Données géométriques de la section.
        diametre_mm (float): Diamètre des armatures longitudinales en mm.

    Retourne:
        int: Nombre maximal de barres admissible géométriquement.
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

    n_max = floor(perimetre_utile / max(diametre_mm, ESPACEMENT_MIN_BARRES_MM))
    return n_max
