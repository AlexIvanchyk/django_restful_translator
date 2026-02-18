from django.test import TestCase

from django_localekit.drf.fields import (
    AutoTranslatableJsonField,
    GetTextCharField,
    GetTextListField,
)


class GetTextCharFieldTest(TestCase):
    def test_to_representation_value(self):
        field = GetTextCharField()
        self.assertEqual(field.to_representation("hello"), "hello")

    def test_to_representation_none(self):
        field = GetTextCharField()
        self.assertIsNone(field.to_representation(None))


class GetTextListFieldTest(TestCase):
    def test_to_representation_list(self):
        field = GetTextListField()
        result = field.to_representation(["a", "b"])
        self.assertEqual(result, ["a", "b"])

    def test_to_representation_none(self):
        field = GetTextListField()
        self.assertIsNone(field.to_representation(None))


class AutoTranslatableJsonFieldTest(TestCase):
    def test_to_representation_dict(self):
        field = AutoTranslatableJsonField()
        result = field.to_representation({"en": "Hi", "es": "Hola"})
        self.assertIsInstance(result, dict)
        self.assertIn("en", result)
        self.assertIn("es", result)

    def test_to_representation_none(self):
        field = AutoTranslatableJsonField()
        self.assertIsNone(field.to_representation(None))

    def test_to_representation_non_dict(self):
        field = AutoTranslatableJsonField()
        self.assertEqual(field.to_representation("not a dict"), "not a dict")
