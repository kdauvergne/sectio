from rest_framework import generics, permissions

from .serializers import InscriptionSerializer


class InscriptionView(generics.CreateAPIView):
    """Création de compte. Seul endpoint ouvert sans authentification."""

    serializer_class = InscriptionSerializer
    permission_classes = [permissions.AllowAny]  # noqa: RUF012
