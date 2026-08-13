from django.conf import settings
from rest_framework.response import Response

DUREE_ACCESS = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
DUREE_REFRESH = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())


def definir_cookie(reponse: Response, nom: str, valeur: str, duree: int) -> None:
    reponse.set_cookie(
        key=nom,
        value=valeur,
        max_age=duree,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )


def definir_tokens(
    reponse: Response, access: str, refresh: str | None = None
) -> Response:

    definir_cookie(reponse, settings.JWT_COOKIE_ACCESS, access, DUREE_ACCESS)
    if refresh is not None:
        definir_cookie(reponse, settings.JWT_COOKIE_REFRESH, refresh, DUREE_REFRESH)
    return reponse


def supprimer_tokens(reponse: Response) -> Response:

    for nom in (settings.JWT_COOKIE_ACCESS, settings.JWT_COOKIE_REFRESH):
        reponse.delete_cookie(nom, path="/", samesite=settings.JWT_COOKIE_SAMESITE)  # type: ignore
    return reponse
