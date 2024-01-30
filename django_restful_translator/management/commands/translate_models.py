import html

from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.translation_providers import TranslationProvider
from django_restful_translator.utils import fetch_translatable_fields, replace_placeholders_with_tokens, \
    replace_tokens_with_placeholders


class Command(BaseCommand):
    help = 'Translate model fields'
    provider_names = [cls.name for cls in TranslationProvider.__subclasses__()]

    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            help='Specify the language to which the fields should be translated'
        )
        parser.add_argument(
            '--provider',
            type=str,
            help='Specify the translation provider to use for the translation. Available providers: ' + ', '.join(
                self.provider_names)
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Translate even existing translations'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=4,
            help='Number of worker threads to use for translation'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=200,
            help='Number of translations to process in one batch'
        )

    def translate_item(self, trans, provider, language, translate_all):
        if len(trans.field_value) > 0 and not translate_all:
            return
        text = getattr(trans.content_object, trans.field_name)
        text_with_tokens, tokens = replace_placeholders_with_tokens(text)
        translated_text = provider.translate_text(text_with_tokens, settings.LANGUAGE_CODE, language)
        translated_text = replace_tokens_with_placeholders(translated_text, tokens)
        decoded_text = html.unescape(translated_text)
        trans.field_value = decoded_text
        trans.save()

        self.stdout.write(
            f'Translated {trans.content_object._meta.model_name} field {trans.field_name} to {language}')

    def handle(self, *args, **options):
        language = options['language']
        provider_name = options['provider']
        translate_all = options['all']
        workers = options['workers']
        batch_size = options['batch_size']

        if language not in [lang[0] for lang in settings.LANGUAGES]:
            self.stdout.write(f'Unknown language: {language}')
            return

        if language == settings.LANGUAGE_CODE:
            self.stdout.write('Cannot translate to the same language')
            return

        available_providers = {cls.name: cls for cls in TranslationProvider.__subclasses__()}
        provider_class = available_providers.get(provider_name)
        if not provider_class:
            self.stdout.write(f'Unknown provider: {provider_name}')
            return

        provider = provider_class()
        translations_qs = fetch_translatable_fields(language)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(self.translate_item, trans, provider, language, translate_all)
                for trans in translations_qs
            ]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error occurred: {e}"))
