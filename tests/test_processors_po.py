import os
import tempfile

import polib
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings

from django_localekit.models import Translation
from django_localekit.processors.po import (
    DrtPoEntry,
    DRTPOFile,
    DRTPoFileManager,
    TranslationDrtPoEntry,
)
from tests.test_app.models import Book


class DRTPoFileManagerTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="World")
        ct = ContentType.objects.get_for_model(Book)
        self.trans = Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )

    def test_get_po_file_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                path = DRTPoFileManager.get_po_file_path("es")
                self.assertIn("es", path)
                self.assertIn("LC_MESSAGES", path)
                self.assertTrue(path.endswith("django.po"))

    def test_get_po_metadata(self):
        meta = DRTPoFileManager.get_po_metadata()
        self.assertIn("Content-Type", meta)

    def test_load_or_create_po_file_creates_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                path = DRTPoFileManager.get_po_file_path("es")
                manager = DRTPoFileManager()
                po = manager.load_or_create_po_file(path)
                self.assertIsInstance(po, DRTPOFile)

    def test_save_po_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                path = DRTPoFileManager.get_po_file_path("es")
                manager = DRTPoFileManager()
                po = manager.load_or_create_po_file(path)
                manager.save_po_file(po, path)
                self.assertTrue(os.path.isfile(path))


class TranslationDrtPoEntryTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="")
        ct = ContentType.objects.get_for_model(Book)
        self.trans = Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )

    def test_entry_has_msgid_msgstr_tcomment(self):
        entry = TranslationDrtPoEntry(self.trans)
        self.assertEqual(entry.msgid, "Hello")
        self.assertEqual(entry.msgstr, "Hola")
        self.assertEqual(entry.tcomment, f"book__title__{self.book.pk}")


class DRTPOFileTest(TestCase):
    def test_from_po_file(self):
        source = polib.POFile()
        source.append(polib.POEntry(msgid="x", msgstr="y"))
        drt = DRTPOFile.from_po_file(source)
        self.assertEqual(len(list(drt)), 1)

    def test_add_drt_entry_new(self):
        drt = DRTPOFile()
        entry = DrtPoEntry(msgid="a", msgstr="b", tcomment="")
        drt.add_drt_entry(entry)
        self.assertEqual(len(list(drt)), 1)

    def test_add_drt_entry_with_empty_msgstr_adds_fuzzy_flag(self):
        drt = DRTPOFile()
        entry = DrtPoEntry(msgid="untranslated", msgstr="", tcomment="some__field__1")
        drt.add_drt_entry(entry)
        added = drt.find("untranslated")
        self.assertIsNotNone(added)
        self.assertIn("fuzzy", added.flags)
