import os
import tempfile
import time
from concurrent.futures import Future
from io import StringIO
from unittest.mock import MagicMock, patch

import polib
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase, override_settings

from django_localekit.models import Translation
from tests.test_app.models import Book


def _sync_executor():
    class SyncExecutor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def submit(self, fn, *args, **kwargs):
            f = Future()
            try:
                f.set_result(fn(*args, **kwargs))
            except Exception as e:
                f.set_exception(e)
            return f

    return SyncExecutor()


@patch("django_localekit.management.commands.dlk_makemessages.ThreadPoolExecutor")
class DrtMakemessagesCommandTest(TestCase):
    def setUp(self):
        self.mock_tpe = None

    def _patch_tpe(self, mock_tpe):
        mock_tpe.return_value.__enter__.return_value = _sync_executor()
        mock_tpe.return_value.__exit__.return_value = None

    def test_dlk_makemessages_runs_without_error(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                out = StringIO()
                call_command("dlk_makemessages", stdout=out)
                self.assertNotIn("Error", out.getvalue())

    def test_dlk_makemessages_creates_po_files_when_models_exist(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                Book.objects.create(title="Test", summary="")
                out = StringIO()
                call_command("dlk_makemessages", stdout=out)
                for lang in ["en", "es"]:
                    path = os.path.join(tmp, lang, "LC_MESSAGES", "django.po")
                    self.assertTrue(os.path.isfile(path), f"Expected {path} to exist")

    def test_dlk_makemessages_writes_model_strings_as_msgids_with_tcomment(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                book = Book.objects.create(title="Hello World", summary="A book.")
                out = StringIO()
                call_command("dlk_makemessages", stdout=out)
                for lang in ["en", "es"]:
                    path = os.path.join(tmp, lang, "LC_MESSAGES", "django.po")
                    po = polib.pofile(path)
                    msgids = [e.msgid for e in po if e.msgid]
                    self.assertIn("Hello World", msgids, f"Expected 'Hello World' in {lang} PO")
                    self.assertIn("A book.", msgids, f"Expected 'A book.' in {lang} PO")
                    entry = po.find("Hello World")
                    self.assertIsNotNone(entry)
                    self.assertIsNotNone(entry.tcomment)
                    self.assertIn("book__title__", entry.tcomment)
                    self.assertIn(str(book.pk), entry.tcomment)

    def test_dlk_makemessages_language_filter_creates_only_specified_language(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                Book.objects.create(title="Filter Test", summary="")
                out = StringIO()
                call_command("dlk_makemessages", "--language=es", stdout=out)
                es_path = os.path.join(tmp, "es", "LC_MESSAGES", "django.po")
                en_path = os.path.join(tmp, "en", "LC_MESSAGES", "django.po")
                self.assertTrue(os.path.isfile(es_path))
                self.assertFalse(os.path.isfile(en_path))

    def test_dlk_makemessages_unknown_language_prints_error(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                out = StringIO()
                call_command("dlk_makemessages", "--language=xx", stdout=out)
                self.assertIn("Unknown language", out.getvalue())


@patch("django_localekit.management.commands.dlk_convert_locales.ThreadPoolExecutor")
class DrtConvertLocalesCommandTest(TestCase):
    def _patch_tpe(self, mock_tpe):
        mock_tpe.return_value.__enter__.return_value = _sync_executor()
        mock_tpe.return_value.__exit__.return_value = None

    def test_dlk_convert_locales_waits_for_futures(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        locale_name = "test_convert_locale"
        with tempfile.TemporaryDirectory() as tmp:
            locale_dir = os.path.join(tmp, locale_name)
            for lang in ["en", "es"]:
                lc = os.path.join(locale_dir, lang, "LC_MESSAGES")
                os.makedirs(lc, exist_ok=True)
                with open(os.path.join(lc, "django.po"), "w") as f:
                    f.write('msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n')
            with override_settings(BASE_DIR=tmp):
                out = StringIO()
                call_command("dlk_convert_locales", "--locale", locale_name, stdout=out)
                self.assertNotIn("Error", out.getvalue())

    def test_dlk_convert_locales_writes_entries_with_tcomment(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        book = Book.objects.create(title="MatchMe", summary="")
        locale_name = "convert_locale"
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(BASE_DIR=tmp, DLK_LOCALE_PATH=tmp):
                for lang in ["en", "es"]:
                    lc = os.path.join(tmp, locale_name, lang, "LC_MESSAGES")
                    os.makedirs(lc, exist_ok=True)
                    with open(os.path.join(lc, "django.po"), "w") as f:
                        f.write('msgid ""\nmsgstr ""\n\n' 'msgid "MatchMe"\n' 'msgstr "Translated"\n')
                out = StringIO()
                call_command("dlk_convert_locales", "--locale", locale_name, stdout=out)
                for lang in ["en", "es"]:
                    po_path = os.path.join(tmp, lang, "LC_MESSAGES", "django.po")
                    self.assertTrue(os.path.isfile(po_path))
                    po = polib.pofile(po_path)
                    entry = po.find("MatchMe")
                    self.assertIsNotNone(entry, f"Expected MatchMe in {lang} PO")
                    self.assertIsNotNone(entry.tcomment)
                    self.assertIn("book__title__", entry.tcomment)
                    self.assertIn(str(book.pk), entry.tcomment)

    def test_dlk_convert_locales_remove_used_removes_entries_from_source(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        Book.objects.create(title="RemoveMe", summary="")
        locale_name = "convert_locale"
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(BASE_DIR=tmp, DLK_LOCALE_PATH=tmp):
                lc = os.path.join(tmp, locale_name, "es", "LC_MESSAGES")
                os.makedirs(lc, exist_ok=True)
                source_po = os.path.join(lc, "django.po")
                with open(source_po, "w") as f:
                    f.write('msgid ""\nmsgstr ""\n\n' 'msgid "RemoveMe"\n' 'msgstr "Traducido"\n')
                out = StringIO()
                call_command(
                    "dlk_convert_locales",
                    "--locale",
                    locale_name,
                    "--remove-used",
                    stdout=out,
                )
                po = polib.pofile(source_po)
                self.assertIsNone(po.find("RemoveMe"), "Entry should be removed from source PO")


@patch("django_localekit.management.commands.dlk_update_database.ThreadPoolExecutor")
class DrtUpdateDatabaseCommandTest(TestCase):
    def _patch_tpe(self, mock_tpe):
        mock_tpe.return_value.__enter__.return_value = _sync_executor()
        mock_tpe.return_value.__exit__.return_value = None

    def test_dlk_update_database_skips_default_language(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        out = StringIO()
        call_command("dlk_update_database", stdout=out)
        self.assertIn("Skipping", out.getvalue())

    def test_dlk_update_database_imports_valid_entry(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        book = Book.objects.create(title="Original", summary="")
        Translation.objects.filter(object_id=str(book.pk), language="es").delete()
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                po_path = os.path.join(tmp, "es", "LC_MESSAGES", "django.po")
                os.makedirs(os.path.dirname(po_path), exist_ok=True)
                entry = polib.POEntry(
                    msgid="Original",
                    msgstr="Traducido",
                    tcomment=f"book__title__{book.pk}",
                )
                po = polib.POFile()
                po.append(entry)
                po.save(po_path)
                out = StringIO()
                call_command("dlk_update_database", stdout=out)
                trans = Translation.objects.filter(object_id=str(book.pk), language="es", field_name="title").first()
                self.assertIsNotNone(trans)
                self.assertEqual(trans.field_value, "Traducido")

    def test_dlk_update_database_skips_when_po_file_missing(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                out = StringIO()
                call_command("dlk_update_database", stdout=out)
                self.assertIn("does not exist", out.getvalue())

    def test_dlk_update_database_skips_when_po_older_than_db(self, mock_tpe):
        self._patch_tpe(mock_tpe)
        book = Book.objects.create(title="Original", summary="")
        Translation.objects.filter(object_id=str(book.pk), language="es").delete()
        ct = ContentType.objects.get_for_model(Book)
        Translation.objects.create(
            content_type=ct,
            object_id=str(book.pk),
            language="es",
            field_name="title",
            field_value="old",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(DLK_LOCALE_PATH=tmp):
                po_path = os.path.join(tmp, "es", "LC_MESSAGES", "django.po")
                os.makedirs(os.path.dirname(po_path), exist_ok=True)
                with open(po_path, "w") as f:
                    f.write(
                        'msgid ""\nmsgstr ""\n\n' f"#  book__title__{book.pk}\n" 'msgid "Original"\n' 'msgstr "New"\n'
                    )
                past = time.time() - 60
                os.utime(po_path, (past, past))
                out = StringIO()
                call_command("dlk_update_database", stdout=out)
                self.assertIn("older than the last update", out.getvalue())
                trans = Translation.objects.get(object_id=str(book.pk), language="es", field_name="title")
                self.assertEqual(trans.field_value, "old")


@patch("django_localekit.management.commands.dlk_translate_models.ThreadPoolExecutor")
class DrtTranslateModelsCommandTest(TestCase):
    def _patch_tpe(self, mock_tpe):
        mock_tpe.return_value.__enter__.return_value = _sync_executor()
        mock_tpe.return_value.__exit__.return_value = None

    @patch("django_localekit.management.commands.dlk_translate_models." "TranslationProviderFactory.get_provider")
    def test_dlk_translate_models_calls_provider_and_updates_db(self, mock_get_provider, mock_tpe):
        self._patch_tpe(mock_tpe)
        mock_provider = MagicMock()
        mock_provider.translate_text = MagicMock(return_value="Hola")
        mock_provider.batch_size = 1
        mock_provider.name = "mock"
        mock_get_provider.return_value = mock_provider
        book = Book.objects.create(title="Hello", summary="World")
        out = StringIO()
        call_command(
            "dlk_translate_models",
            "--language=es",
            "--provider=google_v2",
            stdout=out,
        )
        self.assertTrue(mock_provider.translate_text.called)
        title_trans = Translation.objects.filter(object_id=str(book.pk), language="es", field_name="title").first()
        summary_trans = Translation.objects.filter(object_id=str(book.pk), language="es", field_name="summary").first()
        self.assertIsNotNone(title_trans)
        self.assertEqual(title_trans.field_value, "Hola")
        self.assertIsNotNone(summary_trans)
        self.assertEqual(summary_trans.field_value, "Hola")

    @patch("django_localekit.management.commands.dlk_translate_models." "TranslationProviderFactory.get_provider")
    def test_dlk_translate_models_unknown_language_prints_and_returns(self, mock_get_provider, mock_tpe):
        out = StringIO()
        call_command(
            "dlk_translate_models",
            "--language=xx",
            "--provider=google_v2",
            stdout=out,
        )
        self.assertIn("Unknown language", out.getvalue())
        mock_get_provider.assert_not_called()

    @patch("django_localekit.management.commands.dlk_translate_models." "TranslationProviderFactory.get_provider")
    def test_dlk_translate_models_same_as_default_language_prints_and_returns(self, mock_get_provider, mock_tpe):
        out = StringIO()
        call_command(
            "dlk_translate_models",
            "--language=en",
            "--provider=google_v2",
            stdout=out,
        )
        self.assertIn("Cannot translate to the same language", out.getvalue())
        mock_get_provider.assert_not_called()

    @patch("django_localekit.management.commands.dlk_translate_models." "TranslationProviderFactory.get_provider")
    def test_dlk_translate_models_unknown_provider_prints_and_returns(self, mock_get_provider, mock_tpe):
        mock_get_provider.side_effect = ValueError("Unknown provider: xyz")
        out = StringIO()
        call_command(
            "dlk_translate_models",
            "--language=es",
            "--provider=xyz",
            stdout=out,
        )
        self.assertIn("Unknown provider", out.getvalue())
