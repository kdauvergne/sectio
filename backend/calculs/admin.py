from django.contrib import admin

from .models import Calcul, Export


@admin.register(Calcul)
class CalculAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "type_poteau",
        "As",
        "armatures_affichage",
        "NRd",
        "taux_travail",
        "date_calcul",
    )
    list_filter = ("methode", "as_min_gouverne")
    readonly_fields = [champ.name for champ in Calcul._meta.fields]  # noqa: RUF012

    @admin.display(description="Armatures")
    def armatures_affichage(self, obj) -> str:
        if (
            obj.nombre_barres_longitudinales is None
            or obj.diametre_longitudinal is None
        ):
            return "—"
        return f"{obj.nombre_barres_longitudinales}HA{obj.diametre_longitudinal:.0f}"


@admin.register(Export)
class ExportAdmin(admin.ModelAdmin):
    list_display = ("pk", "intitule", "portee", "date_export")
    list_filter = ("portee",)
    filter_horizontal = ("calculs",)
    readonly_fields = ("date_export",)
