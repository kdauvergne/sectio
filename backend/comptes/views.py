from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .cookies import definir_tokens, supprimer_tokens
from .serializers import InscriptionSerializer


class InscriptionView(generics.CreateAPIView):
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.AllowAny]  # noqa: RUF012


class ConnexionView(TokenObtainPairView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        reponse = super().post(request, *args, **kwargs)
        donnees = reponse.data
        if donnees is None:
            return reponse

        access = donnees.pop("access")
        refresh = donnees.pop("refresh")
        return definir_tokens(reponse, access, refresh)


class RafraichirView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(settings.JWT_COOKIE_REFRESH)
        if not refresh:
            return Response(
                {"detail": "Aucun refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serialiseur = self.get_serializer(data={"refresh": refresh})
        try:
            serialiseur.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        donnees = serialiseur.validated_data
        reponse = Response(status=status.HTTP_204_NO_CONTENT)
        return definir_tokens(reponse, donnees["access"], donnees.get("refresh"))


class DeconnexionView(APIView):
    permission_classes = [permissions.AllowAny]  # noqa: RUF012

    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_COOKIE_REFRESH)
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass
        return supprimer_tokens(Response(status=status.HTTP_204_NO_CONTENT))
