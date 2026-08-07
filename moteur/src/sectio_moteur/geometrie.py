from math import pi

from .exceptions import DimensionsManquantesException, TypeSectionInvalideException
from .modeles import TYPE_CIRCULAIRE, TYPE_RECTANGULAIRE, PoteauInput


def plus_petite_dimension(entree: PoteauInput) -> float:
    """
    Retourne la plus petite dimension de la section, au sens EC2 du "h" normatif
    (utilisée pour les conditions h≥0,15m et d'≤min(0,3h;100mm) de la méthode simplifiée).
    Valeur essentielle pour le calcul.

    Rectangulaire : min(b, h). Circulaire : diametre (section symétrique).

    Raise DimensionsManquantesException si b/h ou diametre valent None.
    Raise TypeSectionInvalideException si type_section est inconnu.
    """
    if entree.type_section == TYPE_RECTANGULAIRE:
        if entree.b is None or entree.h is None:
            raise DimensionsManquantesException()
        return min(entree.b, entree.h)
    elif entree.type_section == TYPE_CIRCULAIRE:
        if entree.diametre is None:
            raise DimensionsManquantesException()
        return entree.diametre
    else:
        raise TypeSectionInvalideException()


def calculer_aire_beton(entree: PoteauInput) -> float:
    """Aire de la section de béton Ac, en m².

    Rectangulaire : Ac = b · h.  Circulaire : Ac = π · D² / 4.
    """
    if entree.type_section == TYPE_RECTANGULAIRE:
        if entree.b is None or entree.h is None:
            raise DimensionsManquantesException()
        return entree.b * entree.h
    elif entree.type_section == TYPE_CIRCULAIRE:
        if entree.diametre is None:
            raise DimensionsManquantesException()
        return pi * entree.diametre**2 / 4
    else:
        raise TypeSectionInvalideException(entree.type_section)
