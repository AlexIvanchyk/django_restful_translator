from django.conf import settings
from django.apps import apps
from django.utils.translation import get_language
from django_restful_translator.models import TranslatableModel, Translation

def get_translation(instance, field_name, as_dict=False):
    translations = list(instance.translations.all())

    if as_dict:
        return {trans.language: trans.field_value for trans in translations if trans.field_name == field_name}
    else:
        user_language = get_language()
        if user_language != settings.LANGUAGE_CODE:
            for trans in translations:
                if trans.field_name == field_name and trans.language == user_language:
                    return trans.field_value
        return getattr(instance, field_name)


def fetch_translatable_fields(language):
    models = apps.get_models()
    translatable_models = [model for model in models if issubclass(model, TranslatableModel)]

    collected_translations = []

    for model in translatable_models:
        objects = model.objects.all().prefetch_related('translations')
        for obj in objects:
            for field_name in model.translatable_fields:
                original_field_value = getattr(obj, field_name)

                if original_field_value is None or original_field_value == '':
                    continue

                trans = next((t for t in obj.translations.all() if
                              t.field_name == field_name and t.language == language), None)

                if not trans:
                    trans = Translation(
                        content_object=obj,
                        field_name=field_name,
                        language=language,
                        field_value=original_field_value if language == settings.LANGUAGE_CODE else ""
                    )

                collected_translations.append(trans)
    return collected_translations

