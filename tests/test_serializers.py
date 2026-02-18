from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import override
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from django_localekit.drf.serializers import (
    TranslatableDBDictSerializer,
    TranslatableDBSerializer,
    TranslatableGettextDictSerializer,
    TranslatableGettextSerializer,
    TranslatableWritableDBDictSerializer,
)
from django_localekit.models import Translation
from tests.test_app.models import Book


class BookTranslatableDBSerializer(TranslatableDBSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "summary")


class BookTranslatableDBDictSerializer(TranslatableDBDictSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "summary")


class BookTranslatableWritableSerializer(TranslatableWritableDBDictSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "summary")


class BookGettextSerializer(TranslatableGettextSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "summary")


class BookGettextDictSerializer(TranslatableGettextDictSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "summary")


class GetTranslatableFieldsTest(TestCase):
    def test_from_model(self):
        class Serializer(BookTranslatableDBSerializer):
            class Meta(BookTranslatableDBSerializer.Meta):
                pass

        s = Serializer()
        self.assertEqual(set(s.get_translatable_fields()), {"title", "summary"})

    def test_meta_all(self):
        class Serializer(BookTranslatableDBSerializer):
            class Meta(BookTranslatableDBSerializer.Meta):
                translatable_fields = "__all__"

        s = Serializer()
        self.assertEqual(set(s.get_translatable_fields()), {"title", "summary"})

    def test_meta_subset(self):
        class Serializer(BookTranslatableDBSerializer):
            class Meta(BookTranslatableDBSerializer.Meta):
                translatable_fields = ["title"]

        s = Serializer()
        self.assertEqual(s.get_translatable_fields(), ["title"])


class TranslatableDBSerializerTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="World")
        ct = ContentType.objects.get_for_model(Book)
        Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )

    def test_representation_uses_current_language(self):
        with override("en"):
            s = BookTranslatableDBSerializer(self.book)
            self.assertEqual(s.data["title"], "Hello")
        with override("es"):
            s = BookTranslatableDBSerializer(self.book)
            self.assertEqual(s.data["title"], "Hola")


class TranslatableDBDictSerializerTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title="Hello", summary="World")
        ct = ContentType.objects.get_for_model(Book)
        Translation.objects.create(
            content_type=ct,
            object_id=str(self.book.pk),
            language="es",
            field_name="title",
            field_value="Hola",
        )

    def test_representation_is_dict(self):
        s = BookTranslatableDBDictSerializer(self.book)
        self.assertIsInstance(s.data["title"], dict)
        self.assertEqual(s.data["title"]["en"], "Hello")
        self.assertEqual(s.data["title"]["es"], "Hola")


class TranslatableWritableDBDictSerializerTest(TestCase):
    def test_create_stores_translations(self):
        factory = APIRequestFactory()
        request = factory.post("/", {}, format="json")
        request = Request(request)
        data = {"title": {"en": "Hi", "es": "Hola"}, "summary": {"en": "Text", "es": "Texto"}}
        s = BookTranslatableWritableSerializer(data=data, context={"request": request})
        self.assertTrue(s.is_valid(), s.errors)
        book = s.save()
        self.assertEqual(book.title, "Hi")
        self.assertEqual(book.summary, "Text")
        qs = Translation.objects.filter(object_id=str(book.pk)).values_list("language", "field_name", "field_value")
        self.assertEqual(set(qs), {("es", "title", "Hola"), ("es", "summary", "Texto")})

    def test_update_stores_translations(self):
        book = Book.objects.create(title="Old", summary="OldS")
        factory = APIRequestFactory()
        request = factory.put("/", {}, format="json")
        request = Request(request)
        data = {"title": {"en": "Old", "es": "Nuevo"}, "summary": {"en": "OldS"}}
        s = BookTranslatableWritableSerializer(book, data=data, partial=True, context={"request": request})
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        trans = Translation.objects.get(object_id=str(book.pk), language="es", field_name="title")
        self.assertEqual(trans.field_value, "Nuevo")


class TranslatableGettextSerializerTest(TestCase):
    def test_representation_returns_value(self):
        book = Book.objects.create(title="Hello", summary="")
        s = BookGettextSerializer(book)
        self.assertEqual(s.data["title"], "Hello")


class TranslatableGettextDictSerializerTest(TestCase):
    def test_representation_is_dict(self):
        book = Book.objects.create(title="Hello", summary="")
        s = BookGettextDictSerializer(book)
        self.assertIsInstance(s.data["title"], dict)
        self.assertIn("en", s.data["title"])
