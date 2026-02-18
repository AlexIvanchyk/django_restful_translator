from django.contrib import admin

from django_localekit.admin import TranslationInline

from .models import ExampleModel


class ExampleModelAdmin(admin.ModelAdmin):
    inlines = [TranslationInline]
    list_display = ("id", "name", "description")
    search_fields = ["name", "description"]
    list_filter = ("name",)


admin.site.register(ExampleModel, ExampleModelAdmin)
