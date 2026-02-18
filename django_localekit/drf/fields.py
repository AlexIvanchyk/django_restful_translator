from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class GetTextCharField(serializers.CharField):
    def to_representation(self, value):
        if value is None:
            return None
        return str(_(value)) or value


class GetTextListField(serializers.ListField):
    def to_representation(self, data):
        if data is None:
            return None
        output = []
        for value in data:
            output.append(str(_(value)) if value is not None else value)
        return output


class AutoTranslatableJsonField(serializers.JSONField):
    def to_representation(self, value):
        if value is None or not isinstance(value, dict):
            return value
        return {lang: str(_(text)) if text is not None else text for lang, text in value.items()}
