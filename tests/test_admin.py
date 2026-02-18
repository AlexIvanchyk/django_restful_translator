from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.test import RequestFactory, TestCase

from django_localekit.admin import TranslationFormSet, TranslationInline
from django_localekit.models import Translation
from tests.test_app.models import Book

User = get_user_model()


class TranslationInlineTest(TestCase):
    def setUp(self):
        self.site = AdminSite()

        class BookAdmin(admin.ModelAdmin):
            inlines = [TranslationInline]

        self.site.register(Book, BookAdmin)
        self.inline = TranslationInline(Book, self.site)
        self.request = RequestFactory().get("/admin/")
        self.request.user = User(is_superuser=True, is_staff=True)
        self.book = Book.objects.create(title="Test", summary="")

    def test_inline_returns_correct_formset_class(self):
        formset_class = self.inline.get_formset(self.request, obj=self.book)
        self.assertIsNotNone(formset_class)
        self.assertIs(self.inline.formset, TranslationFormSet)


class TranslationFormSetValidationTest(TestCase):
    def _make_formset(self, forms_data):
        book = Book.objects.create(title="FormsetTest", summary="")
        formset_class = generic_inlineformset_factory(
            Translation,
            fields=["language", "field_name", "field_value"],
            formset=TranslationFormSet,
            extra=len(forms_data),
            can_delete=True,
        )
        prefix = "translation"
        management_form_data = {
            f"{prefix}-TOTAL_FORMS": str(len(forms_data)),
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
        }
        post_data = {**management_form_data}
        for i, row in enumerate(forms_data):
            for key, value in row.items():
                post_data[f"{prefix}-{i}-{key}"] = value
        return formset_class(post_data, instance=book, prefix=prefix)

    def test_duplicate_language_and_field_name_raises_validation_error(self):
        duplicate_row = {"language": "es", "field_name": "title", "field_value": "Hola"}
        formset = self._make_formset([duplicate_row, duplicate_row])
        self.assertFalse(formset.is_valid())
        self.assertTrue(any("Translation already exists" in str(e) for e in formset.non_form_errors()))

    def test_unique_language_and_field_name_is_valid(self):
        formset = self._make_formset(
            [
                {"language": "es", "field_name": "title", "field_value": "Hola"},
                {"language": "es", "field_name": "summary", "field_value": "Un libro"},
            ]
        )
        self.assertTrue(formset.is_valid(), formset.errors)
