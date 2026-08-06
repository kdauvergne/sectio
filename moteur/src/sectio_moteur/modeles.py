from dataclasses import dataclass

TYPE_RECTANGULAIRE = "rectangulaire"
TYPE_CIRCULAIRE = "circulaire"

#: Classe structurale utilisée par défaut pour déterminer cmin,dur.
CLASSE_STRUCTURALE_DEFAUT = "S4"
#: Tolérance d'exécution Δcdev ajoutée à cmin,dur pour obtenir Cnom (cnom = cmin,dur + Δcdev) (en mm).
DELTA_CDEV_MM = 5.0

TAUX_TRAVAIL_MIN_DEFAUT = 1.0  # Seuil de marge de sécurité visé. On vise NRd = NEd par défaut. L'utilisateur pourra changer ce coefficient.


@dataclass(frozen=True)  # immuable
class PoteauInput:
    """
    Données en entrée saisies par un ingénieur afin d'obtenir le flambement d'un poteau rotulé-rotulé.
    La section béton (b, h ou D) est saisie par l'ingénieur dans cette Méthode Simplifiée.

    La charge de calcul NEd = 1,35·G + 1,5·Q (kN) est calculée en interne afin d'être réutilisée dans le module de résistance au feu à part.

    Pas de validation d'unité ici, la dataclass ici est un conteneur de données pur.
    La détection d'une valeur hors plage (ex. d_prime saisi en mm par erreur) est couverte par MethodeSimplifiee.est_applicable()

    """

    # charges (kN) / NEd = 1.35G + 1.5Q
    G: float
    Q: float

    # résistances béton et acier (MPa)
    fck: float
    fyk: float

    # longueur de flambement (m)
    L0: float

    # distance entre le parement béton et l'axe des armatures longitudinales (m)
    d_prime: float

    # type de section (TYPE_RECTANGULAIRE ou TYPE_CIRCULAIRE)
    type_section: str
    b: float | None = None
    h: float | None = None
    diametre: float | None = None

    # seuil de marge de sécurité visé. Par défaut 1.0.
    taux_travail_min: float = TAUX_TRAVAIL_MIN_DEFAUT

    # module feu (R30/R60/R120, etc)
    duree_resistance_feu: str | None = None
    expose_un_seul_cote: bool = False


@dataclass(frozen=True)
class ResultatPoteau:
    """
    Résultat du dimensionnement au flambement de la section béton saisie par l'ingénieur.
    Un poteau hors domaine d'application ou une section insuffisante ne produisent jamais de ResultatPoteau : ils sont rejetés par exception métier (MethodeNonApplicableException, SectionInsuffisanteException).

    Le détail des grandeurs intermédiaires (λ, α, kh, ks, ρ, δ) est conservé pour la traçabilité de la note de calcul PDF.
    """

    # résultat principal
    As: float  # Aire de la section d'armatures - cm2
    NRd: float  # Force portante - kN
    as_min_gouverne: bool  # Aire de la section minimale d'armatures

    # valeurs intermédiaires
    NEd: float  # Effort normal agissant
    lambda_: float  # Elancement (flambement)
    alpha: float
    kh: float
    ks: float
    rho: float  # taux d'amatures
    delta: float  # d_prime / h (ou D) — position relative des armatures

    taux_travail: float  # NRd / NEd — valeur obtenue

    # armatures transversales - unité : mm
    diametre_cadres: float | None = None
    espacement_central: float | None = None
    espacement_extremites: float | None = None
    combinaisons_possibles: list[tuple[int, int]] | None = None

    # armatures longitudinales - sortie du choix du module choix_armatures indépendant
    nombre_barres_longitudinales: int | None = None
    diametre_longitudinal: float | None = None
    ferraillage_impossible: bool = False


@dataclass(frozen=True)
class TypeFerraillage:
    """Un type de ferraillage proposé pour un groupe de poteaux physiques.

    resultat : le ResultatPoteau retenu pour ce type (calculer() ou verifier()).
    poteaux_couverts : les poteaux physiques auxquels ce ferraillage s'applique.
    """

    resultat: ResultatPoteau
    poteaux_couverts: list[PoteauInput]
