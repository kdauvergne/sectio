class SectioException(Exception):
    """Base commune à toutes les exceptions métier du moteur.

    Permet aux appelants (classement, API) d'attraper « une erreur de
    dimensionnement » sans attraper aussi les bugs Python (TypeError,
    AttributeError…), qui doivent, eux, remonter.
    """


class TypeSectionInvalideException(SectioException):
    pass


class DimensionsManquantesException(SectioException):
    pass


class ClasseExpositionInvalideException(SectioException):
    pass


class SectionInsuffisanteException(SectioException):
    """Levée quand la section béton ne peut pas reprendre l'effort demandé.

    as_calcule et as_max sont optionnels : certains appels (ex. discriminant
    négatif dans resoudre_as_quadratique) ne disposent pas encore d'un As
    calculé au moment où l'exception est levée.
    """

    def __init__(
        self,
        message: str,
        as_calcule: float | None = None,
        as_max: float | None = None,
    ):
        self.as_calcule = as_calcule
        self.as_max = as_max
        self.message = message
        super().__init__(message)


class MethodeNonApplicableException(SectioException):
    """Levée quand un poteau ne respecte pas le domaine d'application de la méthode simplifiée.

    conditions_violees : liste des règles non respectées (ex. "fck hors bornes"),
    stockée en attribut pour être exploitée individuellement,
    en plus du message texte généré automatiquement.
    """

    def __init__(self, conditions_violees: list[str]):
        self.conditions_violees = conditions_violees
        message = f"Méthode non applicable : {conditions_violees}"
        super().__init__(message)


class FerraillageImpossibleException(SectioException):
    """Levée quand aucune combinaison (n, Øl) de barres réelles ne convient.

    As théorique valide, mais le balayage des diamètres normalisés (choix_armatures)
    n'a trouvé aucune disposition qui respecte à la fois As,max et le filtre
    géométrique (nombre de barres qui rentrent physiquement dans la section).
    """

    def __init__(self, as_theorique: float, as_max: float):
        self.as_theorique = as_theorique
        self.as_max = as_max
        message = f"Aucune combinaison (n, Øl) ne convient pour As={as_theorique} cm² (As,max={as_max} cm²)."
        super().__init__(message)
