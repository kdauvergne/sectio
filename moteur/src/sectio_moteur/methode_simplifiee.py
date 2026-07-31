from .exceptions import TypeSectionInvalideException, DimensionsManquantesException
from .modeles import TYPE_RECTANGULAIRE, TYPE_CIRCULAIRE
from .modeles import PoteauInput, ResultatPoteau
from .interfaces import MethodeCalculPoteauInterface
from math import sqrt


class MethodeSimplifiee(MethodeCalculPoteauInterface):

    HYPOTHESES_NON_VERIFIEES = (
        "compression centrée",
        "armatures symétriques (rect: 1/2 par face ; circ: 6 barres réparties)",
        "chargement ≥ 28 jours",
    )

    def est_applicable(self, entree: PoteauInput) -> list[str]:
        """
        7 conditions d'application.
        3 conditions sur 7 ne sont pas vérifiables avec les champs actuels de PoteauInput (hypothèses ingénieur).
        - λ ≤ 120
        - 20 ≤ fck ≤ 50
        - h ≥ 0,15 m
        - d' ≤ min(0,3·h ; 100mm)
        """
        liste_violations = []
        lambda_ = calculer_lambda(entree)

        dim_ref = plus_petite_dimension(entree)
        limite_d_prime = min(0.3 * dim_ref, 100 * 0.001)

        if lambda_ > 120:
            liste_violations.append(f"λ={lambda_:.2f} dépasse la limite de 120")

        if not (20 <= entree.fck <= 50):
            liste_violations.append(f"fck={entree.fck} hors de la plage [20, 50] MPa")

        if dim_ref < 0.15:
            liste_violations.append(
                f"La plus petite dimension ({dim_ref} m) doit être supérieure à 0,15 m"
            )

        if not entree.d_prime <= limite_d_prime:
            liste_violations.append(
                f"d'={entree.d_prime} dépasse la limite {limite_d_prime}"
            )

        return liste_violations

    def calculer(self, entree: PoteauInput) -> ResultatPoteau:
        raise NotImplementedError

    def verifier(self, as_propose: float, entree: PoteauInput) -> ResultatPoteau:
        raise NotImplementedError


def calculer_lambda(entree: PoteauInput) -> float:
    """Calcule λ en fonction du type de la section (rectangulaire ou circulaire).
    Formule (rectangulaire) : λ = L0·√12 / min(b, h)
    Formule (circulaire) : λ = 4·L0 / D (D = diamètre, pas de min() puisque la section est symétrique dans toutes les directions).
    """
    if entree.type_section == TYPE_RECTANGULAIRE:
        if entree.b is None or entree.h is None:
            raise DimensionsManquantesException()
        return entree.L0 * sqrt(12) / min(entree.b, entree.h)
    elif entree.type_section == TYPE_CIRCULAIRE:
        if entree.diametre is None:
            raise DimensionsManquantesException()
        return 4 * entree.L0 / entree.diametre
    else:
        raise TypeSectionInvalideException()


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
