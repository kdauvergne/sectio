from django.conf import settings
from django.db import models


class Calcul(models.Model):
    """Jamais modifié : un nouveau choix crée un nouveau Calcul."""

    type_poteau = models.ForeignKey(
        "projets.TypePoteau", on_delete=models.CASCADE, related_name="calculs"
    )
    calcule_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="calculs",
    )

    date_calcul = models.DateTimeField("date du calcul", auto_now_add=True)
    methode = models.CharField("méthode", max_length=100, default="methode_simplifiee")
    version_moteur = models.CharField("version du moteur de calcul", max_length=20)

    # Entrées figées au moment du calcul
    type_section = models.CharField(max_length=30)
    b = models.FloatField(null=True, blank=True)
    h = models.FloatField(null=True, blank=True)
    diametre = models.FloatField(null=True, blank=True)
    L0 = models.FloatField()
    d_prime = models.FloatField()
    G = models.FloatField()
    Q = models.FloatField()
    fck = models.FloatField()
    fyk = models.FloatField()
    classe_exposition = models.CharField(max_length=10)
    taux_travail_min = models.FloatField()

    # Resultats principaux
    As = models.FloatField("As (cm²)")
    NRd = models.FloatField("NRd (kN)")
    NEd = models.FloatField("NEd (kN)")
    as_min_gouverne = models.BooleanField(default=False)

    # Valeurs intermédiaires
    lambda_elancement = models.FloatField(
        "élancement λ"
    )  # lambda_elancement = lambda_ du moteur. Django interdit un nom de champ de finir par "_"
    alpha = models.FloatField()
    kh = models.FloatField()
    ks = models.FloatField()
    rho = models.FloatField()
    delta = models.FloatField()
    taux_travail = models.FloatField()

    # Armatures retenues
    nombre_barres_longitudinales = models.IntegerField(null=True, blank=True)
    diametre_longitudinal = models.FloatField("Øl (mm)", null=True, blank=True)
    diametre_cadres = models.FloatField("Øt (mm)", null=True, blank=True)
    espacement_central = models.FloatField(
        "espacement central (mm)", null=True, blank=True
    )
    espacement_extremites = models.FloatField(
        "espacement extrémités (mm)", null=True, blank=True
    )

    class Meta:
        verbose_name = "calcul"
        ordering = ["-date_calcul"]  # noqa: RUF012

    def __str__(self) -> str:
        return f"Calcul {self.pk} - {self.type_poteau} ({self.date_calcul:%d/%m/%Y})"


class Export(models.Model):
    """Export PDF de la note de calcul"""

    class Portee(models.TextChoices):
        """A quel niveau s'applique la NDC"""

        TYPE = "type", "Un type de poteau"
        NIVEAU = "niveau", "Un niveau"
        BATIMENT = "batiment", "Un bâtiment"
        PROJET = "projet", "Le projet entier"

    portee = models.CharField("portée", max_length=20, choices=Portee.choices)
    intitule = models.CharField("intitulé figé", max_length=200)

    calculs = models.ManyToManyField(Calcul, related_name="exports")
    exporte_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="exports"
    )

    date_export = models.DateTimeField("date d'export", auto_now_add=True)
    fichier = models.FileField("fichier PDF", upload_to="notes/%Y/%m/")

    class Meta:
        verbose_name = "export"
        ordering = ["-date_export"]  # noqa: RUF012

    def __str__(self) -> str:
        return f"Export {self.pk} - {self.intitule} ({self.date_export:%d/%m/%Y})"
