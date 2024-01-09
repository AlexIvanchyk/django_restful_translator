# django_restful_translator

`django_restful_translator` is a Django library for managing and serving translations of Django models while keeping the original values untouched. This package is designed to integrate seamlessly with Django REST framework.

## Functionality

`django_restful_translator` provides:

- **Model translations**: The `TranslatableModel` mixin adds translation capabilities to your models, allowing you to specify which fields should be translatable, while leaving the original field values intact.

- **Translation management**: Admin inlines for managing translations from the Django Admin site.

- **REST API support**: Provided serializers (`TranslatableDBSerializer`, `TranslatableDBDictSerializer`, `TranslatableGettextSerializer`, `TranslatableGettextDictSerializer`) ensure translated fields are properly serialized in API responses.

- **Translation synchronization**: Commands `generate_locales` and `update_database_translations` export translations to `.po` files and import them back into the database, keeping translations synchronized across different environments.

- **Automatic Translation**: The library supports automatic translation of model fields through popular translation providers like Google Translate and AWS Translate. The feature is configurable and can be run via an admin command.

## Advantages

- **Preserves original values**: `django_restful_translator` stores all translations in a separate model, ensuring that your original model's values remain unchanged.

- **Ease of use**: It integrates seamlessly with the Django Admin interface for easy management of translations.

- **Flexibility**: The `TranslatableModel` mixin can be added to any Django model with specified fields to translate.

- **Efficiency**: By storing translations in the database and only translating fields when necessary, `django_restful_translator` minimizes unnecessary work.

- **Integration with Django REST framework**: If you're using Django REST framework, `django_restful_translator` is designed to work with it out of the box.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install django_restful_translator.

```bash
pip install django-restful-translator
```

## Configuration

In your settings file, add the middleware for handling language preferences:

```python
MIDDLEWARE = [
    ...
    'django.middleware.locale.LocaleMiddleware',
    ...
]
```

In your settings file, add `django_restful_translator` to instaled apps:
```python
INSTALLED_APPS = [
    ...
    'django_restful_translator',
    ...
]
```

Set up your languages and locale paths. Make sure to include both the standard locale directory and the one for django_restful_translator:

```python
LOCALE_PATHS = (
    BASE_DIR / "locale",
    BASE_DIR / "drt_locale",
)

LANGUAGES = (
    ("en", "English"),
    ("sv", "Swedish"),
)

LANGUAGE_CODE = "en"
```
## Migrations
After setting up, you need to create the necessary database tables. You can do this by running migrations:
```bash
python manage.py migrate
```

## Usage

1. Import the `TranslatableModel` in your models.py and use it as a base class for any model you want to be translatable.

```python
from django_restful_translator.models import TranslatableModel

class YourModel(TranslatableModel):
    ...
```

2. Add your translatable fields to the `translatable_fields` attribute.

```python
class YourModel(TranslatableModel):
    title = models.CharField(max_length=100)
    description = models.TextField()

    translatable_fields = ['title', 'description']
```

3. Use the provided serializers in your API.

```python
from django_restful_translator.drf.serializers import TranslatableDBSerializer

class YourModelSerializer(TranslatableDBSerializer):
    ...
```
4. To enable managing translations in the Django admin, add `TranslationInline` to your model admin.
```python
from django_restful_translator.admin import TranslationInline

class YourModelAdmin(admin.ModelAdmin):
    inlines = [TranslationInline,]
```
5. When querying your translatable models, you can optimize your database queries by using `prefetch_related` to prefetch translations.
```python
YourModel.objects.all().prefetch_related('translations')
```
6. Run the provided management commands to generate `.po` files and update the database with translations.

```bash
python manage.py generate_locales
```
```bash
python manage.py update_database_translations
```
7. Converting Existing `.po` Files to DRT Format. 
Utilize the management command `convert_locales_to_drt_format` to transform existing `.po` files into a format suitable for use with the Django Restful Translator (DRT). The command accepts the following arguments:
- `--locale`: The directory where the existing `.po` files are located and will be read from. 
- `--remove-used`: When this option is used, the entries that are converted and added to the new `.po` file formatted for DRT will be removed from the original `.po` file, keeping it clean from already processed entries.


To convert `.po` files without modifying the original file:

```bash
python manage.py convert_locales_to_drt_format --locale locale
```
To remove entries in the original `.po` file that are used/converted in the new DRT format:
```bash
python manage.py convert_locales_to_drt_format --locale locale --remove-used
```

## Automatic Translation Feature Guide

### Overview

Our library provides an easy way to automatically translate fields in your Django models using popular translation providers such as Google Translate, AWS Translate and DeepL. This guide will help you configure and use this feature.

### Requirements

- Make sure the necessary credentials for your chosen translation provider are available in your Django settings file.

For Google Translate v2:

You can use the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to provide the location of a credential JSON file.
https://cloud.google.com/docs/authentication/application-default-credentials#GAC

For AWS Translate:

```python
# settings.py
AWS_ACCESS_KEY_ID = 'your aws access key here'
AWS_SECRET_ACCESS_KEY = 'your aws secret access key here'
AWS_REGION_NAME = 'your aws region name here'
```

For DeepL Translate:

```python
# settings.py
DEEPL_AUTH_KEY = 'your DeepL auth key here'
```

### Running the Admin Command

You can use the provided admin command to translate your model fields. The command accepts the following arguments:

- `--language`: The target language code to which you want to translate.
- `--provider`: The translation provider to use: `google_v2`, `aws`, `deepl`.
- `--all`: Use this flag if you want to overwrite existing translations.
- `--workers`: (Optional) Number of worker threads to use for concurrent processing. Default is 4.

**Run the admin command as follows:**

```bash
python manage.py translate_models --language=es --provider=google_v2
```

This will translate all translatable fields to Spanish using Google Translate.

**To overwrite existing translations:**

```bash
python manage.py translate_models --language=es --provider=google_v2 --all
```

### Verifying Translations

After running the command, your translated text should now be available and stored in your database. You can verify this through your Django admin panel or by querying the models directly.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
