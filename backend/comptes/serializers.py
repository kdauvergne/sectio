from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class InscriptionSerializer(serializers.ModelSerializer):
    """Création d'un compte utilisateur."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "first_name", "last_name", "password"]  # noqa: RUF012

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
