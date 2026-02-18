default_app_config = "django_localekit.apps.DjangoLocaleKitConfig"

__all__ = [
    "AutoTranslatableJsonField",
    "BaseTranslatableSerializer",
    "DeeplTranslateProvider",
    "GetTextCharField",
    "GetTextListField",
    "GoogleTranslateProvider",
    "GoogleV3TranslateProvider",
    "AWSTranslateProvider",
    "Translation",
    "TranslationInline",
    "TranslationProvider",
    "TranslationProviderFactory",
    "TranslatableModel",
    "TranslatableDBDictSerializer",
    "TranslatableDBSerializer",
    "TranslatableGettextDictSerializer",
    "TranslatableGettextSerializer",
    "TranslatableWritableDBDictSerializer",
    "get_translation",
]

_public: dict[str, object] = {}

_MODULE_GROUPS = {
    "TranslationInline": ("django_localekit.admin", ["TranslationInline"]),
    "AutoTranslatableJsonField": (
        "django_localekit.drf.fields",
        ["AutoTranslatableJsonField", "GetTextCharField", "GetTextListField"],
    ),
    "GetTextCharField": (
        "django_localekit.drf.fields",
        ["AutoTranslatableJsonField", "GetTextCharField", "GetTextListField"],
    ),
    "GetTextListField": (
        "django_localekit.drf.fields",
        ["AutoTranslatableJsonField", "GetTextCharField", "GetTextListField"],
    ),
    "BaseTranslatableSerializer": (
        "django_localekit.drf.serializers",
        [
            "BaseTranslatableSerializer",
            "TranslatableDBDictSerializer",
            "TranslatableDBSerializer",
            "TranslatableGettextDictSerializer",
            "TranslatableGettextSerializer",
            "TranslatableWritableDBDictSerializer",
        ],
    ),
    "TranslatableDBDictSerializer": (
        "django_localekit.drf.serializers",
        [
            "BaseTranslatableSerializer",
            "TranslatableDBDictSerializer",
            "TranslatableDBSerializer",
            "TranslatableGettextDictSerializer",
            "TranslatableGettextSerializer",
            "TranslatableWritableDBDictSerializer",
        ],
    ),
    "TranslatableDBSerializer": (
        "django_localekit.drf.serializers",
        [
            "BaseTranslatableSerializer",
            "TranslatableDBDictSerializer",
            "TranslatableDBSerializer",
            "TranslatableGettextDictSerializer",
            "TranslatableGettextSerializer",
            "TranslatableWritableDBDictSerializer",
        ],
    ),
    "TranslatableGettextDictSerializer": (
        "django_localekit.drf.serializers",
        [
            "BaseTranslatableSerializer",
            "TranslatableDBDictSerializer",
            "TranslatableDBSerializer",
            "TranslatableGettextDictSerializer",
            "TranslatableGettextSerializer",
            "TranslatableWritableDBDictSerializer",
        ],
    ),
    "TranslatableGettextSerializer": (
        "django_localekit.drf.serializers",
        [
            "BaseTranslatableSerializer",
            "TranslatableDBDictSerializer",
            "TranslatableDBSerializer",
            "TranslatableGettextDictSerializer",
            "TranslatableGettextSerializer",
            "TranslatableWritableDBDictSerializer",
        ],
    ),
    "TranslatableWritableDBDictSerializer": (
        "django_localekit.drf.serializers",
        [
            "BaseTranslatableSerializer",
            "TranslatableDBDictSerializer",
            "TranslatableDBSerializer",
            "TranslatableGettextDictSerializer",
            "TranslatableGettextSerializer",
            "TranslatableWritableDBDictSerializer",
        ],
    ),
    "Translation": (
        "django_localekit.models",
        ["Translation", "TranslatableModel"],
    ),
    "TranslatableModel": (
        "django_localekit.models",
        ["Translation", "TranslatableModel"],
    ),
    "AWSTranslateProvider": (
        "django_localekit.translation_providers",
        [
            "AWSTranslateProvider",
            "DeeplTranslateProvider",
            "GoogleTranslateProvider",
            "GoogleV3TranslateProvider",
            "TranslationProvider",
            "TranslationProviderFactory",
        ],
    ),
    "DeeplTranslateProvider": (
        "django_localekit.translation_providers",
        [
            "AWSTranslateProvider",
            "DeeplTranslateProvider",
            "GoogleTranslateProvider",
            "GoogleV3TranslateProvider",
            "TranslationProvider",
            "TranslationProviderFactory",
        ],
    ),
    "GoogleTranslateProvider": (
        "django_localekit.translation_providers",
        [
            "AWSTranslateProvider",
            "DeeplTranslateProvider",
            "GoogleTranslateProvider",
            "GoogleV3TranslateProvider",
            "TranslationProvider",
            "TranslationProviderFactory",
        ],
    ),
    "GoogleV3TranslateProvider": (
        "django_localekit.translation_providers",
        [
            "AWSTranslateProvider",
            "DeeplTranslateProvider",
            "GoogleTranslateProvider",
            "GoogleV3TranslateProvider",
            "TranslationProvider",
            "TranslationProviderFactory",
        ],
    ),
    "TranslationProvider": (
        "django_localekit.translation_providers",
        [
            "AWSTranslateProvider",
            "DeeplTranslateProvider",
            "GoogleTranslateProvider",
            "GoogleV3TranslateProvider",
            "TranslationProvider",
            "TranslationProviderFactory",
        ],
    ),
    "TranslationProviderFactory": (
        "django_localekit.translation_providers",
        [
            "AWSTranslateProvider",
            "DeeplTranslateProvider",
            "GoogleTranslateProvider",
            "GoogleV3TranslateProvider",
            "TranslationProvider",
            "TranslationProviderFactory",
        ],
    ),
}


def __getattr__(name: str) -> object:
    if name in _public:
        return _public[name]
    if name == "get_translation":
        from django_localekit.utils import get_translation

        _public[name] = get_translation
        return get_translation
    group = _MODULE_GROUPS.get(name)
    if group:
        module_path, names = group
        import importlib

        mod = importlib.import_module(module_path)
        for n in names:
            _public.setdefault(n, getattr(mod, n))
        return _public[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
