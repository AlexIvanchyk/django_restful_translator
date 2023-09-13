import os

import polib
from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.utils import fetch_translatable_fields


class Command(BaseCommand):
    help = 'Generate .po files from DB translations'

    def handle(self, *args, **options):
        for language_set in settings.LANGUAGES:
            language = language_set[0]
            po_path = os.path.join(settings.BASE_DIR, 'drt_locale', language, 'LC_MESSAGES')
            os.makedirs(po_path, exist_ok=True)
            po_file_path = os.path.join(po_path, 'django.po')

            if os.path.isfile(po_file_path):
                po = polib.pofile(po_file_path)
            else:
                po = polib.POFile()

            translations = fetch_translatable_fields(language)

            for trans in translations:
                self.write_to_po_file(po, trans)

            po.metadata = {
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding': '8bit',
            }
            po.save(po_file_path)

    def write_to_po_file(self, po, trans):
        entry = polib.POEntry(
            msgid=getattr(trans.content_object, trans.field_name),
            msgstr=trans.field_value,
            tcomment=f"{trans.content_object._meta.model_name}__{trans.field_name}__{trans.object_id}"
        )
        if not trans.field_value:
            entry.flags.append('fuzzy')
        po.append(entry)
