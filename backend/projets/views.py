from rest_framework import viewsets

from .models import Projet
from .serializers import ProjetSerializer


class ProjetViewSet(viewsets.ModelViewSet):
    """CRUD complet sur les projets."""

    queryset = Projet.objects.all()
    serializer_class = ProjetSerializer
