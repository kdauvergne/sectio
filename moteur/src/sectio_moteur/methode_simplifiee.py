from .exceptions import (
    TypeSectionInvalideException,
    DimensionsManquantesException,
    SectionInsuffisanteException,
)
from .modeles import TYPE_RECTANGULAIRE, TYPE_CIRCULAIRE
from .modeles import PoteauInput, ResultatPoteau
from .interfaces import MethodeCalculPoteauInterface
from math import sqrt, pi, floor

TAUX_TRAVAIL_MIN = 1.1  # le seuil de marge de sécurité visé — on veut NRd/NEd ≥ 1,1, pas juste NRd ≥ NEd.
M2_MPA_VERS_KN = 1000.0  # convertit surface (m²) · résistance (MPa) en kN — utilisée pour le terme béton (Ac*fcd).
CM2_MPA_VERS_KN = 0.1  # convertit As (cm²) et résistance (MPa) en kN — utilisée pour le terme acier (As*fyd), unité différente puisque As est en cm² et non en m².

COEF_G = 1.35  # NEd = 1.35G + 1.5Q
COEF_Q = 1.5  # NEd = 1.35G + 1.5Q
GAMMA_C = 1.5  # fcd = fck/γc où γc = 1.5
GAMMA_S = 1.15  # fyd = fyk / 1,15
D_PRIME_MAX_M = 0.10  # d' max en mètres = 100 * 0.001

# rectangulaire : kh = (0.75 + 0.5 * h_ou_d) * (1 - 6 * rho * delta)
KH_ORDONNEE_RECT = 0.75
KH_PENTE = 0.5
KH_FACTEUR_RHO_DELTA_RECT = 6
# circulaire : (0.7 + 0.5 * h_ou_d) * (1 - 8 * rho * delta)
KH_ORDONNEE_CIRC = 0.7
KH_FACTEUR_RHO_DELTA_CIRC = 8

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
        limite_d_prime = min(0.3 * dim_ref, D_PRIME_MAX_M)

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

        NEd = (COEF_G * entree.G) + COEF_Q * entree.Q
        Ac = calculer_aire_beton(entree)
        fcd = entree.fck / GAMMA_C  # fcd = fck / 1,5
        fyd = entree.fyk / GAMMA_S  # fyd = fyk / 1,15
        lambda_ = calculer_lambda(entree)
        alpha = calculer_alpha(lambda_, entree.type_section)
        ks = calculer_ks(entree.fyk, lambda_, entree.type_section)
        h_ou_d = plus_petite_dimension(entree)
        delta = entree.d_prime / h_ou_d

        if (entree.type_section == TYPE_RECTANGULAIRE and h_ou_d < 0.5) or (
            entree.type_section == TYPE_CIRCULAIRE and h_ou_d < 0.60
        ):
            a, b, c = calculer_coefficients_quadratique(
                NEd, ks, alpha, Ac, fcd, fyd, h_ou_d, delta, entree.type_section
            )
            As = resoudre_as_quadratique(a, b, c)
        else:
            As = resoudre_as_lineaire(NEd, ks, alpha, Ac, fcd, fyd)

        rho = As * 1e-4 / Ac
        kh = calculer_kh(h_ou_d, rho, delta, entree.type_section)
        NRd = kh * ks * alpha * (Ac * fcd * M2_MPA_VERS_KN + As * fyd * CM2_MPA_VERS_KN)
        taux_travail = NRd / NEd

        return ResultatPoteau(
            As=As,
            NRd=NRd,
            taux_travail=taux_travail,
            as_min_gouverne=False,  #! TODO: brancher le bornage As_min/As_max (cf. page Notion "Exceptions métier et bornage") — toujours False pour l'instant
            NEd=NEd,
            lambda_=lambda_,
            alpha=alpha,
            kh=kh,
            ks=ks,
            rho=rho,
            delta=delta,
        )

    def verifier(self, as_propose: float, entree: PoteauInput) -> ResultatPoteau:
        """
        Vérifie si une section d'acier proposée (as_propose) suffit pour le poteau décrit
        par entree, sens inverse de calculer() avec As déjà connu.

        Paramètres :
            as_propose: Section d'acier à vérifier, en cm² (ex. valeur arrondie au nombre
            entier de barres réellement posées, ou valeur théorique issue de calculer()).
            entree: Caractéristiques du poteau (géométrie, matériaux, charges).

        Retourne :
            ResultatPoteau avec As=as_propose (valeur reçue, pas recalculée) et les
            grandeurs dérivées (NRd, taux_travail, kh, rho...) évaluées pour ce As.
        """

        # Valeurs communes avec calculer()
        NEd = (COEF_G * entree.G) + COEF_Q * entree.Q
        Ac = calculer_aire_beton(entree)
        NEd, Ac, fcd, fyd, lambda_, alpha, ks, h_ou_d, delta = grandeurs_communes(
            entree
        )

        rho = as_propose * 1e-4 / Ac
        kh = calculer_kh(h_ou_d, rho, delta, entree.type_section)
        NRd = (
            kh
            * ks
            * alpha
            * ((Ac * fcd * M2_MPA_VERS_KN) + (as_propose * fyd * CM2_MPA_VERS_KN))
        )
        taux_travail = NRd / NEd

        return ResultatPoteau(
            As=as_propose,
            NRd=NRd,
            taux_travail=taux_travail,
            as_min_gouverne=False,
            NEd=NEd,
            lambda_=lambda_,
            alpha=alpha,
            kh=kh,
            ks=ks,
            rho=rho,
            delta=delta,
        )


