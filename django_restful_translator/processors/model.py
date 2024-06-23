from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from polib import POEntry
from django.db.models import Q
from django_restful_translator.models import Translation, TranslatableModel


class TranslationModelProcessor:
    def __init__(self, language):
        self.language = language

    @staticmethod
    def get_translatable_models():
        models = apps.get_models()
        return [model for model in models if issubclass(model, TranslatableModel)]

    def create_translation(self, obj, field_name: str, original_field_value: str):
        return Translation(
            content_object=obj,
            field_name=field_name,
            language=self.language,
            field_value=original_field_value if self.language == settings.LANGUAGE_CODE else ""
        )

    def get_translation_for_field(self, obj, field_name):
        return next((t for t in obj.translations.all() if
                     t.field_name == field_name and t.language == self.language), None)

    def get_translations_for_object(self, obj, translatable_model):
        translations = []
        for field_name in translatable_model.translatable_fields:
            original_field_value = getattr(obj, field_name)
            if original_field_value:
                tranlation = self.get_translation_for_field(obj, field_name)
                if not tranlation:
                    tranlation = self.create_translation(obj, field_name, original_field_value)
                translations.append(tranlation)
        return translations

    def collect_translations_for_model(self, translatable_model):
        objects = translatable_model.objects.all().prefetch_related('translations')
        return [trans for obj in objects for trans in self.get_translations_for_object(obj, translatable_model)]

    def fetch_all_translations(self):
        all_translations = []
        for model in self.get_translatable_models():
            all_translations.extend(self.collect_translations_for_model(model))
        return all_translations

    @staticmethod
    def find_original_objects_by_text(translatable_models, original_text):
        objects_found = []

        for model in translatable_models:
            filters = Q()
            for field_name in getattr(model, 'translatable_fields', []):
                filters |= Q(**{field_name: original_text})

            objs = model.objects.filter(filters)

            for obj in objs:
                field_name = next(
                    (field for field in getattr(model, 'translatable_fields', []) if
                     getattr(obj, field) == original_text),
                    None
                )
                if field_name:
                    objects_found.append((obj, field_name))
        return objects_found if objects_found else None


class TranslationFromPOEntry:
    def __init__(self, po_entry: POEntry, language: str, translatable_models):
        self.po_entry = po_entry
        self.language = language
        self.translatable_models = translatable_models
        self.model = None
        self.field_name = None
        self.object_id = None
        self.field_value = self.po_entry.msgstr

        self._parse_tcomment()

    def _parse_tcomment(self):
        for comment in self.po_entry.tcomment.splitlines():
            model_name, field_name, object_id = comment.split("__")
            model = next((m for m in self.translatable_models if m._meta.model_name == model_name), None)
            if model:
                self.model = model
                self.field_name = field_name
                self.object_id = object_id
                break

    def is_valid(self):
        return self.model is not None and self.field_value != ""

    def update_or_create_translation(self):
        content_type = ContentType.objects.get_for_model(self.model)
        translation, created = Translation.objects.update_or_create(
            content_type=content_type,
            object_id=self.object_id,
            field_name=self.field_name,
            language=self.language,
            defaults={"field_value": self.field_value}
        )

        if not created:
            translation.field_value = self.field_value
            translation.save()

        return translation
