from abc import abstractmethod
from collections.abc import Iterable

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import translation
from rest_framework import serializers

from django_restful_translator.models import Translation
from django_restful_translator.utils import get_translation
from .fields import GetTextCharField, AutoTranslatableJsonField


class BaseTranslatableSerializer(serializers.ModelSerializer):
    """
    Base serializer for handling common translation logic.
    Abstracts the translation retrieval process to be implemented by subclasses.
    """

    class Meta:
        model = None
        translatable_fields = None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in self.get_translatable_fields():
            if field_name in self.fields:
                data[field_name] = self.get_field_translation(instance, field_name)
        return data

    @abstractmethod
    def get_field_translation(self, instance, field_name):
        """
        Abstract method that should be overridden by subclasses to fetch or generate
        translations for the given field from the specified instance.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_translatable_fields(self):
        """
        Fetches the list of translatable fields based on the serializer's Meta class or model's setting.
        If 'translatable_fields' is '__all__', it returns all fields defined in the model's 'translatable_fields'.
        If it is a list, it checks the fields against the model's 'translatable_fields' to ensure validity.
        """
        model_translatable_fields = getattr(self.Meta.model, 'translatable_fields', [])

        if hasattr(self.Meta, 'translatable_fields'):
            meta_fields = self.Meta.translatable_fields

            if meta_fields == "__all__":
                return model_translatable_fields
            if isinstance(meta_fields, Iterable):
                # Validate that each field in the list is part of the model's translatable fields
                validated_fields = [field for field in meta_fields if field in model_translatable_fields]
                if not validated_fields:
                    raise ValueError("None of the specified translatable fields are recognized by the model.")
                return validated_fields
            raise ValueError("Meta.translatable_fields must be '__all__' or an iterable of field names.")

        return model_translatable_fields


class TranslatableDBSerializer(BaseTranslatableSerializer):
    """
    Handles simple translation retrieval for database stored translations.
    """

    def get_field_translation(self, instance, field_name):
        return get_translation(instance, field_name)


class TranslatableDBDictSerializer(BaseTranslatableSerializer):
    """
    Handles dictionary-based translations, useful for APIs supporting multiple languages in one response.
    """

    def get_field_translation(self, instance, field_name):
        original_text = getattr(instance, field_name)
        translations = get_translation(instance, field_name, as_dict=True)
        return {settings.LANGUAGE_CODE: original_text} | translations


class TranslatableWritableDBDictSerializer(BaseTranslatableSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_translatable_json_fields()

    def initialize_translatable_json_fields(self):
        for field_name in self.get_translatable_fields():
            if field_name in self.fields and not isinstance(self.fields[field_name], AutoTranslatableJsonField):
                self.fields[field_name] = AutoTranslatableJsonField(required=False, default=dict)

    def get_field_translation(self, instance, field_name):
        original_text = getattr(instance, field_name)
        translations = get_translation(instance, field_name, as_dict=True)
        return {settings.LANGUAGE_CODE: original_text} | translations

    def create(self, validated_data):
        translations_data = self.extract_translations_data(validated_data)
        instance = super().create(validated_data)
        self.update_translations(instance, translations_data, skip_primary=True)
        return instance

    def update(self, instance, validated_data):
        translations_data = self.extract_translations_data(validated_data)
        instance = super().update(instance, validated_data)
        self.update_translations(instance, translations_data, skip_primary=True)
        return instance

    def extract_translations_data(self, validated_data):
        translations_data = {}
        for field in self.Meta.model.translatable_fields:
            if field in validated_data and isinstance(validated_data[field], dict):
                if len(validated_data[field]) == 0:
                    validated_data.pop(field)
                    continue
                primary_lang_value = validated_data[field].pop(settings.LANGUAGE_CODE, None)
                if validated_data[field]:
                    translations_data[field] = validated_data.pop(field)
                if primary_lang_value is not None:
                    validated_data[field] = primary_lang_value

        return translations_data

    def update_translations(self, instance, translations_data, skip_primary=False):
        for field, value in translations_data.items():
            for lang_code, text in value.items():
                if skip_primary and lang_code == settings.LANGUAGE_CODE:
                    continue
                Translation.objects.update_or_create(
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=instance.id,
                    field_name=field,
                    language=lang_code,
                    defaults={'field_value': text}
                )


class TranslatableGettextSerializer(BaseTranslatableSerializer):
    """
    Uses gettext for real-time translations based on the active language.
    """

    def get_field_translation(self, instance, field_name):
        value = getattr(instance, field_name)
        return GetTextCharField().to_representation(value)


class TranslatableGettextDictSerializer(BaseTranslatableSerializer):
    """
    Provides a dictionary of all possible translations using gettext.
    """

    def get_field_translation(self, instance, field_name):
        translations = {}
        for lang_code, _ in settings.LANGUAGES:
            value = getattr(instance, field_name)
            if lang_code == settings.LANGUAGE_CODE:
                translations[lang_code] = value
            with translation.override(lang_code):
                translated_value = GetTextCharField().to_representation(value)
                if value != translated_value:
                    translations[lang_code] = translated_value
        return translations
