from django.conf import settings
from django.db import models


class HypothesesHeritees(models.Model):
    """Recopie le palier supérieur à la création de chaque palier."""

    CHAMPS_HERITES = ("fck", "fyk", "classe_exposition")

    fck = models.FloatField("fck (MPa)", blank=True)
    fyk = models.FloatField("fyk (MPa)", blank=True)
    classe_exposition = models.CharField(
        "classe d'exposition", max_length=10, blank=True
    )

    class Meta:
        abstract = True

    @property
    def parent_hypotheses(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        if self._state.adding:
            parent = self.parent_hypotheses
            for champ in self.CHAMPS_HERITES:
                if getattr(self, champ, None) in (None, ""):
                    setattr(self, champ, getattr(parent, champ))
        super().save(*args, **kwargs)


class Projet(models.Model):
    nom = models.CharField("nom du projet", max_length=150)
    description = models.TextField("description", blank=True)
    date_creation = models.DateTimeField("date de création", auto_now_add=True)

    membres = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projets",
        verbose_name="membres",
        blank=True,
    )

    # Hypothèses générales recopiées depuis Projet dans les autres paliers inférieurs. Valeurs défauts métier.
    fck = models.FloatField("fck (MPa)", default=45.0)
    fyk = models.FloatField("fyk (MPa)", default=500.0)
    classe_exposition = models.CharField("classe d'exposition", max_length=10)

    class Meta:
        verbose_name = "projet"
        ordering = ["-date_creation"]  # noqa: RUF012

    def __str__(self) -> str:
        return self.nom


class Batiment(HypothesesHeritees):
    projet = models.ForeignKey(
        Projet, on_delete=models.CASCADE, related_name="batiments"
    )
    nom = models.CharField("nom du bâtiment", max_length=150)

    class Meta:
        verbose_name = "bâtiment"
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["projet", "nom"], name="batiment_unique_par_projet"
            ),
        ]

    @property
    def parent_hypotheses(self):
        return self.projet

    def __str__(self):
        return f"{self.projet.nom} — {self.nom}"


class Niveau(HypothesesHeritees):
    batiment = models.ForeignKey(
        Batiment, on_delete=models.CASCADE, related_name="niveaux"
    )
    nom = models.CharField("nom du niveau", max_length=100)
    ordre = models.IntegerField("ordre d'affichage", default=0)

    class Meta:
        verbose_name = "niveau"
        verbose_name_plural = "niveaux"
        ordering = ["ordre"]  # noqa: RUF012

    @property
    def parent_hypotheses(self):
        return self.batiment

    def __str__(self) -> str:
        return f"{self.batiment} / {self.nom}"


class TypePoteau(models.Model):
    niveau = models.ForeignKey(
        Niveau, on_delete=models.CASCADE, related_name="types_poteaux"
    )
    nom = models.CharField("nom du type", max_length=100)

    calcul_actuel = models.ForeignKey(
        "calculs.Calcul",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="type_courant",
        verbose_name="calcul retenu",
    )

    class Meta:
        verbose_name = "type de poteau"
        verbose_name_plural = "types de poteau"

    def __str__(self) -> str:
        return f"{self.niveau} / {self.nom}"


class Poteau(HypothesesHeritees):
    class TypeSection(models.TextChoices):
        RECTANGULAIRE = "rectangulaire", "Rectangulaire"
        CIRCULAIRE = "circulaire", "Circulaire"

    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name="poteaux")
    type_poteau = models.ForeignKey(
        TypePoteau,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="poteaux_couverts",
    )

    repere = models.CharField("repère", max_length=50)

    # Géométrie (mètres)
    type_section = models.CharField(
        "type de section", max_length=20, choices=TypeSection.choices
    )
    b = models.FloatField("b (m)", null=True, blank=True)
    h = models.FloatField("h (m)", null=True, blank=True)
    diametre = models.FloatField("D (m)", null=True, blank=True)
    L0 = models.FloatField("L0 (m)")
    d_prime = models.FloatField("d' (m)")

    # Charges (kN)
    G = models.FloatField("G (kN)")
    Q = models.FloatField("Q (kN)")

    taux_travail_min = models.FloatField("taux de travail minimal visé", default=1.0)

    # Vérification au feu
    duree_resistance_feu = models.CharField(
        "durée de résistance au feu", max_length=10, blank=True
    )
    expose_un_seul_cote = models.BooleanField("exposé sur un seul côté", default=False)

    class Meta:
        verbose_name = "poteau"
        verbose_name_plural = "poteaux"
        ordering = ["repere"]  # noqa: RUF012
        constraints = [  # noqa: RUF012
            models.CheckConstraint(
                condition=(
                    models.Q(
                        type_section="rectangulaire", b__isnull=False, h__isnull=False
                    )
                    | models.Q(type_section="circulaire", diametre__isnull=False)
                ),
                name="dimensions_coherentes_avec_type_section",
            ),
        ]

    @property
    def parent_hypotheses(self):
        return self.niveau

    def __str__(self) -> str:
        return self.repere
