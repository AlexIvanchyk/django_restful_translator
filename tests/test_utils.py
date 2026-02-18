from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import override

from django_localekit.models import Translation
from django_localekit.utils import get_translation
from tests.test_app.models import Book


class GetTranslationTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="World")
        ct = ContentType.objects.get_for_model(Book)
        Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )
        Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="summary",
            field_value="Mundo",
        )

    def test_returns_original_when_language_matches_default(self):
        with override("en"):
            self.assertEqual(get_translation(self.book, "title"), "Hello")
            self.assertEqual(get_translation(self.book, "summary"), "World")

    def test_returns_translated_when_language_differs(self):
        with override("es"):
            self.assertEqual(get_translation(self.book, "title"), "Hola")
            self.assertEqual(get_translation(self.book, "summary"), "Mundo")

    def test_as_dict_returns_lang_to_value(self):
        result = get_translation(self.book, "title", as_dict=True)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("es"), "Hola")

    def test_prefetch_avoids_extra_queries(self):
        books = list(Book.objects.prefetch_related("translations").all())
        self.assertEqual(len(books), 1)
        with override("es"):
            self.assertEqual(get_translation(books[0], "title"), "Hola")


class GetTranslationNoTranslationsTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="NoTrans", summary="NoTransSummary")

    def test_returns_field_value_when_no_translations_exist_in_default_lang(self):
        with override("en"):
            self.assertEqual(get_translation(self.book, "title"), "NoTrans")

    def test_returns_field_value_when_no_translation_for_requested_lang(self):
        with override("es"):
            self.assertEqual(get_translation(self.book, "title"), "NoTrans")

    def test_as_dict_returns_empty_dict_when_no_translations_exist(self):
        result = get_translation(self.book, "title", as_dict=True)
        self.assertEqual(result, {})
