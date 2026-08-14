from django.urls import path

from .views import InscriptionView, MonCompteView

urlpatterns = [
    path("inscription/", InscriptionView.as_view(), name="inscription"),
    path("me/", MonCompteView.as_view(), name="me"),
]
