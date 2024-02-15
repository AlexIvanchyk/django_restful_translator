import os
import threading

import polib
from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.utils import fetch_translatable_fields, get_po_file_path, get_po_metadata


class Command(BaseCommand):
    help = 'Generate .po files from DB translations'

    def generate_po_for_language(self, language_set):
        language = language_set[0]
        po_file_path = get_po_file_path(language)

        if os.path.isfile(po_file_path):
            po = polib.pofile(po_file_path)
        else:
            po = polib.POFile()

        translations = fetch_translatable_fields(language)

        for trans in translations:
            self.write_to_po_file(po, trans)

        po.metadata = get_po_metadata()
        po.save(po_file_path)

    def write_to_po_file(self, po, trans):
        msgid_value = getattr(trans.content_object, trans.field_name)

        # Find existing entry in po file by msgid
        existing_entry = po.find(msgid_value)

        comment = f"{trans.content_object._meta.model_name}__{trans.field_name}__{trans.object_id}"

        # If the msgid already exists, append a comment; otherwise, add a new entry.
        if existing_entry:
            if comment not in existing_entry.tcomment:
                existing_entry.tcomment += f"\n{comment}"
        else:
            entry = polib.POEntry(
                msgid=msgid_value,
                msgstr=trans.field_value,
                tcomment=comment
            )
            if not trans.field_value:
                entry.flags.append('fuzzy')
            po.append(entry)

    def handle(self, *args, **options):
        threads = []

        for language_set in settings.LANGUAGES:
            t = threading.Thread(target=self.generate_po_for_language, args=(language_set,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
