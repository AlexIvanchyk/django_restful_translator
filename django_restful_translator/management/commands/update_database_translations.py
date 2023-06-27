import os
import polib
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from django_restful_translator.models import TranslatableModel, Translation


class Command(BaseCommand):
    help = 'Import .po files to DB translations'

    def handle(self, *args, **options):
        # Get all the models in the project
        models = apps.get_models()
        # Filter out models that are instances of TranslatableModel
        translatable_models = [model for model in models if issubclass(model, TranslatableModel)]

        # Iterate over each language
        for language_set in settings.LANGUAGES:
            language = language_set[0]

            # Skip default language
            if language == settings.LANGUAGE_CODE:
                continue

            # Open the .po file for this language
            po_file_path = os.path.join(settings.SITE_ROOT, 'drt_locale', language, 'LC_MESSAGES', 'django.po')

            # Check the last modification time of the .po file
            if os.path.isfile(po_file_path):
                po_file_mod_time = os.path.getmtime(po_file_path)

                # Get the last update time of the Translation objects for the current language
                last_translation_update = Translation.objects.filter(language=language).latest(
                    'updated_at').updated_at.timestamp()

                # Only proceed if the .po file is newer than the last update in the database
                if po_file_mod_time <= last_translation_update:
                    continue

            if not os.path.isfile(po_file_path):
                continue

            po = polib.pofile(po_file_path)
            # Iterate over each entry in the .po file
            for entry in po:
                model_name, field_name, object_id = entry.tcomment.split("__")
                model = next((m for m in translatable_models if m._meta.model_name == model_name), None)
                if not model:
                    continue
                field_value = entry.msgstr
                if field_value == "":
                    continue
                # Fetch or create the Translation object
                trans, created = Translation.objects.get_or_create(
                    content_type=ContentType.objects.get_for_model(model),
                    object_id=object_id,
                    field_name=field_name,
                    language=language,
                    defaults={"field_value": field_value}
                )
                # If the Translation object already existed, update it
                if not created:
                    trans.field_value = entry.msgstr
                    trans.save()
