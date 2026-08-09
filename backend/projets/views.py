from django.db.models import QuerySet
from rest_framework import viewsets

from .models import Projet
from .serializers import ProjetSerializer


class ProjetViewSet(viewsets.ModelViewSet):
    """CRUD complet sur les projets."""

    serializer_class = ProjetSerializer

    def get_queryset(self) -> QuerySet[Projet]:  # type: ignore[override]
        return Projet.objects.filter(membres=self.request.user)

    def perform_create(self, serializer):
        projet = serializer.save()
        projet.membres.add(self.request.user)
