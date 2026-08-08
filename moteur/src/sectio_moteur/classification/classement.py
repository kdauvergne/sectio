from ..exceptions import SectioException
from ..interfaces import MethodeCalculPoteauInterface
from ..modeles import PoteauInput, ResultatPoteau, TypeFerraillage


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
        except SectioException as e:
            echecs.append((poteau, e))
    return succes, echecs


def proposer_types(
    poteaux: list[PoteauInput], methode: MethodeCalculPoteauInterface
) -> tuple[list, list[tuple[PoteauInput, Exception]]]:
    """Propose 2 à 3 types de ferraillage pour un groupe de poteaux.

    Type 1 : poteau au As maximal (calculer()).
    Type 2 : poteaux à as_min_gouverne=True (ferraillage minimal partagé).
    Type 3 : poteaux restants, testés via verifier().

    Retourne (types, echecs) : types est une liste de TypeFerraillage,
    echecs la liste des poteaux qui ont échoué au calcul.
    """
    succes, echecs = calculer_tous_les_poteaux(poteaux, methode)
    poteau_1, resultat_1 = max(succes, key=lambda couple: couple[1].As)

    type_1 = TypeFerraillage(resultat=resultat_1, poteaux_couverts=[poteau_1])

    type_2_couples = [
        (p, r) for p, r in succes if r.as_min_gouverne and p is not poteau_1
    ]

    if type_2_couples:
        poteaux_type_2 = [p for p, r in type_2_couples]
        resultat_2 = type_2_couples[0][1]
        type_2 = TypeFerraillage(resultat=resultat_2, poteaux_couverts=poteaux_type_2)
    else:
        type_2 = None

    poteaux_type_1_et_2 = {poteau_1} | {p for p, r in type_2_couples}
    restants = [(p, r) for p, r in succes if p not in poteaux_type_1_et_2]

    if restants:
        as_candidat = resultat_1.As
        poteaux_type_3 = [p for p, r in restants]
        poteau_3, _ = max(restants, key=lambda couple: couple[1].As)
        resultat_3 = methode.verifier(as_candidat, poteau_3)
        type_3 = TypeFerraillage(resultat=resultat_3, poteaux_couverts=poteaux_type_3)
    else:
        type_3 = None

    types = [t for t in [type_1, type_2, type_3] if t is not None]
    return types, echecs
