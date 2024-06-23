from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class GetTextCharField(serializers.CharField):
    def to_representation(self, value):
        return str(_(value)) or value


class GetTextListField(serializers.ListField):
    def to_representation(self, data):
        output = []
        for value in data:
            output.append(str(_(value)) or value)
        return output


class AutoTranslatableJsonField(serializers.JSONField):
    def to_representation(self, value):
        if not isinstance(value, dict):
            return value
        return {lang: str(_(text)) for lang, text in value.items()}
