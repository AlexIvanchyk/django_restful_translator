from abc import ABC, abstractmethod
from typing import (
    Iterable,
    Union,
)

import boto3
import deepl
from django.conf import settings
from google.cloud import translate_v2, translate


class TranslationProvider(ABC):
    name = "Base Provider"
    batch_size = 1

    @abstractmethod
    def translate_text(self, text: Union[str, Iterable[str]], source_language: str, target_language: str) -> Union[
        str, Iterable[str]]:
        pass


class GoogleTranslateProvider(TranslationProvider):
    name = "google_v2"
    batch_size = 1

    def __init__(self):
        self.client = translate_v2.Client()

    def translate_text(self, text, source_language, target_language):
        result = self.client.translate(text, source_language=source_language, target_language=target_language)
        return result['translatedText']


class AWSTranslateProvider(TranslationProvider):
    name = "aws"
    batch_size = 1

    def __init__(self):
        if not (hasattr(settings, 'AWS_ACCESS_KEY_ID') and hasattr(settings, 'AWS_SECRET_ACCESS_KEY') and hasattr(
                settings, 'AWS_REGION_NAME')):
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_REGION_NAME must be set in settings")
        self.client = boto3.client('translate', region_name=settings.AWS_REGION_NAME,
                                   aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    def translate_text(self, text, source_language, target_language):
        response = self.client.translate_text(Text=text, SourceLanguageCode=source_language,
                                              TargetLanguageCode=target_language)
        return response['TranslatedText']


class GoogleV3TranslateProvider(TranslationProvider):
    name = "google_v3"
    batch_size = 50

    def __init__(self):
        if not hasattr(settings, 'GOOGLE_CLOUD_PROJECT'):
            raise ValueError("GOOGLE_CLOUD_PROJECT must be set in settings")
        if not hasattr(settings, 'GOOGLE_CLOUD_LOCATION'):
            raise ValueError("GOOGLE_CLOUD_LOCATION must be set in settings")
        self.client = translate.TranslationServiceClient()

    def translate_text(self, text, source_language, target_language):
        parent = f"projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.GOOGLE_CLOUD_LOCATION}"
        if isinstance(text, list):
            results = self.client.translate_text(parent=parent, contents=text, source_language_code=source_language,
                                                 target_language_code=target_language)
            return [result.translated_text for result in results.translations]
        else:
            results = self.client.translate_text(parent=parent, contents=[text], source_language_code=source_language,
                                                 target_language_code=target_language)

            return results.translations[0].translated_text


class DeeplTranslateProvider(TranslationProvider):
    name = "deepl"
    batch_size = 50

    def __init__(self):
        if not hasattr(settings, 'DEEPL_AUTH_KEY'):
            raise ValueError("DEEPL_AUTH_KEY must be set in settings")
        self.client = deepl.Translator(settings.DEEPL_AUTH_KEY)

    def translate_text(self, text, source_language, target_language):
        results = self.client.translate_text(text, source_lang=source_language, target_lang=target_language)
        if isinstance(text, list):
            return [result.text for result in results]
        else:
            return results.text
