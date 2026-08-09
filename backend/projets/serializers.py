from rest_framework import serializers

from .models import Batiment, Niveau, Poteau, Projet


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


class BatimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batiment
        fields = ["id", "projet", "nom", "fck", "fyk", "classe_exposition"]  # noqa: RUF012


class NiveauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Niveau
        fields = ["id", "batiment", "nom", "ordre", "fck", "fyk", "classe_exposition"]  # noqa: RUF012


class PoteauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poteau
        fields = [  # noqa: RUF012
            "id",
            "niveau",
            "type_poteau",
            "repere",
            "type_section",
            "b",
            "h",
            "diametre",
            "L0",
            "d_prime",
            "G",
            "Q",
            "taux_travail_min",
            "duree_resistance_feu",
            "expose_un_seul_cote",
            "fck",
            "fyk",
            "classe_exposition",
        ]

    def validate_type_poteau(self, type_poteau):
        if type_poteau is None:
            return None

        utilisateur = self.context["request"].user
        projet = type_poteau.niveau.batiment.projet
        if not projet.membres.filter(pk=utilisateur.pk).exists():
            raise serializers.ValidationError("Type de poteau inconnu.")

        return type_poteau


class ProjetDetailSerializer(ProjetSerializer):
    """Projet avec ses bâtiments. Lecture seule sur la partie imbriquée."""

    batiments = BatimentSerializer(many=True, read_only=True)

    class Meta(ProjetSerializer.Meta):
        fields = [*ProjetSerializer.Meta.fields, "batiments"]  # noqa: RUF012


class BatimentDetailSerializer(BatimentSerializer):
    niveaux = NiveauSerializer(many=True, read_only=True)

    class Meta(BatimentSerializer.Meta):
        fields = [*BatimentSerializer.Meta.fields, "niveaux"]  # noqa: RUF012


class NiveauDetailSerializer(NiveauSerializer):
    poteaux = PoteauSerializer(many=True, read_only=True)

    class Meta(NiveauSerializer.Meta):
        fields = [*NiveauSerializer.Meta.fields, "poteaux"]  # noqa: RUF012
