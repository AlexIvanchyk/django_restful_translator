from django.contrib import admin
from .models import ExampleModel
from django_restful_translator.admin import TranslationInline


class ExampleModelAdmin(admin.ModelAdmin):
    inlines = [TranslationInline]
    list_display = ('id', 'name', 'description')
    search_fields = ['name', 'description']
    list_filter = ('name',)


admin.site.register(ExampleModel, ExampleModelAdmin)
