# Django REST Framework integration

django-localekit supports optional integration with Django REST Framework. If you expose translatable models via DRF APIs, you can use the provided serializers and fields so that responses automatically serve translated content based on the request language.

- **[Serializers](serializers.md)** — choose and customise the right serializer for your API (DB-backed, gettext, writable dict, etc.).

No DRF-specific configuration is required beyond adding the serializers to your views. The package works fully without DRF; use this section only if you need API support.
