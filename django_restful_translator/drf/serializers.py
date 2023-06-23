from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from rest_framework import serializers

from django_restful_translator.models import TranslatableModel
from django_restful_translator.utils import get_translation
from .fields import GetTextCharField


class TranslatableDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatableModel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in instance.translatable_fields:
            data[field] = get_translation(instance, field)
        return data


class TranslatableDBDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatableModel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in instance.translatable_fields:
            data[field] = {settings.LANGUAGE_CODE: getattr(instance, field)} | get_translation(instance, field,
                                                                                               as_dict=True)
        return data


class TranslatableGettextSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatableModel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in instance.translatable_fields:
            # Using gettext to get translations
            value = getattr(instance, field)
            data[field] = GetTextCharField().to_representation(value)
        return data


class TranslatableGettextDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatableModel
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in instance.translatable_fields:
            translations = {}
            for lang_code, lang_name in settings.LANGUAGES:
                with translation.override(lang_code):
                    value = getattr(instance, field)
                    translations[lang_code] = _(value)
            data[field] = translations
        return data