"""
Fonctions indépendantes de calculs purs, nécessaires au calcul final (calculer_lambda, calculer_alpha, calculer_ks, calculer_kh, plus_petite_dimension)
Rôle dans le moteur : λ, α, kh, ks sont les 4 coefficients qui composent NRd = kh·ks·α·(Ac·fcd + As·fyd). 
α, kh et ks sont des coefficients correcteurs de la norme EC2, qui ajustent la résistance théorique du poteau pour tenir compte du flambement (α), de l'épaisseur du poteau (kh) et du type d'acier (ks).
Sans eux, impossible d'écrire l'équation en As.
"""


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


def grandeurs_communes(entree: PoteauInput) -> tuple:
    NEd = COEF_G * entree.G + COEF_Q * entree.Q
    Ac = calculer_aire_beton(entree)
    fcd = entree.fck / GAMMA_C
    fyd = entree.fyk / GAMMA_S
    lambda_ = calculer_lambda(entree)
    alpha = calculer_alpha(lambda_, entree.type_section)
    ks = calculer_ks(entree.fyk, lambda_, entree.type_section)
    h_ou_d = plus_petite_dimension(entree)
    delta = entree.d_prime / h_ou_d
    return NEd, Ac, fcd, fyd, lambda_, alpha, ks, h_ou_d, delta


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
            return (KH_ORDONNEE_RECT + KH_PENTE * h_ou_d) * (
                1 - KH_FACTEUR_RHO_DELTA_RECT * rho * delta
            )
        else:
            return 1.0
    elif type_section == TYPE_CIRCULAIRE:
        if h_ou_d < 0.60:
            return (KH_ORDONNEE_CIRC + KH_PENTE * h_ou_d) * (
                1 - KH_FACTEUR_RHO_DELTA_CIRC * rho * delta
            )
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


def resoudre_as_lineaire(
    NEd: float, ks: float, alpha: float, Ac: float, fcd: float, fyd: float
) -> float:
    """
    Résout la section d'acier (As) nécessaire, cas linéaire (h≥0,50m, kh=1 fixe).

    Isole As dans NRd = ks·α·(Ac·fcd·M2_MPA_VERS_KN + As·fyd·CM2_MPA_VERS_KN),
    avec NRd visé = TAUX_TRAVAIL_MIN·NEd.
    On isole As car c'est l'inconnue à trouver : on connaît la charge à reprendre
    (NEd) et on cherche combien d'acier il faut pour que la résistance du poteau
    (NRd) atteigne au moins TAUX_TRAVAIL_MIN·NEd.

    Formule isolée : As = (TAUX_TRAVAIL_MIN·NEd/(ks·α) − Ac·fcd·M2_MPA_VERS_KN) / (fyd·CM2_MPA_VERS_KN)

    Paramètres :
        NEd: Effort normal de calcul, en kN
        ks: Coefficient ks (sans dimension)
        alpha: Coefficient α (sans dimension)
        ac: Aire de la section de béton, en m² (Rectangulaire : Ac = b · h | Circulaire: Ac = π · diametre² / 4)
        fcd: Résistance de calcul du béton, en MPa
        fyd: Résistance de calcul de l'acier, en MPa

    Retourne :
        As, en cm², non arrondi.
    """
    return (TAUX_TRAVAIL_MIN * NEd / (ks * alpha) - Ac * fcd * M2_MPA_VERS_KN) / (
        fyd * CM2_MPA_VERS_KN
    )


