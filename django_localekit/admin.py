from django import forms
from django.conf import settings
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet

from django_localekit.models import Translation


class TranslationFormSet(BaseGenericInlineFormSet):
    def clean(self):
        super().clean()

        unique_values = set()
        for form in self.forms:
            if not form.is_valid() or form in self.deleted_forms:
                continue

            language = form.cleaned_data["language"]
            field_name = form.cleaned_data["field_name"]

            if (language, field_name) in unique_values:
                raise forms.ValidationError("Translation already exists for this language and field name.")
            unique_values.add((language, field_name))


class TranslationForm(forms.ModelForm):
    class Meta:
        model = Translation
        fields = "__all__"


class TranslationInline(GenericTabularInline):
    model = Translation
    form = TranslationForm
    formset = TranslationFormSet
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.parent_obj = obj
        return formset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "field_name":
            parent_model = getattr(self, "parent_model", None)
            if parent_model and getattr(parent_model, "translatable_fields", None):
                field.widget = forms.Select(choices=[(f, f) for f in parent_model.translatable_fields])
            elif not parent_model:
                field.widget = forms.Select(choices=[])
        return field

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        field = super().formfield_for_choice_field(db_field, request, **kwargs)
        if db_field.name == "language":
            field.choices = [choice for choice in field.choices if choice[0] != settings.LANGUAGE_CODE]
        return field
