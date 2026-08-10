from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BatimentViewSet,
    NiveauViewSet,
    PoteauViewSet,
    ProjetViewSet,
    TypePoteauViewSet,
)

router = DefaultRouter()
router.register(r"projets", ProjetViewSet, basename="projet")
router.register(r"batiments", BatimentViewSet, basename="batiment")
router.register(r"niveaux", NiveauViewSet, basename="niveau")
router.register(r"poteaux", PoteauViewSet, basename="poteau")
router.register(r"types-poteaux", TypePoteauViewSet, basename="typepoteau")

urlpatterns = [
    path("", include(router.urls)),
]
