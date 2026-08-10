from collections import Counter

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

    def validate_projet(self, projet):
        utilisateur = self.context["request"].user
        if not projet.membres.filter(pk=utilisateur.pk).exists():
            raise serializers.ValidationError("Projet inconnu.")
        return projet


class NiveauSerializer(serializers.ModelSerializer):
    class Meta:
        model = Niveau
        fields = ["id", "batiment", "nom", "ordre", "fck", "fyk", "classe_exposition"]  # noqa: RUF012

    def validate_batiment(self, batiment):
        utilisateur = self.context["request"].user
        if not batiment.projet.membres.filter(pk=utilisateur.pk).exists():
            raise serializers.ValidationError("Bâtiment inconnu.")
        return batiment


class PoteauListSerializer(serializers.ListSerializer):
    """Borne la taille d'une création en lot et interdit les repères en double."""

    MAX_ELEMENTS = 100

    def validate(self, attrs):
        if len(attrs) > self.MAX_ELEMENTS:
            raise serializers.ValidationError(
                f"Maximum {self.MAX_ELEMENTS} poteaux par envoi."
            )

        compteur = Counter(
            (element["niveau"].pk, element["repere"]) for element in attrs
        )
        doublons = sorted(
            repere for (_, repere), nombre in compteur.items() if nombre > 1
        )
        if doublons:
            raise serializers.ValidationError(
                f"Repères en double dans l'envoi : {', '.join(doublons)}."
            )

        return attrs


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
        list_serializer_class = PoteauListSerializer

    def validate(self, attrs):
        type_section = attrs.get("type_section")

        if type_section == Poteau.TypeSection.RECTANGULAIRE and (
            attrs.get("b") is None or attrs.get("h") is None
        ):
            raise serializers.ValidationError("Une section rectangulaire exige b et h.")

        if (
            type_section == Poteau.TypeSection.CIRCULAIRE
            and attrs.get("diametre") is None
        ):
            raise serializers.ValidationError(
                "Une section circulaire exige le diamètre."
            )

        return attrs

    def validate_type_poteau(self, type_poteau):
        if type_poteau is None:
            return None

        utilisateur = self.context["request"].user
        projet = type_poteau.niveau.batiment.projet
        if not projet.membres.filter(pk=utilisateur.pk).exists():
            raise serializers.ValidationError("Type de poteau inconnu.")

        return type_poteau

    def validate_niveau(self, niveau):
        utilisateur = self.context["request"].user
        if not niveau.batiment.projet.membres.filter(pk=utilisateur.pk).exists():
            raise serializers.ValidationError("Niveau inconnu.")
        return niveau


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
