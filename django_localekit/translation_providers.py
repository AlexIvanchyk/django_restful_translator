from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Protocol, Union


class TranslationProviderProtocol(Protocol):
    name: str
    batch_size: int

    def translate_text(
        self, text: Union[str, Iterable[str]], source_language: str, target_language: str
    ) -> Union[str, list[str]]: ...


def _all_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _all_subclasses(sub)


class TranslationProviderFactory:
    @staticmethod
    def get_available_providers():
        return {cls.name: cls for cls in _all_subclasses(TranslationProvider)}

    @staticmethod
    def get_provider_names():
        return [cls.name for cls in _all_subclasses(TranslationProvider)]

    @staticmethod
    def get_provider(provider_name: str):
        available_providers = TranslationProviderFactory.get_available_providers()
        provider_class = available_providers.get(provider_name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")
        return provider_class()


class TranslationProvider(ABC):
    name = "Base Provider"
    batch_size = 1

    @abstractmethod
    def translate_text(
        self, text: Union[str, Iterable[str]], source_language: str, target_language: str
    ) -> Union[str, Iterable[str]]:
        pass


class GoogleTranslateProvider(TranslationProvider):
    name = "google_v2"
    batch_size = 1

    def __init__(self):
        try:
            from google.cloud import translate_v2
        except ImportError as e:
            raise ImportError(
                "google-cloud-translate is required for google_v2 provider. "
                "Install it with: pip install django-localekit[google_v2]"
            ) from e
        self.client = translate_v2.Client()

    def translate_text(self, text, source_language, target_language) -> str:
        result = self.client.translate(text, source_language=source_language, target_language=target_language)
        if isinstance(result, list):
            return result[0]["translatedText"] if result else ""
        return result["translatedText"]


class AWSTranslateProvider(TranslationProvider):
    name = "aws"
    batch_size = 1

    def __init__(self):
        try:
            import boto3
        except ImportError as e:
            raise ImportError(
                "boto3 is required for the aws provider. " "Install it with: pip install django-localekit[aws]"
            ) from e
        from django.conf import settings

        if not (
            hasattr(settings, "AWS_ACCESS_KEY_ID")
            and hasattr(settings, "AWS_SECRET_ACCESS_KEY")
            and hasattr(settings, "AWS_REGION_NAME")
        ):
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION_NAME must be set in settings")
        self.client = boto3.client(
            "translate",
            region_name=settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def translate_text(self, text, source_language, target_language) -> str:
        response = self.client.translate_text(
            Text=text, SourceLanguageCode=source_language, TargetLanguageCode=target_language
        )
        return response["TranslatedText"]


class GoogleV3TranslateProvider(TranslationProvider):
    name = "google_v3"
    batch_size = 50

    def __init__(self):
        try:
            from google.cloud import translate
        except ImportError as e:
            raise ImportError(
                "google-cloud-translate is required for google_v3 provider. "
                "Install it with: pip install django-localekit[google_v3]"
            ) from e
        from django.conf import settings

        if not hasattr(settings, "GOOGLE_CLOUD_PROJECT"):
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set in settings")
        if not hasattr(settings, "GOOGLE_CLOUD_LOCATION"):
            raise ValueError("GOOGLE_CLOUD_LOCATION must be set in settings")
        self.client = translate.TranslationServiceClient()

    def translate_text(self, text, source_language, target_language) -> Union[str, list[str]]:
        from django.conf import settings

        parent = f"projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.GOOGLE_CLOUD_LOCATION}"
        if isinstance(text, list):
            results = self.client.translate_text(
                parent=parent, contents=text, source_language_code=source_language, target_language_code=target_language
            )
            return [result.translated_text for result in results.translations]
        results = self.client.translate_text(
            parent=parent, contents=[text], source_language_code=source_language, target_language_code=target_language
        )
        return results.translations[0].translated_text


class DeeplTranslateProvider(TranslationProvider):
    name = "deepl"
    batch_size = 50

    def __init__(self):
        try:
            import deepl as deepl_lib
        except ImportError as e:
            raise ImportError(
                "deepl is required for the deepl provider. " "Install it with: pip install django-localekit[deepl]"
            ) from e
        from django.conf import settings

        if not hasattr(settings, "DEEPL_AUTH_KEY"):
            raise ValueError("DEEPL_AUTH_KEY must be set in settings")
        self.client = deepl_lib.Translator(settings.DEEPL_AUTH_KEY)

    def translate_text(self, text, source_language, target_language) -> Union[str, list[str]]:
        results = self.client.translate_text(text, source_lang=source_language, target_lang=target_language)
        if isinstance(text, list):
            return [result.text for result in results]
        return results.text