def calculer_coefficients_quadratique(
    NEd: float,
    ks: float,
    alpha: float,
    Ac: float,
    fcd: float,
    fyd: float,
    h_ou_d: float,
    delta: float,
    type_section: str,
) -> tuple[float, float, float]:
    """Calcule les coefficients a, b, c de l'équation a·As² + b·As + c = 0.

    Ramène la formule NRd = kh·ks·α·(Ac·fcd + As·fyd) à une équation du second
    degré en As, avec NRd visé = TAUX_TRAVAIL_MIN·NEd. Le second degré vient de
    ce que As apparaît deux fois : dans la part acier, et dans kh via ρ = As/Ac.

    En posant kh = K1 − C·As , le développement du produit
    ks·α·(K1 − C·As)·(T + As·fyd) donne les trois coefficients.

    Les valeurs de K1 et du facteur devant ρ·δ dépendent du type de section :
        Rectangulaire : kh = (0,75 + 0,5·h)·(1 − 6·ρ·δ)
        Circulaire    : kh = (0,70 + 0,5·D)·(1 − 8·ρ·δ)
    Elles sont lues dans les constantes KH_* du module, partagées avec
    calculer_kh() : les deux fonctions doivent toujours décrire le même kh.

    Paramètres :
        NEd: Effort normal de calcul, en kN.
        ks: Coefficient ks (sans dimension).
        alpha: Coefficient α (sans dimension).
        Ac: Aire de la section de béton, en m².
        fcd: Résistance de calcul du béton, en MPa.
        fyd: Résistance de calcul de l'acier, en MPa.
        h_ou_d: Plus petite dimension de la section (h ou D selon le type), en m.
        delta: Rapport d'/h (ou d'/D), sans dimension.
        type_section: TYPE_RECTANGULAIRE ou TYPE_CIRCULAIRE.

    Retourne :
        Tuple (a, b, c), les coefficients de l'équation du second degré.
        a est toujours négatif en pratique. c vaut la résistance du béton seul
        moins la charge visée : c ≥ 0 signifie que le béton suffit sans acier.
        Ces coefficients doivent ensuite être passés à resoudre_as_quadratique().

    Lève :
        TypeSectionInvalideException: si type_section n'est ni TYPE_RECTANGULAIRE
        ni TYPE_CIRCULAIRE.
    """
    if type_section == TYPE_RECTANGULAIRE:
        K1 = KH_ORDONNEE_RECT + KH_PENTE * h_ou_d
        facteur_rho_delta = KH_FACTEUR_RHO_DELTA_RECT
    elif type_section == TYPE_CIRCULAIRE:
        K1 = KH_ORDONNEE_CIRC + KH_PENTE * h_ou_d
        facteur_rho_delta = KH_FACTEUR_RHO_DELTA_CIRC
    else:
        raise TypeSectionInvalideException(type_section)

    C = facteur_rho_delta * K1 * delta * 1e-4 / Ac
    T = Ac * fcd * M2_MPA_VERS_KN

    a = -ks * alpha * C * fyd * CM2_MPA_VERS_KN
    b = ks * alpha * (K1 * fyd * CM2_MPA_VERS_KN - C * T)
    c = ks * alpha * K1 * T - TAUX_TRAVAIL_MIN * NEd

    return (a, b, c)


def resoudre_as_quadratique(a: float, b: float, c: float) -> float:
    """Résout l'équation a·As² + b·As + c = 0, cas quadratique (h<0,50m).

    As apparaît au carré car kh dépend lui-même de As (cf. formule de départ
    NRd = kh·ks·α·(Ac·fcd + As·fyd)). a, b, c sont déjà calculés par
    calculer_coefficients_quadratique() et ne dépendent plus de rien d'autre ici.

    a étant négatif, la parabole admet deux racines : la plus petite est la
    solution physique, la seconde est un artefact (branche descendante, plus
    d'acier que de béton). Si c >= 0, le béton seul suffit et la seule racine
    positive est cet artefact — d'où le retour anticipé à 0.0.

    Paramètres :
        a: Coefficient du second degré (toujours négatif en pratique).
        b: Coefficient du premier degré.
        c: Coefficient constant.

    Retourne :
        As, en cm², non arrondi — la plus petite racine positive de l'équation.

    Erreurs :
        ValueError: Si le discriminant (b² − 4ac) est négatif, ce qui signifie
            qu'aucune section d'acier ne permet d'atteindre le taux de travail
            visé (section insuffisante).
    """
    if c >= 0:
        return 0.0
    discriminant = b**2 - (4 * a * c)
    if discriminant < 0:
        raise SectionInsuffisanteException("Section insuffisante.")

    racine_1 = (-b + sqrt(discriminant)) / (2 * a)
    racine_2 = (-b - sqrt(discriminant)) / (2 * a)

    racines_positives = [r for r in (racine_1, racine_2) if r > 0]
    if not racines_positives:
        raise SectionInsuffisanteException("Aucune racine positive trouvée.")

    return min(racines_positives)


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
