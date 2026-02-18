from rest_framework import serializers

from django_localekit.drf.fields import AutoTranslatableJsonField
from django_localekit.drf.serializers import (
    TranslatableDBDictSerializer,
    TranslatableDBSerializer,
    TranslatableGettextDictSerializer,
    TranslatableGettextSerializer,
    TranslatableWritableDBDictSerializer,
)

from .models import ExampleModel


class ExampleModelBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = ("id", "name", "description")


class ExampleModelTranslatableDBSerializer(ExampleModelBaseSerializer, TranslatableDBSerializer):
    pass


class ExampleModelTranslatableDBDictSerializer(ExampleModelBaseSerializer, TranslatableDBDictSerializer):
    pass


class ExampleModelTranslatableWritableDBDictSerializer(
    ExampleModelBaseSerializer, TranslatableWritableDBDictSerializer
):
    name = AutoTranslatableJsonField(required=True)


class ExampleModelTranslatableGettextSerializer(ExampleModelBaseSerializer, TranslatableGettextSerializer):
    pass


class ExampleModelTranslatableGettextDictSerializer(ExampleModelBaseSerializer, TranslatableGettextDictSerializer):
    pass
