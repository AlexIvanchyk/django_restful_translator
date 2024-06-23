from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.processors.model import TranslationModelProcessor
from django_restful_translator.processors.po import DRTPoFileManager, TranslationDrtPoEntry
from django_restful_translator.utils import handle_futures


class Command(BaseCommand):
    help = 'Generate .po files from DB translations'

    def generate_po_for_language(self, language):
        po_file_manager = DRTPoFileManager()
        po_file_path = po_file_manager.get_po_file_path(language)
        drt_po = po_file_manager.load_or_create_po_file(po_file_path)

        translation_processor = TranslationModelProcessor(language)
        translations = translation_processor.fetch_all_translations()

        for translation in translations:
            entry_object = TranslationDrtPoEntry(translation)
            drt_po.add_drt_entry(entry_object)

        po_file_manager.save_po_file(drt_po, po_file_path)

    def handle(self, *args, **options):
        futures = []
        with ThreadPoolExecutor(max_workers=len(settings.LANGUAGES)) as executor:
            for language_set in settings.LANGUAGES:
                language = language_set[0]
                futures.append(executor.submit(self.generate_po_for_language, language))

            handle_futures(futures, self.stdout, self.style)
