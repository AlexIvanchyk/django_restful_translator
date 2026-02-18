from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_localekit.models import TranslatableModel, Translation


@receiver(post_save)
def auto_create_translations(sender, instance, created, **kwargs):
    if not created:
        return
    if not issubclass(sender, TranslatableModel):
        return
    if not getattr(settings, "DLK_AUTO_CREATE_TRANSLATIONS", False):
        return

    from django.contrib.contenttypes.models import ContentType

    content_type = ContentType.objects.get_for_model(instance)
    non_default_languages = [lang for lang, _ in settings.LANGUAGES if lang != settings.LANGUAGE_CODE]

    new_translations = []
    for language in non_default_languages:
        for field_name in instance.translatable_fields:
            new_translations.append(
                Translation(
                    content_type=content_type,
                    object_id=str(instance.pk),
                    language=language,
                    field_name=field_name,
                    field_value="",
                )
            )

    if new_translations:
        Translation.objects.bulk_create(new_translations, ignore_conflicts=True)
