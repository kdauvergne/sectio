from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from .models import Utilisateur


class InscriptionSerializer(serializers.ModelSerializer):
    """Création d'un compte utilisateur."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "password"]  # noqa: RUF012

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class MonCompteSerializer(serializers.ModelSerializer):
    """Fiche de l'utilisateur connecté"""

    class Meta:
        model = Utilisateur
        fields = ["id", "email", "first_name", "last_name"]  # noqa: RUF012
        read_only_fields = fields


class DemandeResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )

    def validate(self, attrs):
        try:
            pk = force_str(urlsafe_base64_decode(attrs["uid"]))
            utilisateur = Utilisateur.objects.get(pk=pk)
        except (TypeError, ValueError, Utilisateur.DoesNotExist):
            raise serializers.ValidationError("Lien invalide ou expiré.") from None

        if not default_token_generator.check_token(utilisateur, attrs["token"]):
            raise serializers.ValidationError("Lien invalide ou expiré.")

        attrs["utilisateur"] = utilisateur

        return attrs

    def save(self, **kwargs):
        utilisateur = self.validated_data["utilisateur"]  # type: ignore[index]
        utilisateur.set_password(self.validated_data["new_password"])  # type: ignore[index]
        utilisateur.save()
