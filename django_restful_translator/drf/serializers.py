from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import translation
from rest_framework import serializers

from django_restful_translator.models import Translation
from django_restful_translator.utils import get_translation
from .fields import GetTextCharField, AutoTranslatableDictField


class TranslatableDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in instance.translatable_fields:
            if field_name in self.fields:
                data[field_name] = get_translation(instance, field_name)
        return data


class TranslatableDBDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in instance.translatable_fields:
            if field_name in self.fields:
                data[field_name] = {settings.LANGUAGE_CODE: getattr(instance, field_name)} | get_translation(instance,
                                                                                                             field_name,
                                                                                                             as_dict=True)
        return data


class TranslatableWritebleDBDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.Meta.model.translatable_fields:
            if field_name in self.fields:
                if not isinstance(self.fields[field_name], AutoTranslatableDictField):
                    self.fields[field_name] = AutoTranslatableDictField(required=False)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for field_name in instance.translatable_fields:
            if field_name in self.fields:
                data[field_name] = {settings.LANGUAGE_CODE: getattr(instance, field_name)} | get_translation(instance,
                                                                                                             field_name,
                                                                                                             as_dict=True)
        return data

    def create(self, validated_data):
        translations_data = self.extract_translations_data(validated_data)
        instance = self.Meta.model.objects.create(**validated_data)
        self.update_translations(instance, translations_data)
        return instance

    def update(self, instance, validated_data):
        translations_data = self.extract_translations_data(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self.update_translations(instance, translations_data)
        return instance

    def extract_translations_data(self, validated_data):
        translations_data = {}
        for field in self.Meta.model.translatable_fields:
            if field in validated_data and isinstance(validated_data[field], dict):
                translations_data[field] = validated_data.pop(field)
        return translations_data

    def update_translations(self, instance, translations_data):
        for field, value in translations_data.items():
            for lang_code, text in value.items():
                self.set_translation(instance, field, lang_code, text)

    def set_translation(self, instance, field, lang_code, text):
        if lang_code != settings.LANGUAGE_CODE:
            Translation.objects.update_or_create(
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
                field_name=field,
                language=lang_code,
                defaults={'field_value': text}
            )
        else:
            setattr(instance, field, text)
            instance.save()


class TranslatableGettextSerializer(serializers.ModelSerializer):
    class Meta:
        model = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in instance.translatable_fields:
            if field_name in self.fields:
                value = getattr(instance, field_name)
                data[field_name] = GetTextCharField().to_representation(value)
        return data


class TranslatableGettextDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in instance.translatable_fields:
            if field_name in self.fields:
                translations = {}
                for lang_code, lang_name in settings.LANGUAGES:
                    value = getattr(instance, field_name)
                    if lang_code == settings.LANGUAGE_CODE:
                        translations[lang_code] = value
                    with translation.override(lang_code):
                        translated_value = GetTextCharField().to_representation(value)
                        if value != translated_value:
                            translations[lang_code] = translated_value
                data[field_name] = translations
        return data
