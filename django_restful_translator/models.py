from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.db import models


class Translation(models.Model):
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    field_name = models.CharField(max_length=255)
    field_value = models.TextField()
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'language', 'field_name',)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.content_type}__{self.field_name}__{self.object_id}'


class TranslatableModel(models.Model):
    translations = GenericRelation(Translation)
    translatable_fields = []

    class Meta:
        abstract = True
