from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class GetTextCharField(serializers.CharField):
    def to_representation(self, value):
        return str(_(value)) or value


class GetTextListField(serializers.ListField):
    def to_representation(self, values):
        output = []
        for value in values:
            output.append(str(_(value)) or value)
        return output
