from django.db import transaction
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.request import Request

from .models import Batiment, Niveau, Poteau, Projet
from .serializers import (
    BatimentDetailSerializer,
    BatimentSerializer,
    NiveauDetailSerializer,
    NiveauSerializer,
    PoteauSerializer,
    ProjetDetailSerializer,
    ProjetSerializer,
)


class ProjetViewSet(viewsets.ModelViewSet):
    """CRUD complet sur les projets."""

    def get_queryset(self) -> QuerySet[Projet]:  # type: ignore[override]
        return Projet.objects.filter(membres=self.request.user).prefetch_related(
            "batiments"
        )

    def perform_create(self, serializer):
        projet = serializer.save()
        projet.membres.add(self.request.user)

    def get_serializer_class(self):  # type: ignore[override]
        if self.action == "retrieve":
            return ProjetDetailSerializer
        return ProjetSerializer


class BatimentViewSet(viewsets.ModelViewSet):
    """Bâtiments des projets dont l'utilisateur est membre."""

    def get_serializer_class(self):  # type: ignore[override]
        if self.action == "retrieve":
            return BatimentDetailSerializer
        return BatimentSerializer

    def get_queryset(self) -> QuerySet[Batiment]:  # type: ignore[override]
        queryset = Batiment.objects.filter(projet__membres=self.request.user)

        projet = self.request.query_params.get("projet")  # type: ignore[override]
        if projet:
            queryset = queryset.filter(projet_id=projet)

        return queryset.select_related("projet").prefetch_related("niveaux")


class NiveauViewSet(viewsets.ModelViewSet):
    """Niveaux des projets dont l'utilisateur est membre."""

    request: Request

    def get_serializer_class(self):  # type: ignore[override]
        if self.action == "retrieve":
            return NiveauDetailSerializer
        return NiveauSerializer

    def get_queryset(self) -> QuerySet[Niveau]:  # type: ignore[override]
        queryset = Niveau.objects.filter(batiment__projet__membres=self.request.user)

        batiment = self.request.query_params.get("batiment")
        if batiment:
            queryset = queryset.filter(batiment_id=batiment)

        return queryset.select_related("batiment__projet").prefetch_related("poteaux")


class PoteauViewSet(viewsets.ModelViewSet):
    """Poteaux des projets dont l'utilisateur est membre."""

    serializer_class = PoteauSerializer

    def get_queryset(self) -> QuerySet[Poteau]:  # type: ignore[override]
        queryset = Poteau.objects.filter(
            niveau__batiment__projet__membres=self.request.user
        )

        niveau = self.request.query_params.get("niveau")  # type: ignore[override]
        if niveau:
            queryset = queryset.filter(niveau_id=niveau)

        return queryset.select_related("niveau__batiment__projet")

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()
