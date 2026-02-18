# django-localekit

**v1.0.0** · [PyPI](https://pypi.org/project/django-localekit/) · [GitHub](https://github.com/AlexIvanchyk/django-localekit)

django-localekit is a Django library that adds database-backed model translations. It works entirely through the database with an optional `.po` file workflow and optional automatic translation via external providers or AI. Optional Django REST Framework integration is available for serving translations in APIs.

## Key features

- **Non-destructive translations** — all translations are stored in a separate `Translation` model; your original field values are never modified.
- **DB-first workflow** — the system works entirely through the database. Translations can be created and managed via the Django admin without ever touching a file.
- **Admin support** — the `TranslationInline` class lets you manage translations directly in the Django admin.
- **Optional PO file workflow** — if you need to work with a translation agency or integrate with an existing gettext setup, `dlk_makemessages` and `dlk_update_database` export and import standard `.po` files. This is entirely optional.
- **Automatic translation** — the `dlk_translate_models` command translates all empty (or all) fields via a configurable provider: Google Translate v2/v3, AWS Translate, DeepL, or any custom provider including AI language models such as GPT-4o.
- **Extensible provider system** — implementing a custom translation provider requires only a single class with two attributes and one method.
- **DRF integration** — optional serializers serve translated content in APIs based on the active request language. See [DRF](drf/index.md).

## Quick example

```python
# models.py
from django_localekit.models import TranslatableModel

class Article(TranslatableModel):
    title = models.CharField(max_length=200)
    body = models.TextField()

    translatable_fields = ["title", "body"]
```

Use `get_translation(article, "title")` in views or templates, or add `TranslationInline` in the admin. For APIs, see [DRF → Serializers](drf/serializers.md).

```python
# serializers.py (optional)
from django_localekit.drf.serializers import TranslatableDBSerializer

class ArticleSerializer(TranslatableDBSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

A `GET /articles/1/` request with `Accept-Language: es` returns the Spanish translation automatically.

## Navigation

- [Installation](installation.md) — install and configure the package.
- [Usage](usage.md) — models, admin, and the utility function.
- [DRF](drf/index.md) — optional Django REST Framework integration (serializers).
- [Commands](commands.md) — management commands with example PO file output.
- [Translation Providers](providers.md) — built-in providers and writing your own (including AI models).
- [Development](development.md) — running the test suite and previewing these docs locally.
