from django import forms
from django.conf import settings
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet

from django_restful_translator.models import Translation


class TranslationFormSet(BaseGenericInlineFormSet):
    def clean(self):
        super().clean()

        # We'll keep track of unique values as we go
        unique_values = set()
        for form in self.forms:
            # Skip empty forms or forms with errors
            if not form.is_valid() or form in self.deleted_forms:
                continue

            language = form.cleaned_data['language']
            field_name = form.cleaned_data['field_name']

            # Check if this combination already exists
            if (language, field_name) in unique_values:
                raise forms.ValidationError("Translation already exists for this language and field name.")
            unique_values.add((language, field_name))


class TranslationForm(forms.ModelForm):
    class Meta:
        model = Translation
        fields = '__all__'


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
        if db_field.name == 'field_name':
            if hasattr(self, 'parent_model') and self.parent_model:
                field.widget = forms.Select(choices=[(f, f) for f in self.parent_model.translatable_fields])
        return field

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        field = super().formfield_for_choice_field(db_field, request, **kwargs)
        if db_field.name == 'language':
            field.choices = [choice for choice in field.choices if choice[0] != settings.LANGUAGE_CODE]
        return field
