from abc import ABC, abstractmethod

import boto3
import deepl
from django.conf import settings
from google.cloud import translate_v2


class TranslationProvider(ABC):
    name = "Base Provider"

    @abstractmethod
    def translate_text(self, text: str, source_language: str, target_language: str) -> str:
        pass


class GoogleTranslateProvider(TranslationProvider):
    name = "google_v2"

    def __init__(self):
        self.client = translate_v2.Client()

    def translate_text(self, text, source_language, target_language):
        result = self.client.translate(text, source_language=source_language, target_language=target_language)
        return result['translatedText']


class AWSTranslateProvider(TranslationProvider):
    name = "aws"

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


class DeeplTranslateProvider(TranslationProvider):
    name = "deepl"

    def __init__(self):
        if not hasattr(settings, 'DEEPL_AUTH_KEY'):
            raise ValueError("DEEPL_AUTH_KEY must be set in settings")
        self.client = deepl.Translator(settings.DEEPL_AUTH_KEY)

    def translate_text(self, text, source_language, target_language):
        result = self.client.translate_text(text, source_lang=source_language, target_lang=target_language)
        return result.text
