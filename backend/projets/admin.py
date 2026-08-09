from django.contrib import admin

from .models import Batiment, Niveau, Poteau, Projet, TypePoteau


class BatimentInline(admin.TabularInline):
    model = Batiment
    extra = 1


class NiveauInline(admin.TabularInline):
    model = Niveau
    extra = 1


class PoteauInline(admin.TabularInline):
    model = Poteau
    extra = 3


class PoteauInlineParType(admin.TabularInline):
    model = Poteau
    extra = 0
    fields = ("repere", "type_section", "taille_affichage", "L0", "G", "Q")
    readonly_fields = ("taille_affichage",)

    @admin.display(description="Taille")
    def taille_affichage(self, obj) -> str:
        if obj.type_section == Poteau.TypeSection.CIRCULAIRE:
            return f"D={obj.diametre} m" if obj.diametre else "—"
        return f"{obj.b}×{obj.h} m" if obj.b and obj.h else "—"


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ("nom", "fck", "fyk", "date_creation")
    search_fields = ("nom",)
    filter_horizontal = ("membres",)
    inlines = [BatimentInline]  # noqa: RUF012


@admin.register(Batiment)
class BatimentAdmin(admin.ModelAdmin):
    list_display = ("nom", "projet")
    list_filter = ("projet",)
    inlines = [NiveauInline]  # noqa: RUF012


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ("nom", "batiment", "ordre")
    inlines = [PoteauInline]  # noqa: RUF012


@admin.register(Poteau)
class PoteauAdmin(admin.ModelAdmin):
    list_display = ("repere", "niveau", "type_section", "L0", "G", "Q")
    list_filter = ("type_section", "niveau")


@admin.register(TypePoteau)
class TypePoteauAdmin(admin.ModelAdmin):
    list_display = ("nom", "niveau", "calcul_actuel")
    inlines = [PoteauInlineParType]  # noqa: RUF012
