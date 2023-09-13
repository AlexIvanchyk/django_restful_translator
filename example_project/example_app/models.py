from django.db import models
from django_restful_translator.models import TranslatableModel


class ExampleModel(TranslatableModel):
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    translatable_fields = ['name', 'description']
