from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import CsrfViewMiddleware
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason


class JWTAuthenticationCookie(JWTAuthentication):
    def authenticate(self, request):
        token_brut = request.COOKIES.get(settings.JWT_COOKIE_ACCESS)
        if not token_brut:
            return None

        token_valide = self.get_validated_token(token_brut)
        self.check_csrf(request)
        return (self.get_user(token_valide), token_valide)

    def check_csrf(self, request):

        def dummy_get_response(request: HttpRequest) -> HttpResponse:
            return HttpResponse()

        verificateur = CSRFCheck(dummy_get_response)
        verificateur.process_request(request)
        raison = verificateur.process_view(request, None, (), {})
        if raison:
            raise exceptions.PermissionDenied(f"Contrôle CSRF a échoué : {raison}")


class JWTAuthenticationCookieScheme(OpenApiAuthenticationExtension):
    """Décrit JWTAuthenticationCookie à drf-spectacular (documentation OpenAPI)"""

    target_class = JWTAuthenticationCookie
    name = "cookieAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": settings.JWT_COOKIE_ACCESS,
        }
