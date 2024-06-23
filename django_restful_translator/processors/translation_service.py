import html
import re
from typing import Iterable, Sequence

from django.conf import settings

from django_restful_translator.models import Translation
from django_restful_translator.translation_providers import TranslationProvider


class TranslationService:
    def __init__(self, provider: TranslationProvider, target_language: str):
        self.provider = provider
        self.target_language = target_language

    def translate_item(self, translation: Translation) -> Translation:
        original_text = translation.get_original_text()
        text_with_tokens, tokens = self._replace_placeholders_with_tokens(original_text)
        translated_text = self.provider.translate_text(text_with_tokens, settings.LANGUAGE_CODE, self.target_language)
        translated_text = self._replace_tokens_with_placeholders(translated_text, tokens)
        decoded_text = html.unescape(translated_text)
        translation.field_value = decoded_text
        translation.save()
        print(f'Translated {translation.content_object._meta.model_name} '
              f'field {translation.field_name} to {self.target_language}')
        return translation

    def translate_batch(self, translations: Iterable[Translation]) -> Iterable[Translation]:
        content_to_translate = []
        original_translations = []
        tokens_list = []
        for translation in translations:
            original_text = translation.get_original_text()
            text_with_tokens, tokens = self._replace_placeholders_with_tokens(original_text)
            content_to_translate.append(text_with_tokens)
            tokens_list.append(tokens)
            original_translations.append(translation)

        translated_texts = self.provider.translate_text(content_to_translate, settings.LANGUAGE_CODE,
                                                        self.target_language)

        for translation, tokens, translated_text in zip(original_translations, tokens_list, translated_texts):
            translated_text_with_placeholders = self._replace_tokens_with_placeholders(translated_text, tokens)
            translation.field_value = html.unescape(translated_text_with_placeholders)
            translation.save()
            print(f'Translated {translation.content_object._meta.model_name} '
                  f'field {translation.field_name} to {self.target_language}')
        return original_translations

    @staticmethod
    def get_batches(items: Sequence, batch_size: int) -> Iterable[Sequence]:
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    @staticmethod
    def _replace_placeholders_with_tokens(text: str) -> tuple:
        placeholders = re.findall(r'\{.*?\}', text)
        tokens = {}
        counter = 1
        for placeholder in placeholders:
            token = f"__TOKEN{counter}__"
            counter += 1
            tokens[token] = placeholder
            text = text.replace(placeholder, token)
        return text, tokens

    @staticmethod
    def _replace_tokens_with_placeholders(text: str, tokens: dict) -> str:
        for token, placeholder in tokens.items():
            text = text.replace(token, placeholder)
        return text
