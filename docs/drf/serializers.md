# Serializers

All serializers extend `BaseTranslatableSerializer`, which itself extends DRF's `ModelSerializer`. They override `to_representation` to replace translatable field values with their translated equivalents before the response is returned.

## Choosing a serializer

| Serializer | Field output | Writable |
|---|---|---|
| `TranslatableDBSerializer` | Single string (active language) | No |
| `TranslatableDBDictSerializer` | `{"en": "...", "es": "..."}` dict | No |
| `TranslatableWritableDBDictSerializer` | `{"en": "...", "es": "..."}` dict | Yes |
| `TranslatableGettextSerializer` | Single string via gettext | No |
| `TranslatableGettextDictSerializer` | Dict via gettext for all languages | No |

---

## TranslatableDBSerializer

Returns the translation for the **active request language** as a plain string, falling back to the original field value when no translation exists.

```python
from django_localekit.drf.serializers import TranslatableDBSerializer

class ArticleSerializer(TranslatableDBSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

**Response (Accept-Language: es):**

```json
{
  "id": 1,
  "title": "Hola Mundo",
  "body": "Un artículo de ejemplo."
}
```

---

## TranslatableDBDictSerializer

Returns **all available translations** as a dictionary keyed by language code. The original language value is always included under `LANGUAGE_CODE`.

```python
from django_localekit.drf.serializers import TranslatableDBDictSerializer

class ArticleSerializer(TranslatableDBDictSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

**Response:**

```json
{
  "id": 1,
  "title": {"en": "Hello World", "es": "Hola Mundo", "fr": "Bonjour le Monde"},
  "body": {"en": "A sample article.", "es": "Un artículo de ejemplo."}
}
```

---

## TranslatableWritableDBDictSerializer

Same read output as `TranslatableDBDictSerializer`, but also **accepts dict input on create and update**. The primary-language value is saved to the model field; all other language values are saved as `Translation` rows.

```python
from django_localekit.drf.serializers import TranslatableWritableDBDictSerializer

class ArticleSerializer(TranslatableWritableDBDictSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

**POST / PUT request body:**

```json
{
  "title": {"en": "Hello World", "es": "Hola Mundo"},
  "body": {"en": "A sample article.", "es": "Un artículo de ejemplo."}
}
```

The `"en"` values are written to the model; the `"es"` values are stored as translations.

!!! note
    If a field receives a plain string instead of a dict, it is saved as-is (no translations are created for that field).

---

## TranslatableGettextSerializer

Returns a single string translated via Django's standard `gettext` mechanism. Use this when your translations live in `.po`/`.mo` files (managed by `makemessages` / `compilemessages`) rather than in the database.

```python
from django_localekit.drf.serializers import TranslatableGettextSerializer

class ArticleSerializer(TranslatableGettextSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

The active language is determined by the request (via `LocaleMiddleware`).

---

## TranslatableGettextDictSerializer

Returns a dict of gettext translations for **all configured languages**. Only languages where the translation differs from the source string are included.

```python
from django_localekit.drf.serializers import TranslatableGettextDictSerializer

class ArticleSerializer(TranslatableGettextDictSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

**Response:**

```json
{
  "id": 1,
  "title": {"en": "Hello World", "es": "Hola Mundo"}
}
```

---

## Restricting translatable fields

By default, all fields listed in `Model.translatable_fields` are translated. Override this in the serializer's `Meta`:

```python
class ArticleSerializer(TranslatableDBSerializer):
    class Meta:
        model = Article
        fields = "__all__"
        translatable_fields = ["title"]  # only translate title, leave body as-is
```

Pass `"__all__"` (string) to explicitly use all of the model's translatable fields:

```python
        translatable_fields = "__all__"
```
