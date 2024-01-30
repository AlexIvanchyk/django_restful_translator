import os
import re
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


def get_po_file_path(language):
    po_path = os.path.join(settings.BASE_DIR, 'drt_locale', language, 'LC_MESSAGES')
    os.makedirs(po_path, exist_ok=True)
    po_file_path = os.path.join(po_path, 'django.po')
    return po_file_path


def get_po_metadata():
    return {
        'Content-Type': 'text/plain; charset=UTF-8',
        'Content-Transfer-Encoding': '8bit',
    }


def replace_placeholders_with_tokens(text):
    placeholders = re.findall(r'\{.*?\}', text)
    tokens = {}
    counter = 1
    for placeholder in placeholders:
        token = f"__TOKEN{counter}__"
        counter += 1
        tokens[token] = placeholder
        text = text.replace(placeholder, token)
    return text, tokens


def replace_tokens_with_placeholders(text, tokens):
    for token, placeholder in tokens.items():
        text = text.replace(token, placeholder)
    return text
