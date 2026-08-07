from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """Utilisateur de Sectio. Identification par e-mail plutôt que par pseudo."""

    email = models.EmailField("adresse e-mail", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # noqa: RUF012

    def __str__(self):
        return self.email
