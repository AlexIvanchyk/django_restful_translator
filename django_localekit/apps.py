from django.apps import AppConfig
from django.core import checks


class DjangoLocaleKitConfig(AppConfig):
    name = "django_localekit"
    verbose_name = "Django Locale Kit"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from django.conf import settings

        if getattr(settings, "DLK_AUTO_CREATE_TRANSLATIONS", False):
            from django_localekit import signals  # noqa: F401


@checks.register()
def check_dlk_settings(app_configs, **kwargs):
    from django.conf import settings

    errors = []

    if not hasattr(settings, "LANGUAGES") or not settings.LANGUAGES:
        errors.append(
            checks.Error(
                "LANGUAGES setting is required by django-localekit but is not configured.",
                hint="Add LANGUAGES to your settings, e.g. LANGUAGES = [('en', 'English'), ('es', 'Spanish')]",
                id="django_localekit.E001",
            )
        )

    if not hasattr(settings, "LANGUAGE_CODE") or not settings.LANGUAGE_CODE:
        errors.append(
            checks.Error(
                "LANGUAGE_CODE setting is required by django-localekit but is not configured.",
                hint="Add LANGUAGE_CODE to your settings, e.g. LANGUAGE_CODE = 'en'",
                id="django_localekit.E002",
            )
        )

    if not hasattr(settings, "BASE_DIR"):
        errors.append(
            checks.Warning(
                "BASE_DIR is not set. django-localekit cannot resolve the default DLK_LOCALE_PATH.",
                hint="Set BASE_DIR in your settings or set DLK_LOCALE_PATH explicitly.",
                id="django_localekit.W001",
            )
        )

    return errors
