from django.test import TestCase, override_settings

from django_localekit.models import Translation
from tests.test_app.models import Book


class AutoCreateTranslationsSignalTest(TestCase):
    @override_settings(DLK_AUTO_CREATE_TRANSLATIONS=True)
    def test_creates_empty_translations_on_save(self):
        from django_localekit import signals  # noqa: F401 — ensure signal is connected

        book = Book.objects.create(title="Signal Test", summary="Summary")
        translations = Translation.objects.filter(object_id=str(book.pk))
        languages = {t.language for t in translations}
        self.assertIn("es", languages)
        self.assertNotIn("en", languages)

    @override_settings(DLK_AUTO_CREATE_TRANSLATIONS=True)
    def test_creates_translation_rows_for_all_translatable_fields(self):
        from django_localekit import signals  # noqa: F401

        book = Book.objects.create(title="Fields Test", summary="Field Summary")
        field_names = set(
            Translation.objects.filter(object_id=str(book.pk), language="es").values_list("field_name", flat=True)
        )
        self.assertIn("title", field_names)
        self.assertIn("summary", field_names)

    @override_settings(DLK_AUTO_CREATE_TRANSLATIONS=True)
    def test_created_translations_have_empty_field_value(self):
        from django_localekit import signals  # noqa: F401

        book = Book.objects.create(title="Empty Value", summary="Check")
        for trans in Translation.objects.filter(object_id=str(book.pk), language="es"):
            self.assertEqual(trans.field_value, "")

    @override_settings(DLK_AUTO_CREATE_TRANSLATIONS=False)
    def test_does_not_create_translations_when_setting_is_false(self):
        book = Book.objects.create(title="No Auto", summary="No Auto Summary")
        count = Translation.objects.filter(object_id=str(book.pk)).count()
        self.assertEqual(count, 0)

    @override_settings(DLK_AUTO_CREATE_TRANSLATIONS=True)
    def test_does_not_create_duplicate_on_update(self):
        from django_localekit import signals  # noqa: F401

        book = Book.objects.create(title="Once", summary="")
        count_after_create = Translation.objects.filter(object_id=str(book.pk), language="es").count()
        book.title = "Updated"
        book.save()
        count_after_update = Translation.objects.filter(object_id=str(book.pk), language="es").count()
        self.assertEqual(count_after_create, count_after_update)
