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


"""
Fonctions indépendantes de calculs purs, nécessaires au calcul final (calculer_lambda, calculer_alpha, calculer_ks, calculer_kh, plus_petite_dimension)
Rôle dans le moteur : λ, α, kh, ks sont les 4 coefficients qui composent NRd = kh·ks·α·(Ac·fcd + As·fyd). 
α, kh et ks sont des coefficients correcteurs de la norme EC2, qui ajustent la résistance théorique du poteau pour tenir compte du flambement (α), de l'épaisseur du poteau (kh) et du type d'acier (ks).
Sans eux, impossible d'écrire l'équation en As.
"""


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


def calculer_alpha(lambda_: float, type_section: str) -> float:
    """
    Calcule le coefficient de flambement α.

    Section rectangulaire :
    - si λ ≤ 60  : α = 0,86 / (1 + (λ / 62)²)
    - si 60 < λ ≤ 120 : α = (32 / λ)^1,3

    Section circulaire :
    - si λ ≤ 60  : α = 0,84 / (1 + (λ / 52)²)
    - si λ > 60  : α = (27 / λ)^1,24
    """
    if type_section == TYPE_RECTANGULAIRE:
        if lambda_ <= 60:
            return 0.86 / (1 + (lambda_ / 62) ** 2)
        elif 60 < lambda_ <= 120:
            return (32 / lambda_) ** 1.3
        else:
            raise ValueError("λ hors domaine")

    elif type_section == TYPE_CIRCULAIRE:
        if lambda_ <= 60:
            return 0.84 / (1 + (lambda_ / 52) ** 2)
        else:
            return (27 / lambda_) ** 1.24
    else:
        raise TypeSectionInvalideException()


def calculer_kh(h_ou_d: float, rho: float, delta: float, type_section: str) -> float:
    """
    Calcule le coefficient d'épaisseur kh.

    Section rectangulaire :
    - si h < 0,50 m :
      kh = (0,75 + 0,5 × h) × (1 - 6 × ρ × δ)
    - sinon :
      kh = 1

    Section circulaire :
    - si D < 0,60 m :
      kh = (0,7 + 0,5 × D) × (1 - 8 × ρ × δ)
    - sinon :
      kh = 1

    h_ou_d : plus petite dimension de la section (m) — hauteur/largeur min. en rectangulaire, diamètre en circulaire.
    rho : taux d'armatures, ρ = As / Ac.
    delta : position relative des armatures, δ = d' / h.
    """
    if type_section == TYPE_RECTANGULAIRE:
        if h_ou_d < 0.5:
            return (0.75 + 0.5 * h_ou_d) * (1 - 6 * rho * delta)
        else:
            return 1.0
    elif type_section == TYPE_CIRCULAIRE:
        if h_ou_d < 0.60:
            return (0.7 + 0.5 * h_ou_d) * (1 - 8 * rho * delta)
        else:
            return 1.0
    else:
        raise TypeSectionInvalideException()


def calculer_ks(fyk: float, lambda_: float, type_section: str) -> float:
    """
    Calcule le coefficient ks lié à la nuance d'acier.

    Section rectangulaire :
    - si fyk > 500 MPa et λ > 40 :
    ks = 1,6 - 0,60 × (fyk / 500)
    - sinon :
    ks = 1

    Section circulaire :
    - si fyk > 500 MPa et λ > 30 :
    ks = 1,6 - 0,65 × (fyk / 500)
    - sinon :
    ks = 1

    Paramètres :
    fyk : limite d'élasticité caractéristique de l'acier (MPa).
    lambda_ : élancement du poteau.

    Le coefficient ks vaut généralement 1 avec un acier B500.
    Il ne s'applique que si les deux conditions sont vérifiées :
        - fyk > 500 MPa
        - λ dépasse le seuil de la section (40 en rectangulaire, 30 en circulaire).
    """
    if type_section == TYPE_RECTANGULAIRE:
        if fyk > 500 and lambda_ > 40:
            return 1.6 - 0.60 * (fyk / 500)
        else:
            return 1.0
    elif type_section == TYPE_CIRCULAIRE:
        if fyk > 500 and lambda_ > 30:
            return 1.6 - 0.65 * (fyk / 500)
        else:
            return 1.0
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
