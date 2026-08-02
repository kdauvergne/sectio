"""
Module permettant de calculer l'enrobage nominal "Cnom" à partir :
- de la classe d'exposition du béton ;
- de la classe structurale ;
- d'une tolérance d'exécution.

⚠️ STATUT V1 : non branché. Hypothèse cnom = d' (donnée d'entrée existante)
pour alléger la saisie utilisateur, section "cnom".
Ce module reste fonctionnel et testé, réactivation possible en V2
si l'approximation cnom=d' s'avère trop pénalisante sur des cas réels
(faux rejets FerraillageImpossibleException).
"""

import json
from pathlib import Path

from .exceptions import ClasseExpositionInvalideException
from .modeles import CLASSE_STRUCTURALE_DEFAUT, DELTA_CDEV_MM

"""Module permettant de calculer l'enrobage nominal "Cnom" à partir :
- de la classe d'exposition du béton ;
- de la classe structurale ;
- d'une tolérance d'exécution."""

CHEMIN_DONNEES_REELLES = Path(__file__).parent / "data" / "tables_enrobage.json"


def calculer_cnom(
    classe_exposition: str,
    classe_structurale: str = CLASSE_STRUCTURALE_DEFAUT,
    chemin_table: Path = CHEMIN_DONNEES_REELLES,
) -> float:
    """
    Calcule l'enrobage nominal cnom.
    cnom = cmin,dur + Δcdev

    Paramètres:
        classe_exposition:
            Classe d'exposition du béton selon l'Eurocode 2.

        classe_structurale:
            Classe structurale utilisée pour déterminer cmin,dur.

        chemin_table:
            Chemin vers le fichier JSON de la table d'enrobage.
            Par défaut, pointe vers les vraies valeurs (tables_enrobage.json).
            Les tests injectent le chemin du fichier example pour ne
            jamais dépendre des valeurs protégées AFNOR.

    Retourne:
        Enrobage nominal (cnom) en cm.
    """
    table = _charger_table_enrobage(chemin_table)

    try:
        classe = table[classe_exposition]
    except KeyError:
        raise ClasseExpositionInvalideException(
            f"Classe d'exposition inconnue : {classe_exposition}"
        )

    try:
        structure = classe[classe_structurale]
    except KeyError:
        raise ClasseExpositionInvalideException(
            f"Classe structurale inconnue : {classe_structurale} "
            f"(pour la classe d'exposition {classe_exposition})"
        )

    cmin_dur_mm = structure["cmin_dur_mm"]
    cnom_mm = cmin_dur_mm + DELTA_CDEV_MM

    return cnom_mm / 10  # converti cnom en cm


def _charger_table_enrobage(chemin: Path) -> dict:
    with chemin.open(mode="r", encoding="utf-8") as fichier:
        return json.load(fichier)
