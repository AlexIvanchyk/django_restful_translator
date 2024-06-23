import os
from concurrent.futures import ThreadPoolExecutor

import polib
from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.processors.model import TranslationModelProcessor
from django_restful_translator.processors.po import DRTPoFileManager, DrtPoEntry
from django_restful_translator.utils import handle_futures


class Command(BaseCommand):
    help = 'Process existing .po files and regenerate them with specific comments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--locale',
            type=str,
            help='Specify the locale folder name'
        )
        parser.add_argument(
            '--remove-used',
            action='store_true',
            help='Remove entries used in the new .po file from the original .po file'
        )

    def handle(self, *args, **options):
        threads = []
        locale = options['locale']
        remove_used = options['remove_used']
        futures = []
        with ThreadPoolExecutor(max_workers=len(settings.LANGUAGES)) as executor:
            for language_code, _ in settings.LANGUAGES:
                futures.append(executor.submit(self.process_language, locale, language_code, remove_used))
            handle_futures(threads, self.stdout, self.style)

    def process_language(self, locale, language_code, remove_used):
        read_po_file_path = os.path.join(settings.BASE_DIR, locale, language_code, 'LC_MESSAGES', 'django.po')

        if not os.path.isfile(read_po_file_path):
            self.stdout.write(self.style.WARNING(f"Skipping {language_code} because the .po file does not exist"))
            return

        read_po_file = polib.pofile(str(read_po_file_path))

        drt_po_manager = DRTPoFileManager()
        save_po_file_path = drt_po_manager.get_po_file_path(language_code)
        save_po_file = drt_po_manager.load_or_create_po_file(save_po_file_path)
        save_po_file, used_entries = self.process_po_file(read_po_file, save_po_file)
        drt_po_manager.save_po_file(save_po_file, save_po_file_path)

        if remove_used:
            self.remove_used_entries(read_po_file, used_entries)
            read_po_file.save(str(read_po_file_path))

    def process_po_file(self, po, save_po_file):
        used_entries = []
        found_objects_cache = {}
        translatable_models = TranslationModelProcessor.get_translatable_models()
        for entry in po:
            objects_with_fields = self.find_original_objects(found_objects_cache, translatable_models, entry.msgid)
            if objects_with_fields:
                new_entry = self.create_new_entry(entry, objects_with_fields)
                save_po_file.append(new_entry)
                used_entries.append(entry)
        return save_po_file, used_entries

    def remove_used_entries(self, po, used_entries):
        for entry in used_entries:
            po.remove(entry)

    def create_new_entry(self, entry, objects_with_fields):
        tcomments = [
            f"{obj._meta.model_name}__{field_name}__{obj.pk}"
            for obj, field_name in objects_with_fields
        ]
        return DrtPoEntry(
            msgid=entry.msgid,
            msgstr=entry.msgstr,
            tcomment="\n".join(tcomments)
        )

    def find_original_objects(self, found_objects_cache, translatable_models, msgid):
        if msgid in found_objects_cache:
            return found_objects_cache[msgid]
        objects_found = TranslationModelProcessor.find_original_objects_by_text(translatable_models, msgid)

        found_objects_cache[msgid] = objects_found
        return objects_found
