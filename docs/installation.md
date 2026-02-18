# Installation

## Requirements

- Python 3.9+
- Django 4.2+
- Django REST Framework 3.15+ (optional; only if you use the DRF serializers)

## Install the package

Install the base package (no cloud SDK dependencies):

```bash
pip install django-localekit
```

Or with a specific translation provider:

```bash
pip install "django-localekit[google_v2]"   # Google Translate v2
pip install "django-localekit[google_v3]"   # Google Translate v3
pip install "django-localekit[aws]"          # AWS Translate
pip install "django-localekit[deepl]"        # DeepL
pip install "django-localekit[all]"          # all built-in providers
```

With Poetry:

```bash
poetry add django-localekit
poetry add "django-localekit[deepl]"  # with DeepL extra
```

!!! note
    If you only use custom or AI-based providers (OpenAI, Ollama, etc.), installing the base package without any extras is sufficient.

## Configure Django

### Installed apps

Add `django_localekit` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_localekit",
    ...
]
```

### Middleware

Add `LocaleMiddleware` so Django sets the active language from the request:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # must come after SessionMiddleware
    "django.middleware.common.CommonMiddleware",
    ...
]
```

### Languages and locale paths

Define the languages your project supports and include both the standard locale directory and the Locale Kit locale directory:

```python
LANGUAGES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
]

LANGUAGE_CODE = "en"  # default / source language

LOCALE_PATHS = [
    BASE_DIR / "locale",      # standard Django translations
    BASE_DIR / "dlk_locale",  # django-localekit .po files
]
```

### Optional: custom locale path

By default, django-localekit stores its `.po` files under `BASE_DIR / "dlk_locale"`. Override this with an absolute path:

```python
DLK_LOCALE_PATH = BASE_DIR / "translations"
```

This setting is used by `dlk_makemessages`, `dlk_update_database`, and `dlk_convert_locales`.

### Optional: auto-create translations on model save

Set `DLK_AUTO_CREATE_TRANSLATIONS = True` to automatically create empty `Translation` rows for all non-default languages whenever a new `TranslatableModel` instance is saved:

```python
DLK_AUTO_CREATE_TRANSLATIONS = True  # default: False
```

This removes the need to run `dlk_makemessages` before `dlk_translate_models` on fresh data. Rows are inserted with an empty `field_value` and can be filled later by a translator or the `dlk_translate_models` command.

## Run migrations

Create the `Translation` database table:

```bash
python manage.py migrate
```

If you are upgrading from django-restful-translator and the table already exists, run:

```bash
python manage.py migrate django_localekit --fake-initial
```
