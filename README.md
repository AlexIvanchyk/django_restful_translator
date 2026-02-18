# django-localekit

[![CI](https://github.com/AlexIvanchyk/django-localekit/actions/workflows/ci.yml/badge.svg)](https://github.com/AlexIvanchyk/django-localekit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-localekit)](https://pypi.org/project/django-localekit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://choosealicense.com/licenses/mit/)

A Django library that adds database-backed model translations with optional Django REST Framework integration. Translations are stored in a separate table — original field values are never modified.

## Features

- `TranslatableModel` mixin — declare which fields are translatable in one line
- Five DRF serializers covering all read/write translation patterns (optional)
- `TranslationInline` for managing translations in the Django admin
- Management commands to export/import `.po` files and run automatic machine translation
- Built-in providers: Google Translate v2/v3, AWS Translate, DeepL
- Extensible provider system — plug in any API or local LLM (OpenAI, Ollama, etc.)

## Quick start

```bash
pip install django-localekit          # base (no cloud SDKs)
pip install "django-localekit[deepl]" # with DeepL provider
pip install "django-localekit[all]"   # all built-in providers
python manage.py migrate
```

```python
# models.py
from django_localekit.models import TranslatableModel

class Article(TranslatableModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    translatable_fields = ["title", "body"]
```

```python
# serializers.py (optional DRF integration)
from django_localekit.drf.serializers import TranslatableDBSerializer

class ArticleSerializer(TranslatableDBSerializer):
    class Meta:
        model = Article
        fields = "__all__"
```

A `GET /articles/1/` request with `Accept-Language: es` returns the Spanish translation automatically.

## Documentation

Full documentation is available at **[https://alexivanchyk.github.io/django-localekit/](https://alexivanchyk.github.io/django-localekit/)**

- [Installation](https://alexivanchyk.github.io/django-localekit/installation/)
- [Usage](https://alexivanchyk.github.io/django-localekit/usage/)
- [Serializers](https://alexivanchyk.github.io/django-localekit/drf/serializers/)
- [Commands](https://alexivanchyk.github.io/django-localekit/commands/)
- [Translation Providers](https://alexivanchyk.github.io/django-localekit/providers/)
- [Development](https://alexivanchyk.github.io/django-localekit/development/)

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

## License

[MIT](https://choosealicense.com/licenses/mit/)
