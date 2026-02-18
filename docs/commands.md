# Management Commands

django-localekit provides four management commands that handle the full translation lifecycle — from exporting DB content to `.po` files, importing translated files back, converting existing locale files, and running automatic machine translation.

## Locale Kit .po file format

All django-localekit `.po` files use a special **translator comment** (the `#  ` line before each entry) to link a `msgid` back to the exact model instance and field that owns it:

```
#  <model_name>__<field_name>__<object_pk>
```

For example, if an `Article` with `pk=42` has the field `title`, its entry looks like:

```po
#  article__title__42
msgid "Hello World"
msgstr ""
```

This comment is how `dlk_update_database` knows which `Translation` row to create or update when it imports a file.

---

## dlk_makemessages

Reads all `Translation` rows from the database and writes django-localekit-format `.po` files — one per configured language — into `DLK_LOCALE_PATH`.

**When to use:** after manually creating or editing translations in the admin, to export them as `.po` files for a translation agency or for backup.

```bash
python manage.py dlk_makemessages
```

| Option | Default | Description |
|---|---|---|
| `--language` | all languages | Only generate the `.po` file for this language code |

Generate only the Spanish file:

```bash
python manage.py dlk_makemessages --language=es
```

**Generated file** — `dlk_locale/es/LC_MESSAGES/django.po`:

```po
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# LANGUAGE TEAM <EMAIL>
#
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#  article__title__42
msgid "Hello World"
msgstr "Hola Mundo"

#  article__body__42
#, fuzzy
msgid "A sample article."
msgstr ""

#  article__title__43
msgid "Quick Start Guide"
msgstr "Guía de Inicio Rápido"
```

!!! note
    Entries with an empty `msgstr` receive a `fuzzy` flag automatically, signalling to translators that the string is untranslated.

---

## dlk_update_database

Reads django-localekit `.po` files from `DLK_LOCALE_PATH` and imports each valid entry into the `Translation` table.

**When to use:** after a translator returns the completed `.po` files, to load the translations into the database.

```bash
python manage.py dlk_update_database
```

**Skip logic:**

- The default language (`LANGUAGE_CODE`) is always skipped — it is the source, not a translation.
- A language is skipped if its `.po` file does not exist yet.
- A language is skipped if its `.po` file is **older** than the most recent `Translation.updated_at` for that language, preventing accidental overwrites.

**Input file** — `dlk_locale/es/LC_MESSAGES/django.po`:

```po
#  article__title__42
msgid "Hello World"
msgstr "Hola Mundo"

#  article__body__42
msgid "A sample article."
msgstr "Un artículo de ejemplo."
```

After the command runs, two `Translation` rows exist for `article` pk=42 in Spanish.

---

## dlk_convert_locales

Converts a **standard Django `.po` file** (produced by `makemessages`) into django-localekit format by matching each `msgid` against translatable model instances in the database.

**When to use:** when you already have translated `.po` files from a regular Django gettext workflow and want to import them into the database-backed system.

```bash
python manage.py dlk_convert_locales --locale locale
```

| Option | Required | Description |
|---|---|---|
| `--locale` | Yes | Name of the folder under `BASE_DIR` containing the source `.po` files (e.g. `locale`) |
| `--remove-used` | No | Remove matched entries from the source `.po` file after they have been written to the output file |

**Input** — `locale/es/LC_MESSAGES/django.po`:

```po
msgid "Hello World"
msgstr "Hola Mundo"

msgid "A sample article."
msgstr "Un artículo de ejemplo."

msgid "This string has no matching model object."
msgstr "Esta cadena no tiene objeto de modelo coincidente."
```

**Output** — `dlk_locale/es/LC_MESSAGES/django.po`:

```po
#  article__title__42
msgid "Hello World"
msgstr "Hola Mundo"

#  article__body__42
msgid "A sample article."
msgstr "Un artículo de ejemplo."
```

Only entries whose `msgid` matches a value in a translatable model field are written to the output file. The unmatched entry (`"This string has no matching model object."`) is silently ignored.

With `--remove-used`, the two matched entries are also removed from the source `locale/es/LC_MESSAGES/django.po`, leaving only the unmatched one.

---

## dlk_translate_models

Automatically translates empty translation fields (or all fields with `--all`) using a configured translation provider.

**When to use:** to populate translations in bulk without a human translator, using machine translation or an AI language model.

```bash
python manage.py dlk_translate_models --language=es --provider=google_v3
```

| Option | Default | Description |
|---|---|---|
| `--language` | required | Target language code (e.g. `es`, `fr`) |
| `--provider` | required | Provider name (e.g. `google_v2`, `google_v3`, `aws`, `deepl`, or a custom name) |
| `--target_language` | same as `--language` | Provider-side language code when it differs from `LANGUAGES` (e.g. `pt-BR` vs `pt`) |
| `--all` | `false` | Translate even fields that already have a translation |
| `--workers` | `4` | Number of parallel worker threads |
| `--without_batch` | `false` | Send one string per request instead of batching |

**Translate only empty fields to Spanish:**

```bash
python manage.py dlk_translate_models --language=es --provider=google_v3
```

**Re-translate everything to French (overwrite):**

```bash
python manage.py dlk_translate_models --language=fr --provider=deepl --all
```

**Use a provider whose internal language code differs (e.g. Brazilian Portuguese):**

```bash
python manage.py dlk_translate_models --language=pt --target_language=pt-BR --provider=deepl
```

See [Translation Providers](providers.md) for how to configure built-in providers and how to write a custom one.
