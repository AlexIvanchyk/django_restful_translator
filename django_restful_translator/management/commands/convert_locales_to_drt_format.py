import os

import polib
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.models import TranslatableModel
from django_restful_translator.utils import get_po_file_path, get_po_metadata


class Command(BaseCommand):
    help = 'Process existing .po files and regenerate them with specific comments'
    found_objects_cache = {}

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
        locale = options['locale']
        remove_used = options['remove_used']

        for language_code, _ in settings.LANGUAGES:
            self.process_language(locale, language_code, remove_used)

    def process_language(self, locale, language_code, remove_used):
        read_po_file_path = os.path.join(settings.BASE_DIR, locale, language_code, 'LC_MESSAGES', 'django.po')
        save_po_file_path = get_po_file_path(language_code)

        if not os.path.isfile(read_po_file_path):
            self.stdout.write(self.style.WARNING(f"No .po file found for {language_code}."))
            return

        po = polib.pofile(read_po_file_path)
        new_po, used_entries = self.process_po_file(po)
        new_po.save(save_po_file_path)

        if remove_used:
            self.remove_used_entries(po, used_entries)
            po.save(read_po_file_path)

    def process_po_file(self, po):
        new_po = polib.POFile()
        used_entries = []

        for entry in po:
            obj, field_name = self.find_original_objects(entry.msgid)
            if obj is not None:
                new_entry = self.create_new_entry(entry, obj, field_name)
                new_po.append(new_entry)
                used_entries.append(entry)

        new_po.metadata = get_po_metadata()
        return new_po, used_entries

    def remove_used_entries(self, po, used_entries):
        for entry in used_entries:
            po.remove(entry)

    def create_new_entry(self, entry, obj, field_name):
        tcomment = f"{obj._meta.model_name}__{field_name}__{obj.id}" if obj else ""
        return polib.POEntry(
            msgid=entry.msgid,
            msgstr=entry.msgstr,
            tcomment=tcomment
        )

    def find_original_objects(self, msgid):
        if msgid in self.found_objects_cache:
            return self.found_objects_cache[msgid]

        translatable_models = [
            model for model in apps.get_models() if issubclass(model, TranslatableModel)
        ]

        for model in translatable_models:
            for field_name in getattr(model, 'translatable_fields', []):
                obj = model.objects.filter(**{field_name: msgid}).first()
                if obj:
                    self.found_objects_cache[msgid] = (obj, field_name)
                    return obj, field_name

        self.found_objects_cache[msgid] = (None, None)
        return None, None
