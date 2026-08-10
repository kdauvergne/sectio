from rest_framework import serializers

from .models import Calcul


class CalculSerializer(serializers.ModelSerializer):
    """Lecture seule : un Calcul ne se modifie jamais."""

    class Meta:
        model = Calcul
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        for champ in fields.values():
            champ.read_only = True
        return fields
