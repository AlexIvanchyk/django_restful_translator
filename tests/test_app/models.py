from django.db import models

from django_localekit.models import TranslatableModel


class Book(TranslatableModel):
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)

    translatable_fields = ["title", "summary"]
