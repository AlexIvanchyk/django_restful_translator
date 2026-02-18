from unittest.mock import MagicMock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_localekit.models import Translation
from django_localekit.processors.translation_service import (
    TranslationService,
)
from tests.test_app.models import Book


class MockProvider:
    name = "mock"
    batch_size = 2

    def translate_text(self, text, source_language, target_language):
        if isinstance(text, list):
            return [f"{t}-translated" for t in text]
        return f"{text}-translated"


class TranslationServiceTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="World")
        ct = ContentType.objects.get_for_model(Book)
        self.trans = Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="",
        )

    def test_translate_item_updates_field_value(self):
        provider = MockProvider()
        service = TranslationService(provider, "es")
        service.translate_item(self.trans)
        self.trans.refresh_from_db()
        self.assertEqual(self.trans.field_value, "Hello-translated")

    def test_translate_item_calls_progress_callback(self):
        provider = MockProvider()
        messages = []
        service = TranslationService(provider, "es", progress_callback=messages.append)
        service.translate_item(self.trans)
        self.assertEqual(len(messages), 1)
        self.assertIn("es", messages[0])

    def test_translate_batch(self):
        trans2 = Translation.objects.create(
            content_type=ContentType.objects.get_for_model(Book),
            object_id=str(self.book.pk),
            language="es",
            field_name="summary",
            field_value="",
        )
        provider = MockProvider()
        service = TranslationService(provider, "es")
        result = list(service.translate_batch([self.trans, trans2]))
        self.trans.refresh_from_db()
        trans2.refresh_from_db()
        self.assertEqual(self.trans.field_value, "Hello-translated")
        self.assertEqual(trans2.field_value, "World-translated")
        self.assertEqual(len(result), 2)

    def test_placeholder_preserved(self):
        self.book.title = "Hello {name}"
        self.book.save()
        self.trans.refresh_from_db()
        self.trans.field_value = ""
        self.trans.save()
        provider = MagicMock()

        def _translate(text, s, t):
            if isinstance(text, str):
                return text.replace("Hello", "Hola")
            return [x.replace("Hello", "Hola") for x in text]

        provider.translate_text = _translate
        provider.name = "mock"
        provider.batch_size = 1
        service = TranslationService(provider, "es")
        service.translate_item(self.trans)
        self.trans.refresh_from_db()
        self.assertIn("{name}", self.trans.field_value)
