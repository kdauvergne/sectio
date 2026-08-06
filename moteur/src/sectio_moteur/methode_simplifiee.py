from .exceptions import (
    TypeSectionInvalideException,
    DimensionsManquantesException,
    SectionInsuffisanteException,
    MethodeNonApplicableException,
    FerraillageImpossibleException,
)
from .modeles import TYPE_RECTANGULAIRE, TYPE_CIRCULAIRE
from .modeles import PoteauInput, ResultatPoteau
from .interfaces import MethodeCalculPoteauInterface
from .geometrie import plus_petite_dimension, calculer_aire_beton
from .choix_armatures import (
    choix_armatures,
    choisir_combinaison_par_defaut,
    calculer_armatures_transversales,
)
from math import sqrt, floor
from dataclasses import replace

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


# Constantes de conversion d'unité pour As,min As,max
RATIO_AS_MIN_EFFORT = 0.10
RATIO_AS_MIN_GEOMETRIQUE = 0.002
RATIO_AS_MAX = 0.04
KN_PAR_MPA_VERS_CM2 = 10.0  # (kN / MPa) -> cm2
M2_VERS_CM2 = 1e4  # m2 -> cm2


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
        """Résout la section d'acier As nécessaire pour un poteau donné.

        Enchaînement :
            1. rejet si le poteau sort du domaine de la méthode simplifiée
            2. résolution de As (branche linéaire ou quadratique selon la
                plus petite dimension de la section)
            3. bornage réglementaire As,min / As,max
            4. assemblage du résultat de dimensionnement
            5. matérialisation en barres et cadres (ajouter_ferraillage)

        Contrairement à verifier(), calculer() applique elle-même le bornage :
        As trop faible est remonté à As,min (as_min_gouverne=True), As trop
        élevé provoque un rejet.

        Paramètres :
            entree: caractéristiques du poteau (géométrie, matériaux, charges).

        Retourne :
            ResultatPoteau complet : As retenu, NRd, taux de travail,
            grandeurs intermédiaires et armatures (barres + cadres).
            Si aucune disposition de barres n'est constructible, le
            dimensionnement est tout de même retourné, armatures à None et
            ferraillage_impossible=True.

        Erreurs :
            MethodeNonApplicableException: poteau hors domaine d'application.
            SectionInsuffisanteException: As requis dépasse As,max.
        """

        # rejet explicite si le poteau sort du domaine de la méthode simplifiée
        violations = self.est_applicable(entree)
        if violations:
            raise MethodeNonApplicableException(violations)

        grandeurs = grandeurs_communes(
            entree
        )  # on garde le tuple complet, car assembler_resultat l'attend en paramètre
        NEd, Ac, fcd, fyd, lambda_, alpha, ks, h_ou_d, delta = (
            grandeurs  # décompacte aussi en 9 variables, utilisées plus bas pour résoudre As
        )

        if (entree.type_section == TYPE_RECTANGULAIRE and h_ou_d < 0.5) or (
            entree.type_section == TYPE_CIRCULAIRE and h_ou_d < 0.60
        ):
            a, b, c = calculer_coefficients_quadratique(
                NEd,
                ks,
                alpha,
                Ac,
                fcd,
                fyd,
                h_ou_d,
                delta,
                entree.type_section,
                entree.taux_travail_min,
            )
            As = resoudre_as_quadratique(a, b, c)
        else:
            As = resoudre_as_lineaire(
                NEd, ks, alpha, Ac, fcd, fyd, entree.taux_travail_min
            )
        # bornes réglementaires, calculées à partir de l'effort et de la section
        as_min = calculer_as_min(NEd, fyd, Ac)
        as_max = calculer_as_max(Ac)
        # corrige As si hors bornes ; lève SectionInsuffisanteException si trop grand
        As, as_min_gouverne = borner_as(As, as_min, as_max)

        resultat = assembler_resultat(As, as_min_gouverne, as_max, entree, grandeurs)

        return ajouter_ferraillage(resultat, entree, as_max)

    def verifier(self, as_propose: float, entree: PoteauInput) -> ResultatPoteau:
        """
        Vérifie si une section d'acier proposée (as_propose) suffit pour le poteau.

        Sens inverse de calculer() : As est déjà connu, on évalue les grandeurs
        qui en découlent (NRd, taux_travail...). Contrairement à calculer(),
        ne corrige jamais As : un dépassement de borne est signalé, jamais
        substitué silencieusement.

        Enchaînement :
            1. rejet si le poteau sort du domaine de la méthode simplifiée
            2. calcul des bornes réglementaires As,min / As,max
            3. rejet si as_propose dépasse As,max (aucune substitution)
            4. assemblage du résultat sur as_propose tel quel
            5. matérialisation en barres et cadres (ajouter_ferraillage)

        Paramètres :
            as_propose: section d'acier à vérifier, en cm² (ex. valeur arrondie
            au nombre entier de barres réellement posées, ou valeur théorique
            issue de calculer()).
            entree: caractéristiques du poteau (géométrie, matériaux, charges).

        Retourne :
            ResultatPoteau avec As=as_propose (valeur reçue, pas recalculée)
            et les grandeurs dérivées évaluées pour ce As.

            as_min_gouverne a ici un sens différent de calculer() : il indique
            que as_propose est au niveau ou en dessous du minimum réglementaire
            (une alerte), pas qu'une substitution a eu lieu.

            Comme dans calculer(), une matérialisation impossible n'annule pas
            la vérification : ferraillage_impossible=True, armatures à None.

        Erreurs :
            MethodeNonApplicableException: poteau hors domaine d'application.
            SectionInsuffisanteException: as_propose dépasse As,max.
        """

        # rejet explicite si le poteau sort du domaine de la méthode simplifiée
        violations = self.est_applicable(entree)
        if violations:
            raise MethodeNonApplicableException(violations)

        # grandeurs communes avec calculer()
        grandeurs = grandeurs_communes(entree)
        NEd, Ac, fcd, fyd, lambda_, alpha, ks, h_ou_d, delta = grandeurs

        # mêmes bornes que calculer(), mais AUCUNE substitution ici
        as_min = calculer_as_min(NEd, fyd, Ac)
        as_max = calculer_as_max(Ac)
        if as_propose > as_max:
            raise SectionInsuffisanteException(
                "As proposé dépasse As,max", as_calcule=as_propose, as_max=as_max
            )
        # drapeau d'alerte : le ferraillage proposé est au niveau ou sous le minimum
        as_min_gouverne = as_propose <= as_min

        resultat = assembler_resultat(
            as_propose, as_min_gouverne, as_max, entree, grandeurs
        )

        return ajouter_ferraillage(resultat, entree, as_max)


