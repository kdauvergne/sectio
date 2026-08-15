from django.urls import path

from .views import (
    DemandeResetPasswordView,
    InscriptionView,
    MonCompteView,
    ResetPasswordView,
)

urlpatterns = [
    path("inscription/", InscriptionView.as_view(), name="inscription"),
    path("me/", MonCompteView.as_view(), name="me"),
    path(
        "mot-de-passe-oublie/", DemandeResetPasswordView.as_view(), name="demande-reset"
    ),
    path(
        "reinitialiser-mot-de-passe/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
]
