from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .cookies import definir_tokens, supprimer_tokens
from .serializers import (
    DemandeResetPasswordSerializer,
    InscriptionSerializer,
    MonCompteSerializer,
    ResetPasswordSerializer,
)


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


class MonCompteView(generics.RetrieveAPIView):
    """GET /api/me renvoie l'utilisateur correspondant au cookie identifié"""

    serializer_class = MonCompteSerializer

    def get_object(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return self.request.user


class DemandeResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]  # noqa: RUF012

    @extend_schema(request=DemandeResetPasswordSerializer, responses={200: None})
    def post(self, request):
        serialiseur = DemandeResetPasswordSerializer(data=request.data)
        serialiseur.is_valid(raise_exception=True)
        email = serialiseur.validated_data["email"]  # type: ignore[index]

        utilisateur = get_user_model().objects.filter(email__iexact=email).first()
        if utilisateur:
            uid = urlsafe_base64_encode(force_bytes(utilisateur.pk))
            token = default_token_generator.make_token(utilisateur)
            lien = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

            send_mail(
                subject="Réinitialisation de votre mot de passe Sectio",
                message=f"Cliquez sur ce lien pour réinitialiser votre mot de passe : {lien}",
                from_email=None,
                recipient_list=[email],
            )

        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]  # noqa: RUF012

    @extend_schema(request=ResetPasswordSerializer, responses={200: None})
    def post(self, request):
        serialiseur = ResetPasswordSerializer(data=request.data)
        serialiseur.is_valid(raise_exception=True)
        serialiseur.save()

        return Response(status=status.HTTP_200_OK)
