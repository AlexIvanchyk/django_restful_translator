from django.test import TestCase, override_settings


class DrtSystemChecksTest(TestCase):
    def _run_checks(self):
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command("check", "--deploy", stdout=out, stderr=out, verbosity=0)

    def test_app_is_configured(self):
        from django.apps import apps

        app = apps.get_app_config("django_localekit")
        self.assertEqual(app.name, "django_localekit")
        self.assertEqual(app.verbose_name, "Django Locale Kit")

    def test_check_passes_with_valid_settings(self):
        from django_localekit.apps import check_dlk_settings

        errors = check_dlk_settings(None)
        self.assertEqual(errors, [])

    @override_settings(LANGUAGES=None)
    def test_check_errors_when_languages_missing(self):
        from django_localekit.apps import check_dlk_settings

        errors = check_dlk_settings(None)
        ids = [e.id for e in errors]
        self.assertIn("django_localekit.E001", ids)

    @override_settings(LANGUAGE_CODE=None)
    def test_check_errors_when_language_code_missing(self):
        from django_localekit.apps import check_dlk_settings

        errors = check_dlk_settings(None)
        ids = [e.id for e in errors]
        self.assertIn("django_localekit.E002", ids)

    def test_check_warns_when_base_dir_missing(self):
        from django.conf import settings

        from django_localekit.apps import check_dlk_settings

        original = getattr(settings, "BASE_DIR", None)
        try:
            del settings.BASE_DIR
            errors = check_dlk_settings(None)
            ids = [e.id for e in errors]
            self.assertIn("django_localekit.W001", ids)
        finally:
            if original is not None:
                settings.BASE_DIR = original