"""
Fonctions indépendantes de calculs purs, nécessaires au calcul final (calculer_lambda, calculer_alpha, calculer_ks, calculer_kh, plus_petite_dimension)
Rôle dans le moteur : λ, α, kh, ks sont les 4 coefficients qui composent NRd = kh·ks·α·(Ac·fcd + As·fyd). 
α, kh et ks sont des coefficients correcteurs de la norme EC2, qui ajustent la résistance théorique du poteau pour tenir compte du flambement (α), de l'épaisseur du poteau (kh) et du type d'acier (ks).
Sans eux, impossible d'écrire l'équation en As.
"""


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
    NEd: float,
    ks: float,
    alpha: float,
    Ac: float,
    fcd: float,
    fyd: float,
    taux_travail_min: float,
) -> float:
    """
    Résout la section d'acier (As) nécessaire, cas linéaire (h≥0,50m, kh=1 fixe).

    Isole As dans NRd = ks·α·(Ac·fcd·M2_MPA_VERS_KN + As·fyd·CM2_MPA_VERS_KN),
    avec NRd visé = taux_travail_min·NEd.
    On isole As car c'est l'inconnue à trouver : on connaît la charge à reprendre
    (NEd) et on cherche combien d'acier il faut pour que la résistance du poteau
    (NRd) atteigne au moins taux_travail_min·NEd.

    Formule isolée : As = (taux_travail_min·NEd/(ks·α) − Ac·fcd·M2_MPA_VERS_KN) / (fyd·CM2_MPA_VERS_KN)

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
    return (taux_travail_min * NEd / (ks * alpha) - Ac * fcd * M2_MPA_VERS_KN) / (
        fyd * CM2_MPA_VERS_KN
    )


def calculer_as_min(NEd: float, fyd: float, Ac: float) -> float:
    """As,min = max(0,10·NEd/fyd ; 0,002·Ac), en cm².

    NEd en kN, fyd en MPa, Ac en m². Retour en cm².
    Le max retient le critère le plus contraignant des deux (effort et
    section minimale géométrique).
    """
    terme_effort = RATIO_AS_MIN_EFFORT * (NEd / fyd) * KN_PAR_MPA_VERS_CM2
    terme_geometrique = RATIO_AS_MIN_GEOMETRIQUE * Ac * M2_VERS_CM2
    return max(terme_effort, terme_geometrique)


def calculer_as_max(Ac: float) -> float:
    """As,max = 0,04·Ac, en cm².

    Ac en m². Au-delà, le béton ne peut plus circuler correctement
    entre les barres.
    """
    return RATIO_AS_MAX * Ac * M2_VERS_CM2


def borner_as(as_brut: float, as_min: float, as_max: float) -> tuple[float, bool]:
    """Borne un As brut aux limites réglementaires As,min / As,max.

        as_brut: As calculé par resoudre_as_lineaire/quadratique, en cm².
        as_min: borne inférieure réglementaire, en cm² (calculer_as_min).
        as_max: borne supérieure réglementaire, en cm² (calculer_as_max).

    Retourne :
        Un couple (as_final, as_min_gouverne). as_min_gouverne vaut True
        quand as_brut était en dessous du minimum et a été remplacé par
        as_min ; False quand as_brut était déjà conforme.

    Erreurs :
        SectionInsuffisanteException: si as_brut dépasse as_max, la section
        béton ne peut pas reprendre l'effort demandé.
    """
    if as_brut > as_max:
        raise SectionInsuffisanteException(
            "As dépasse As,max", as_calcule=as_brut, as_max=as_max
        )
    elif as_brut < as_min:
        return as_min, True
    else:
        return as_brut, False


def assembler_resultat(
    As: float,
    as_min_gouverne: bool,
    as_max: float,
    entree: PoteauInput,
    grandeurs: tuple,
) -> ResultatPoteau:
    """Construit le ResultatPoteau à partir d'un As définitif.

    Seul endroit du moteur où rho, kh, NRd, taux_travail et les armatures
    sont calculés. Appelée par calculer() ET par verifier().
    """
    NEd, Ac, fcd, fyd, lambda_, alpha, ks, h_ou_d, delta = grandeurs
    rho = As * 1e-4 / Ac
    kh = calculer_kh(h_ou_d, rho, delta, entree.type_section)
    NRd = kh * ks * alpha * (Ac * fcd * M2_MPA_VERS_KN + As * fyd * CM2_MPA_VERS_KN)
    taux_travail = NRd / NEd

    return ResultatPoteau(
        As=As,
        NRd=NRd,
        taux_travail=taux_travail,
        as_min_gouverne=as_min_gouverne,
        NEd=NEd,
        lambda_=lambda_,
        alpha=alpha,
        kh=kh,
        ks=ks,
        rho=rho,
        delta=delta,
    )


def ajouter_ferraillage(
    resultat: ResultatPoteau, entree: PoteauInput, as_max: float
) -> ResultatPoteau:
    """Matérialise un dimensionnement en armatures réelles (barres + cadres).

    Deuxième temps du calcul : assembler_resultat() répond « combien de cm²
    d'acier », ajouter_ferraillage() répond « comment les disposer ».

    Un As pourtant conforme (≤ As,max) peut n'admettre aucune disposition
    constructible — arrondi au nombre entier de barres dépassant As,max, ou
    barres ne rentrant pas dans le périmètre utile. Ce cas ne détruit pas le
    dimensionnement : il est signalé, jamais corrigé.

    Paramètres :
        resultat: ResultatPoteau issu d'assembler_resultat(), armatures à None.
        entree: géométrie et type_section du poteau.
        as_max: borne réglementaire, en cm² (calculer_as_max).

    Retourne :
        Une copie du résultat (frozen → dataclasses.replace), armatures
        renseignées ; ou le résultat inchangé avec ferraillage_impossible=True.

    Erreurs :
        Aucune : FerraillageImpossibleException est capturée ici et convertie
        en drapeau — seul endroit du moteur où elle est absorbée.
    """
    try:
        combinaisons = choix_armatures(resultat.As, as_max, entree)
    except FerraillageImpossibleException:
        return replace(resultat, ferraillage_impossible=True)

    n, diametre_l = choisir_combinaison_par_defaut(combinaisons)
    diametre_cadre, e_central, e_extremites = calculer_armatures_transversales(
        diametre_l, entree
    )
    return replace(
        resultat,
        combinaisons_possibles=combinaisons,
        nombre_barres_longitudinales=n,
        diametre_longitudinal=diametre_l,
        diametre_cadres=diametre_cadre,
        espacement_central=e_central,
        espacement_extremites=e_extremites,
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
    taux_travail_min: float,
) -> tuple[float, float, float]:
    """Calcule les coefficients a, b, c de l'équation a·As² + b·As + c = 0.

    Ramène la formule NRd = kh·ks·α·(Ac·fcd + As·fyd) à une équation du second
    degré en As, avec NRd visé = taux_travail_min ·NEd. Le second degré vient de
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
        taux_travail_min: seuil de marge de sécurité minimum visé

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
    c = ks * alpha * K1 * T - taux_travail_min * NEd

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
        c: Coefficient constant, égal à la résistance du béton seul moins la charge visée

    Retourne :
        As, en cm², non arrondi — la plus petite racine positive, ou 0.0 si
        aucun acier n'est requis par la résistance (As,min prendra le relais).

    Erreurs :
        SectionInsuffisanteException: Si le discriminant (b² − 4ac) est négatif,
            aucune section d'acier ne permet d'atteindre le taux de travail visé.
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
