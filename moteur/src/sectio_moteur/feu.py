import json
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from abc import ABC
from .modeles import TYPE_RECTANGULAIRE, TYPE_CIRCULAIRE

# CHEMIN_DONNEES_REELLES = Path(__file__).parent / "data" / "tables_feu.json"


class DureeResistanceFeu(Enum):
    R30 = 30
    R60 = 60
    R90 = 90
    R120 = 120
    R180 = 180
    R240 = 240


@dataclass(frozen=True)
class EntreeFeu:
    Gk: float  # charge permanente caractéristique (kN)
    Qk1: float  # charge d'exploitation caractéristique principale (kN)
    duree_resistance_feu: str  # code durée visée : "R30", "R60", "R90"...
    l0: float  # longueur efficace à température normale (m)
    l0_fi: float  # longueur efficace au feu (m)
    e1: float  # excentricité au feu (m)
    b: float  # largeur (m)
    h: float  # plus petite dimension normative (m) — cf. plus_petite_dimension()
    a: float  # distance axe armatures longi. / parement exposé (mm)
    as_: float  # section d'acier (cm²)
    ac: float  # aire de la section (unité à trancher, cf. point bloquant)
    expose_un_seul_cote: bool
    type_section: str


@dataclass(frozen=True)
class ResultatFeu:
    conforme: bool  # verdict final de conformité
    duree_resistance_feu: str
    limites_methode: (
        bool  # distingue hors périmètre de la méthode A d'un échec véritable
    )
    couple_valide: (
        tuple[float, float] | None
    )  # couple (bmin, a) retenu si conforme, sinon None


class DureeResistanceFeuInvalideException(Exception):
    """Levée quand une valeur reçue ne correspond à aucun membre de DureeResistanceFeu.
    valeur_recue: la valeur str invalide à l'origine de l'exception.
    """

    def __init__(self, valeur_recue):
        self.valeur_recue = valeur_recue
        super().__init__(
            f"Cette durée de résistance n'est pas prise en compte : {valeur_recue}"
        )


def convertir_duree(valeur: str) -> DureeResistanceFeu:
    """Convertit une durée de résistance feu (str) en membre de DureeResistanceFeu.

    Arguments:
        valeur: la durée reçue depuis PoteauInput (ex. "R90").

    Retourne:
        Le membre DureeResistanceFeu correspondant.

    Lève:
        DureeResistanceFeuInvalideException: si valeur ne correspond à aucun membre.
    """
    try:
        return DureeResistanceFeu(valeur)
    except ValueError:
        raise DureeResistanceFeuInvalideException(valeur)


# def _charger_table_feu(chemin: Path) -> dict:
#     with chemin.open(mode="r", encoding="utf-8") as fichier:
#         return json.load(fichier)
