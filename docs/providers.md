# Translation Providers

## Built-in providers

Each built-in provider requires its own optional dependency. Install only what you need:

| Provider | Extra | Install command |
|---|---|---|
| `google_v2` | `google_v2` | `pip install "django-localekit[google_v2]"` |
| `google_v3` | `google_v3` | `pip install "django-localekit[google_v3]"` |
| `aws` | `aws` | `pip install "django-localekit[aws]"` |
| `deepl` | `deepl` | `pip install "django-localekit[deepl]"` |

---

### google_v2

Uses the [Google Cloud Translation API (v2 / Basic)](https://cloud.google.com/translate/docs/basic/translating-text).

**Install:**

```bash
pip install "django-localekit[google_v2]"
```

**Setup:**

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your service account JSON key:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

**Usage:**

```bash
python manage.py dlk_translate_models --language=es --provider=google_v2
```

---

### google_v3

Uses the [Google Cloud Translation API (v3 / Advanced)](https://cloud.google.com/translate/docs/advanced/translating-text-v3). Supports glossaries and AutoML models.

**Install:**

```bash
pip install "django-localekit[google_v3]"
```

**Setup:**

```python
# settings.py
GOOGLE_CLOUD_PROJECT = "my-gcp-project-id"
GOOGLE_CLOUD_LOCATION = "global"
```

**Usage:**

```bash
python manage.py dlk_translate_models --language=es --provider=google_v3
```

---

### aws

Uses [Amazon Translate](https://docs.aws.amazon.com/translate/).

**Install:**

```bash
pip install "django-localekit[aws]"
```

**Setup:**

```python
# settings.py
AWS_ACCESS_KEY_ID = "AKIA..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_REGION_NAME = "us-east-1"
```

**Usage:**

```bash
python manage.py dlk_translate_models --language=es --provider=aws
```

---

### deepl

Uses the [DeepL API](https://www.deepl.com/docs-api).

**Install:**

```bash
pip install "django-localekit[deepl]"
```

**Setup:**

```python
# settings.py
DEEPL_AUTH_KEY = "your-deepl-auth-key"
```

**Usage:**

```bash
python manage.py dlk_translate_models --language=fr --provider=deepl
```

---

## Custom providers

Any class that subclasses `TranslationProvider` is **automatically discovered** by `TranslationProviderFactory` at runtime — no registration step is needed.

### Interface

```python
from abc import ABC, abstractmethod

class TranslationProvider(ABC):
    name: str       # the value passed to --provider
    batch_size: int # how many strings are sent in one API call (1 = one at a time)

    @abstractmethod
    def translate_text(
        self,
        text: str | list[str],
        source_language: str,
        target_language: str,
    ) -> str | list[str]:
        ...
```

- When `batch_size > 1`, `text` is a `list[str]` and the method must return a `list[str]` of the same length.
- When `batch_size == 1` (or `--without_batch` is used), `text` is a plain `str` and the method must return a `str`.

---

## Example: OpenAI GPT provider

AI language models like GPT-4o are an excellent fit for translation tasks — they produce natural, context-aware output and can be guided with domain-specific instructions via the system prompt.

### Implementation

```python
# myapp/providers.py
from openai import OpenAI
from django_localekit.translation_providers import TranslationProvider


class OpenAITranslationProvider(TranslationProvider):
    name = "openai"
    batch_size = 1  # LLMs work best one string at a time

    def __init__(self):
        self.client = OpenAI()  # reads OPENAI_API_KEY from env

    def translate_text(self, text, source_language, target_language):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional translator. "
                        f"Translate from {source_language} to {target_language}. "
                        f"Return only the translated text, no explanations."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
```

### Registration

The provider class must be imported before `TranslationProviderFactory` is used. The cleanest place is the `ready()` method of your app config:

```python
# myapp/apps.py
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = "myapp"

    def ready(self):
        import myapp.providers  # noqa: F401
```

### Usage

```bash
python manage.py dlk_translate_models --language=es --provider=openai
```

### Tips for AI providers

- **Prompt engineering** — customise the system message with domain-specific instructions (e.g. "Use formal Spanish", "Preserve HTML tags", "Use the following glossary: ...") to improve consistency.
- **Batch size** — keep `batch_size = 1` for most LLM providers. You can increase it only if you construct your prompt to send multiple strings at once and reliably parse the response back into a list.
- **`--without_batch` flag** — forces single-string mode regardless of the provider's `batch_size`. Useful for debugging.
- **Costs** — LLMs charge per token. Use `--all False` (the default) to only translate fields that are currently empty, avoiding re-translation of content that is already done.
- **Rate limits** — lower `--workers` (e.g. `--workers 2`) to stay within API rate limits for providers that enforce them.

---

## Example: local LLM provider (Ollama)

You are not limited to cloud APIs. Any locally-running LLM that exposes an OpenAI-compatible HTTP endpoint — such as [Ollama](https://ollama.com/) — works exactly the same way. This keeps all data on-premises and has no per-token cost.

Start a local model (e.g. `llama3`):

```bash
ollama pull llama3
ollama serve
```

Implement the provider, pointing the OpenAI client at the local endpoint:

```python
# myapp/providers.py
from openai import OpenAI
from django_localekit.translation_providers import TranslationProvider


class OllamaTranslationProvider(TranslationProvider):
    name = "ollama"
    batch_size = 1

    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # required by the client but not validated by Ollama
        )

    def translate_text(self, text, source_language, target_language):
        response = self.client.chat.completions.create(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional translator. "
                        f"Translate from {source_language} to {target_language}. "
                        f"Return only the translated text, no explanations."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
```

Register it in `apps.py` the same way as any other custom provider, then run:

```bash
python manage.py dlk_translate_models --language=es --provider=ollama
```

!!! tip
    Any model available in Ollama works — swap `"llama3"` for `"mistral"`, `"gemma3"`, `"qwen2.5"`, etc. Models with stronger multilingual training generally produce better translations. Use `--workers 1` for slower hardware to avoid overloading the local inference server.

### Example with a custom system prompt

```python
class OpenAITranslationProvider(TranslationProvider):
    name = "openai"
    batch_size = 1

    SYSTEM_PROMPT = (
        "You are a professional translator specialising in e-commerce product descriptions. "
        "Translate from {source} to {target}. "
        "Preserve any HTML tags exactly. "
        "Return only the translated text."
    )

    def __init__(self):
        self.client = OpenAI()

    def translate_text(self, text, source_language, target_language):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT.format(
                        source=source_language,
                        target=target_language,
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
```
