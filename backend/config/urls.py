from django.contrib import admin
from django.urls import include, path

from comptes.views import ConnexionView, DeconnexionView, RafraichirView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("projets.urls")),
    path("api/", include("comptes.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", ConnexionView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", RafraichirView.as_view(), name="token_refresh"),
    path("api/deconnexion/", DeconnexionView.as_view(), name="deconnexion"),
]
