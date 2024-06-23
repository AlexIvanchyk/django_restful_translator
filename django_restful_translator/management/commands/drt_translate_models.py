from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.processors.model import TranslationModelProcessor
from django_restful_translator.processors.translation_service import TranslationService
from django_restful_translator.translation_providers import TranslationProviderFactory
from django_restful_translator.utils import handle_futures


class Command(BaseCommand):
    help = 'Translate model fields'

    @property
    def provider_names(self):
        return TranslationProviderFactory.get_provider_names()

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

    def handle(self, *args, **options):
        language = options['language']
        target_language = options['target_language'] or language
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

        try:
            provider = TranslationProviderFactory.get_provider(provider_name)
        except ValueError as e:
            self.stdout.write(str(e))
            return

        translation_processor = TranslationModelProcessor(language)
        translations_qs = translation_processor.fetch_all_translations()

        for_translation_list = []
        if not translate_all:
            for translation in translations_qs:
                if len(translation.field_value) > 0:
                    continue
                for_translation_list.append(translation)
        else:
            for_translation_list = translations_qs

        translation_service = TranslationService(provider, target_language)

        futures = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            if without_batch or provider.batch_size == 1:
                for translation in for_translation_list:
                    futures.append(executor.submit(translation_service.translate_item, translation))
            else:
                for batch in translation_service.get_batches(for_translation_list, provider.batch_size):
                    futures.append(executor.submit(translation_service.translate_batch, batch))

        handle_futures(futures, self.stdout, self.style)
