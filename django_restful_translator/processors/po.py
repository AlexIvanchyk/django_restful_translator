import os

import polib
from django.conf import settings
from polib import POEntry

from django_restful_translator.models import Translation


class DrtPoEntry(POEntry):
    pass


class TranslationDrtPoEntry(DrtPoEntry):
    def __init__(self, translation_object: Translation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.translation_object = translation_object
        self.msgid = self._get_msgid()
        self.msgstr = self._get_msgstr()
        self.tcomment = self._get_tcomment()

    def _get_msgid(self):
        return self.translation_object.get_original_text()

    def _get_msgstr(self):
        return self.translation_object.field_value

    def _get_tcomment(self):
        return f"{self._get_model_name()}__{self._get_object_field_name()}__{self.translation_object.object_id}"

    def _get_model_name(self):
        return self.translation_object.content_object._meta.model_name

    def _get_object_field_name(self):
        return self.translation_object.field_name


class DRTPOFile(polib.POFile):
    @classmethod
    def from_po_file(cls, po_file: polib.POFile) -> 'DRTPOFile':
        drt_po_file = cls()
        drt_po_file.metadata = po_file.metadata
        for entry in po_file:
            drt_po_file.append(entry)
        return drt_po_file

    def set_metadata(self, metadata: dict) -> None:
        self.metadata = metadata

    def add_drt_entry(self, entry_object: DrtPoEntry) -> None:
        entry = self.find(entry_object.msgid)
        if entry:
            self._add_drt_comment(entry, entry_object.tcomment)
        else:
            self._create_drt_entry(entry_object)

    def _add_drt_comment(self, entry_object: POEntry, comment: str) -> None:
        if comment not in entry_object.tcomment:
            entry_object.tcomment += f"\n{comment}"

    def _create_drt_entry(self, entry_object: DrtPoEntry) -> None:
        if not entry_object.msgstr:
            entry_object.flags.append('fuzzy')
        self.append(entry_object)


class DRTPoFileManager:
    def __init__(self):
        self.drt_po_class = DRTPOFile

    def load_po_file(self, file_path: str) -> DRTPOFile:
        po = polib.pofile(file_path)
        drt_po_file = self.drt_po_class.from_po_file(po)
        return drt_po_file

    def load_or_create_po_file(self, po_file_path) -> DRTPOFile:
        if os.path.isfile(po_file_path):
            po = self.load_po_file(po_file_path)
        else:
            po = self.drt_po_class()
        return po

    @staticmethod
    def get_po_file_path(language_code: str) -> str:
        po_path = os.path.join(settings.BASE_DIR, 'drt_locale', language_code, 'LC_MESSAGES')
        os.makedirs(po_path, exist_ok=True)
        po_file_path = os.path.join(str(po_path), 'django.po')
        return po_file_path

    @staticmethod
    def get_po_metadata() -> dict:
        return {
            'Content-Type': 'text/plain; charset=UTF-8',
            'Content-Transfer-Encoding': '8bit',
        }

    def save_po_file(self, po_file: DRTPOFile, po_file_path: str) -> None:
        po_file.set_metadata(self.get_po_metadata())
        po_file.save(po_file_path)
