from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand

from django_localekit.management.utils import handle_futures
from django_localekit.processors.model import TranslationModelProcessor
from django_localekit.processors.po import DRTPoFileManager, TranslationDrtPoEntry


class Command(BaseCommand):
    help = "Generate .po files from DB translations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--language",
            type=str,
            default=None,
            help="Only generate the .po file for this language code (e.g. es). Defaults to all configured languages.",
        )

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
        language_filter = options["language"]

        if language_filter:
            all_codes = [lang[0] for lang in settings.LANGUAGES]
            if language_filter not in all_codes:
                self.stdout.write(self.style.ERROR(f"Unknown language: {language_filter}"))
                return
            languages = [language_filter]
        else:
            languages = [lang[0] for lang in settings.LANGUAGES]

        futures = []
        with ThreadPoolExecutor(max_workers=len(languages)) as executor:
            for language in languages:
                futures.append(executor.submit(self.generate_po_for_language, language))

            handle_futures(futures, self.stdout, self.style)
