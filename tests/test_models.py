from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_localekit.models import Translation
from tests.test_app.models import Book


class TranslationModelTest(TestCase):
    def test_create_translation(self):
        book = Book.objects.create(title="Hello", summary="World")
        ct = ContentType.objects.get_for_model(Book)
        trans = Translation.objects.create(
            content_type=ct,
            object_id=str(book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )
        self.assertEqual(trans.field_value, "Hola")
        self.assertEqual(trans.get_original_text(), "Hello")

    def test_get_original_text_returns_none_when_content_object_missing(self):
        ct = ContentType.objects.get_for_model(Book)
        trans = Translation.objects.create(
            content_type=ct,
            object_id="99999",
            language="es",
            field_name="title",
            field_value="Hola",
        )
        self.assertIsNone(trans.content_object)
        self.assertIsNone(trans.get_original_text())

    def test_str(self):
        book = Book.objects.create(title="X", summary="")
        ct = ContentType.objects.get_for_model(Book)
        trans = Translation.objects.create(
            content_type=ct,
            object_id=str(book.pk),
            language="en",
            field_name="title",
            field_value="X",
        )
        self.assertEqual(str(trans), f"{ct}__title__{book.pk}")

    def test_unique_together_raises_on_duplicate(self):
        book = Book.objects.create(title="Unique", summary="")
        ct = ContentType.objects.get_for_model(Book)
        Translation.objects.create(
            content_type=ct,
            object_id=str(book.pk),
            language="es",
            field_name="title",
            field_value="Único",
        )
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Translation.objects.create(
                content_type=ct,
                object_id=str(book.pk),
                language="es",
                field_name="title",
                field_value="Duplicado",
            )


class TranslatableModelTest(TestCase):
    def test_subclass_has_translations_relation(self):
        book = Book.objects.create(title="Test", summary="")
        self.assertTrue(hasattr(book, "translations"))
        self.assertEqual(list(book.translations.all()), [])
