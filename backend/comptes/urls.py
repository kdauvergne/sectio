from django.urls import path

from .views import InscriptionView

urlpatterns = [
    path("inscription/", InscriptionView.as_view(), name="inscription"),
]
