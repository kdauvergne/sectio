from rest_framework import serializers

from .models import Projet


class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = [  # noqa: RUF012
            "id",
            "nom",
            "description",
            "date_creation",
            "membres",
            "fck",
            "fyk",
            "classe_exposition",
        ]
        read_only_fields = ["date_creation"]  # noqa: RUF012
