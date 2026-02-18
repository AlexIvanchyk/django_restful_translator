from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from polib import POEntry

from django_localekit.models import Translation
from django_localekit.processors.model import (
    TranslationFromPOEntry,
    TranslationModelProcessor,
)
from tests.test_app.models import Book


class TranslationModelProcessorTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="World")
        self.processor = TranslationModelProcessor("es")

    def test_get_translatable_models_includes_book(self):
        models = TranslationModelProcessor.get_translatable_models()
        self.assertIn(Book, models)

    def test_create_translation(self):
        trans = self.processor.create_translation(self.book, "title", "Hello")
        self.assertIsNone(trans.pk)
        self.assertEqual(trans.field_value, "")
        self.assertEqual(trans.language, "es")
        trans_en = TranslationModelProcessor("en").create_translation(self.book, "title", "Hello")
        self.assertEqual(trans_en.field_value, "Hello")

    def test_get_translation_for_field(self):
        ct = ContentType.objects.get_for_model(Book)
        Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )
        trans = self.processor.get_translation_for_field(self.book, "title")
        self.assertIsNotNone(trans)
        self.assertEqual(trans.field_value, "Hola")

    def test_get_translations_for_object_creates_unsaved_for_missing(self):
        trans_list = self.processor.get_translations_for_object(self.book, Book)
        self.assertEqual(len(trans_list), 2)
        self.assertTrue(any(t.field_name == "title" for t in trans_list))

    def test_collect_translations_for_model(self):
        result = self.processor.collect_translations_for_model(Book)
        self.assertEqual(len(result), 2)

    def test_fetch_all_translations_returns_iterator(self):
        result = self.processor.fetch_all_translations()
        from collections.abc import Iterator

        self.assertIsInstance(result, Iterator)

    def test_fetch_all_translations_yields_expected_count(self):
        result = list(self.processor.fetch_all_translations())
        self.assertGreaterEqual(len(result), 2)

    def test_collect_translations_bulk_creates_new_rows(self):
        from django_localekit.models import Translation

        before = Translation.objects.filter(language="es").count()
        self.processor.collect_translations_for_model(Book)
        after = Translation.objects.filter(language="es").count()
        self.assertGreater(after, before)

    def test_find_original_objects_by_text(self):
        found = TranslationModelProcessor.find_original_objects_by_text([Book], "Hello")
        self.assertIsNotNone(found)
        self.assertEqual(len(found), 1)
        obj, field_name = found[0]
        self.assertEqual(obj, self.book)
        self.assertEqual(field_name, "title")


class TranslationFromPOEntryTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Original", summary="")
        self.models = [Book]

    def test_parse_tcomment_valid(self):
        entry = POEntry(msgid="Original", msgstr="Traducido", tcomment=f"book__title__{self.book.pk}")
        po = TranslationFromPOEntry(entry, "es", self.models)
        self.assertEqual(po.model, Book)
        self.assertEqual(po.field_name, "title")
        self.assertEqual(po.object_id, str(self.book.pk))
        self.assertTrue(po.is_valid())

    def test_parse_tcomment_invalid_empty(self):
        entry = POEntry(msgid="x", msgstr="y", tcomment="")
        po = TranslationFromPOEntry(entry, "es", self.models)
        self.assertFalse(po.is_valid())

    def test_update_or_create_translation(self):
        entry = POEntry(msgid="Original", msgstr="Traducido", tcomment=f"book__title__{self.book.pk}")
        po = TranslationFromPOEntry(entry, "es", self.models)
        self.assertTrue(po.is_valid())
        trans = po.update_or_create_translation()
        self.assertEqual(trans.field_value, "Traducido")
        trans.refresh_from_db()
        self.assertEqual(trans.field_value, "Traducido")
