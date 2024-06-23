import os
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.models import Translation
from django_restful_translator.processors.model import TranslationModelProcessor, TranslationFromPOEntry
from django_restful_translator.processors.po import DRTPoFileManager
from django_restful_translator.utils import handle_futures


class Command(BaseCommand):
    help = 'Import .po files to DB translations'

    def handle_language(self, language_code):
        # Skip default language
        if language_code == settings.LANGUAGE_CODE:
            self.stdout.write(self.style.WARNING(f"Skipping {language_code} because it is the default language."))
            return

        # Create a PO file manager instance
        po_file_manager = DRTPoFileManager()
        po_file_path = po_file_manager.get_po_file_path(language_code)

        # Check the last modification time of the .po file
        if os.path.isfile(po_file_path):
            po_file_mod_time = os.path.getmtime(po_file_path)
            try:
                # Get the last update time of the Translation objects for the current language
                last_translation_update = Translation.objects.filter(language=language_code).latest(
                    'updated_at').updated_at.timestamp()
                # Only proceed if the .po file is newer than the last update in the database
                if po_file_mod_time <= last_translation_update:
                    mess = (f"Skipping {language_code} "
                            f"because the .po file is older than the last update in the database")
                    self.stdout.write(
                        self.style.WARNING(mess))
                    return
            except Translation.DoesNotExist:
                pass
        else:
            self.stdout.write(self.style.WARNING(f"Skipping {language_code} because the .po file does not exist"))
            return

        po_file = po_file_manager.load_po_file(po_file_path)
        translation_processor = TranslationModelProcessor(language_code)
        translatable_models = translation_processor.get_translatable_models()

        # Process the PO file entries
        for entry in po_file:
            TranslationFromPOEntry(entry, language_code, translatable_models).update_or_create_translation()

    def handle(self, *args, **options):
        futures = []
        with ThreadPoolExecutor(max_workers=len(settings.LANGUAGES)) as executor:
            for language_set in settings.LANGUAGES:
                language = language_set[0]
                futures.append(executor.submit(self.handle_language, language))

            handle_futures(futures, self.stdout, self.style)
