from concurrent.futures import as_completed

from django.conf import settings
from django.utils.translation import get_language


def get_translation(instance, field_name, as_dict=False):
    translations = list(instance.translations.all())

    if as_dict:
        return {trans.language: trans.field_value for trans in translations if trans.field_name == field_name}
    user_language = get_language()
    if user_language != settings.LANGUAGE_CODE:
        for trans in translations:
            if trans.field_name == field_name and trans.language == user_language:
                return trans.field_value
    return getattr(instance, field_name)


def handle_futures(futures, stdout, style):
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            stdout.write(style.ERROR(f"Error occurred: {e}"))
