# Usage

## 1. Make a model translatable

Inherit from `TranslatableModel` and declare which fields should be translated via `translatable_fields`:

```python
# models.py
from django.db import models
from django_localekit.models import TranslatableModel

class Article(TranslatableModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    published = models.BooleanField(default=False)

    translatable_fields = ["title", "body"]
    # `published` is not in the list — it is never translated
```

The original field values (`title`, `body`) are never changed. Translations are stored in a separate `Translation` table linked via a generic foreign key.

## 2. Manage translations in Django admin

Add `TranslationInline` to your model admin to let editors create and update translations directly in the admin interface:

```python
# admin.py
from django.contrib import admin
from django_localekit.admin import TranslationInline
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [TranslationInline]
```

The inline shows one row per `(language, field)` pair and prevents duplicates via form validation.

## 3. Optimise queries with prefetch_related

When displaying a list of translatable objects, always prefetch translations to avoid N+1 queries:

```python
# views.py
from .models import Article

articles = Article.objects.all().prefetch_related("translations")
```

This is especially important for DRF list views — all serializers in this package work correctly with prefetched translations. See [DRF → Serializers](drf/serializers.md).

## 4. Read a translation directly

Outside of a DRF serializer you can fetch the current-language translation for a single field using `get_translation`:

```python
from django_localekit.utils import get_translation

# Returns the Spanish title if the active language is "es",
# otherwise falls back to the original field value.
title = get_translation(article, "title")
```

Pass `as_dict=True` to get all available translations at once:

```python
translations = get_translation(article, "title", as_dict=True)
# {"es": "Hola Mundo", "fr": "Bonjour le Monde"}
```

!!! tip
    When calling `get_translation` in a loop (e.g. in a template tag), make sure the queryset was built with `prefetch_related("translations")` to keep the query count constant.

## 5. Auto-create empty translations on save (optional)

Enable `DLK_AUTO_CREATE_TRANSLATIONS = True` in your settings to have empty `Translation` rows created automatically for every non-default language whenever a new `TranslatableModel` instance is saved:

```python
# settings.py
DLK_AUTO_CREATE_TRANSLATIONS = True
```

This means you can immediately run `dlk_translate_models` on fresh data without needing to run `dlk_makemessages` first.

!!! note
    Auto-created rows have an empty `field_value`. They act as placeholders that `dlk_translate_models` will fill in, or that a human translator can edit via the admin.
