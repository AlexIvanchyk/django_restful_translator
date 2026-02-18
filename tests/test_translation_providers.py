from unittest.mock import MagicMock, patch

from django.test import TestCase

from django_localekit.translation_providers import (
    GoogleTranslateProvider,
    TranslationProvider,
    TranslationProviderFactory,
)


class TranslationProviderFactoryTest(TestCase):
    def test_get_provider_names_returns_list(self):
        names = TranslationProviderFactory.get_provider_names()
        self.assertIsInstance(names, list)
        self.assertIn("google_v2", names)
        self.assertIn("google_v3", names)
        self.assertIn("aws", names)
        self.assertIn("deepl", names)

    def test_get_available_providers_returns_dict(self):
        providers = TranslationProviderFactory.get_available_providers()
        self.assertIsInstance(providers, dict)
        self.assertIn("google_v2", providers)

    @patch("django_localekit.translation_providers.GoogleTranslateProvider.__init__", return_value=None)
    def test_get_provider_returns_instance(self, _mock_init):
        provider = TranslationProviderFactory.get_provider("google_v2")
        self.assertIsNotNone(provider)
        self.assertEqual(provider.name, "google_v2")

    def test_get_provider_unknown_raises(self):
        with self.assertRaises(ValueError) as ctx:
            TranslationProviderFactory.get_provider("nonexistent")
        self.assertIn("Unknown provider", str(ctx.exception))

    def test_recursive_discovery_finds_subclass_of_builtin(self):
        class MyCustomProvider(GoogleTranslateProvider):
            name = "my_custom"

            def __init__(self):
                pass

        try:
            names = TranslationProviderFactory.get_provider_names()
            self.assertIn("my_custom", names)
            provider = TranslationProviderFactory.get_provider("my_custom")
            self.assertIsInstance(provider, MyCustomProvider)
        finally:
            pass

    def test_recursive_discovery_finds_deeply_nested_subclass(self):
        class LevelOne(TranslationProvider):
            name = "level_one"

            def translate_text(self, text, source_language, target_language):
                return text

        class LevelTwo(LevelOne):
            name = "level_two"

        names = TranslationProviderFactory.get_provider_names()
        self.assertIn("level_one", names)
        self.assertIn("level_two", names)


class GoogleTranslateProviderTest(TestCase):
    @patch("django_localekit.translation_providers.GoogleTranslateProvider.__init__", return_value=None)
    def test_translate_text_returns_string(self, _mock_init):
        provider = GoogleTranslateProvider()
        mock_client = MagicMock()
        mock_client.translate.return_value = {"translatedText": "Hola"}
        provider.client = mock_client
        result = provider.translate_text("Hello", "en", "es")
        self.assertEqual(result, "Hola")

    def test_missing_google_library_raises_import_error(self):
        import sys
        import unittest.mock as um

        with um.patch.dict(sys.modules, {"google.cloud": None, "google.cloud.translate_v2": None}):
            with self.assertRaises((ImportError, TypeError)):
                GoogleTranslateProvider()
