from rest_framework import serializers
from .models import ExampleModel
from django_restful_translator.drf.serializers import TranslatableDBSerializer, TranslatableDBDictSerializer, \
    TranslatableGettextSerializer, TranslatableGettextDictSerializer


class ExampleModelBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleModel
        fields = ('id', 'name', 'description')


class ExampleModelTranslatableDBSerializer(ExampleModelBaseSerializer, TranslatableDBSerializer):
    pass


class ExampleModelTranslatableDBDictSerializer(ExampleModelBaseSerializer, TranslatableDBDictSerializer):
    pass


class ExampleModelTranslatableGettextSerializer(ExampleModelBaseSerializer, TranslatableGettextSerializer):
    pass


class ExampleModelTranslatableGettextDictSerializer(ExampleModelBaseSerializer, TranslatableGettextDictSerializer):
    pass
