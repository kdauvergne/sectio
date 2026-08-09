from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        utilisateur = self.model(email=self.normalize_email(email), **extra_fields)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractUser):
    """Utilisateur de Sectio. Identification par e-mail plutôt que par pseudo."""

    username = None
    email = models.EmailField("adresse e-mail", unique=True)
    first_name = models.CharField("prénom", max_length=150)
    last_name = models.CharField("nom", max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # noqa: RUF012

    objects = UtilisateurManager()  # type: ignore[assignment]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
