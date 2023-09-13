from django.core.management.base import BaseCommand
from django_restful_translator.translation_providers import TranslationProvider
from django_restful_translator.utils import fetch_translatable_fields
from django.conf import settings


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

    def handle(self, *args, **options):
        language = options['language']
        provider_name = options['provider']
        translate_all = options['all']

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
        translations = fetch_translatable_fields(language)

        for trans in translations:
            if len(trans.field_value) > 0 and not translate_all:
                continue
            text = getattr(trans.content_object, trans.field_name)
            translated_text = provider.translate_text(text, settings.LANGUAGE_CODE, language)

            trans.field_value = translated_text
            trans.save()

            self.stdout.write(
                f'Translated {trans.content_object._meta.model_name} field {trans.field_name} to {language}')
