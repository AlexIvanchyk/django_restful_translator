from rest_framework import generics

from .models import ExampleModel
from .serializers import (
    ExampleModelTranslatableDBSerializer,
    ExampleModelTranslatableDBDictSerializer,
    ExampleModelTranslatableGettextSerializer,
    ExampleModelTranslatableGettextDictSerializer,
    ExampleModelTranslatableWritableDBDictSerializer
)


class ExampleModelTranslatableDBView(generics.ListCreateAPIView):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelTranslatableDBSerializer


class ExampleModelTranslatableDBDictView(generics.ListCreateAPIView):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelTranslatableDBDictSerializer


class ExampleModelTranslatableGettextView(generics.ListCreateAPIView):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelTranslatableGettextSerializer


class ExampleModelTranslatableGettextDictView(generics.ListCreateAPIView):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelTranslatableGettextDictSerializer


class ExampleModelTranslatableWritebleDBDictView(generics.ListCreateAPIView):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelTranslatableWritableDBDictSerializer


class ExampleModelTranslatableWritebleDBDictDetails(generics.RetrieveUpdateAPIView):
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelTranslatableWritableDBDictSerializer
