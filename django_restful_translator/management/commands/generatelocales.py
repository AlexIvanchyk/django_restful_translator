import os

import polib
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from django_restful_translator.models import TranslatableModel, Translation


class Command(BaseCommand):
    help = 'Generate .po files from DB translations'

    def handle(self, *args, **options):
        # Get all the models in the project
        models = apps.get_models()
        # Filter out models that are instances of TranslatableModel
        translatable_models = [model for model in models if issubclass(model, TranslatableModel)]

        # Iterate over each language
        for language_set in settings.LANGUAGES:
            language = language_set[0]
            # Open or create the .po file for this language
            po_path = os.path.join(settings.SITE_ROOT, 'drt_locale', language, 'LC_MESSAGES')
            os.makedirs(po_path, exist_ok=True)
            po_file_path = os.path.join(po_path, 'django.po')
            if os.path.isfile(po_file_path):
                po = polib.pofile(po_file_path)
            else:
                po = polib.POFile()
            # Iterate over each translatable model
            for model in translatable_models:
                # Fetch objects with prefetched translations
                objects = model.objects.all().prefetch_related('translations')
                for obj in objects:
                    for field_name in model.translatable_fields:
                        original_field_value = getattr(obj, field_name)
                        if original_field_value is None or original_field_value == '':
                            self.stdout.write(
                                f'Skipping {model._meta.model_name} id {obj.id} due to None value for field {field_name}')
                            continue
                        trans = next((t for t in obj.translations.all() if
                                      t.field_name == field_name and t.language == language), None)
                        if not trans:
                            # If translation doesn't exist, create a blank one for the .po file
                            trans = Translation(
                                content_object=obj,
                                field_name=field_name,
                                language=language,
                                field_value=original_field_value if language == settings.LANGUAGE_CODE else ""
                            )
                        self.write_to_po_file(po, trans)
            # Save and close the .po file for this language
            po.save(po_file_path)

    def write_to_po_file(self, po, trans):
        entry = polib.POEntry(
            msgid=getattr(trans.content_object, trans.field_name),
            msgstr=trans.field_value,
            tcomment=f"{trans.content_object._meta.model_name}__{trans.field_name}__{trans.object_id}"
        )
        if not trans.field_value:
            entry.flags.append('fuzzy')
        po.append(entry)
