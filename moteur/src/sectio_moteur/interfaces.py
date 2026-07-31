from abc import ABC, abstractmethod
from .modeles import PoteauInput, ResultatPoteau


class MethodeCalculPoteauInterface(ABC):
    """
    Pose le contrat que toute méthode de calcul doit respecter (pattern Stratégie). Le "contrat" défini  que toute méthode de calcul, présente ou future respecte les 3 méthodes suivantes:
        - es-tu applicable à ce poteau ?
        - quel est le résultat si je te laisse résoudre As à partir de NEd ?
        - et est-ce qu'un As que je te propose moi-même est conforme ?
    Important pour plus tard lors de futures versions de Sectio et implémentation de nouvelles méthodes de calcul (méthode générale, méthode de second ordre, méthode Feissel...). En lien avec le pattern Stratégie de développement.
    """

    @abstractmethod
    def est_applicable(self, entree: PoteauInput) -> list[str]:
        pass

    @abstractmethod
    def calculer(self, entree: PoteauInput) -> ResultatPoteau:
        pass

    @abstractmethod
    def verifier(self, as_propose: float, entree: PoteauInput) -> ResultatPoteau:
        pass
