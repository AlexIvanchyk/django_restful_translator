import html

from concurrent.futures import ThreadPoolExecutor, as_completed

from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.translation_providers import TranslationProvider
from django_restful_translator.utils import fetch_translatable_fields, replace_placeholders_with_tokens, \
    replace_tokens_with_placeholders, get_batches


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
            '--target_language',
            type=str,
            help='Specify the provider target language if it differs from the setting language',
            default=None
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
            '--without_batch',
            action='store_true',
            help='One request per one unit of text'
        )

    def translate_item(self, translation, provider, target_language, translate_all):
        if len(translation.field_value) > 0 and not translate_all:
            return
        text = getattr(translation.content_object, translation.field_name)
        text_with_tokens, tokens = replace_placeholders_with_tokens(text)
        translated_text = provider.translate_text(text_with_tokens, settings.LANGUAGE_CODE, target_language)
        translated_text = replace_tokens_with_placeholders(translated_text, tokens)
        decoded_text = html.unescape(translated_text)
        translation.field_value = decoded_text
        translation.save()

        self.stdout.write(
            f'Translated {translation.content_object._meta.model_name} field {translation.field_name} to {target_language}')

    def translate_batch(self, translations, provider, target_language, translate_all=False):
        content_to_translate = []
        original_translations = []
        tokens_list = []

        for translation in translations:
            if len(translations.field_value) > 0 and not translate_all:
                continue
            original_text = getattr(translation.content_object, translation.field_name)
            text_with_tokens, tokens = replace_placeholders_with_tokens(original_text)
            content_to_translate.append(text_with_tokens)
            tokens_list.append(tokens)
            original_translations.append(translation)

        translated_texts = provider.translate_text(content_to_translate, settings.LANGUAGE_CODE,
                                                   target_language)

        for translation, tokens, translated_text in zip(original_translations, tokens_list, translated_texts):
            translated_text_with_placeholders = replace_tokens_with_placeholders(translated_text, tokens)
            translation.field_value = html.unescape(translated_text_with_placeholders)
            translation.save()
            self.stdout.write(
                f'Translated {translation.content_object._meta.model_name} field {translation.field_name} to {target_language}')

    def handle(self, *args, **options):
        language = options['language']
        target_language = options.pop('target_language', language)
        provider_name = options['provider']
        translate_all = options['all']
        workers = options['workers']
        without_batch = options['without_batch']

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

        if without_batch or provider.batch_size == 1:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(self.translate_item, trans, provider, target_language, translate_all)
                    for trans in translations_qs
                ]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error occurred: {e}"))
        else:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(self.translate_batch, batch, provider, target_language, translate_all)
                    for batch in get_batches(translations_qs, provider.batch_size)
                ]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error occurred: {e}"))
