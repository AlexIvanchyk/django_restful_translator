from typing import Union

from django.conf import settings
from django.utils.translation import get_language


def get_translation(instance, field_name, as_dict: bool = False) -> Union[str, None, dict[str, str]]:
    """
    Return the translation for the given field on the instance.

    For list views, use prefetch_related('translations') on the queryset to avoid N+1 queries.
    """
    translations = list(instance.translations.all())

    if as_dict:
        return {trans.language: trans.field_value for trans in translations if trans.field_name == field_name}
    user_language = get_language()
    if user_language != settings.LANGUAGE_CODE:
        for trans in translations:
            if trans.field_name == field_name and trans.language == user_language:
                return trans.field_value
    return getattr(instance, field_name)
