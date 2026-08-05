from ..interfaces import MethodeCalculPoteauInterface
from ..modeles import PoteauInput, ResultatPoteau


def calculer_tous_les_poteaux(
    poteaux: list[PoteauInput], methode: MethodeCalculPoteauInterface
) -> tuple[
    list[tuple[PoteauInput, ResultatPoteau]], list[tuple[PoteauInput, Exception]]
]:
    """Calcule chaque poteau du groupe individuellement.

    Retourne (succes, echecs) : succes est une liste de couples
    (poteau, resultat) ; echecs une liste de couples (poteau, exception).
    Un poteau en échec n'empêche pas le calcul des autres.
    """
    succes = []
    echecs = []
    for poteau in poteaux:
        try:
            resultat = methode.calculer(poteau)
            succes.append((poteau, resultat))
        except Exception as e:
            echecs.append((poteau, e))
    return succes, echecs
