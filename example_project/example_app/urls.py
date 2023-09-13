from django.urls import path
from . import views

urlpatterns = [
    path('translatable_db/', views.ExampleModelTranslatableDBView.as_view(), name='translatable_db'),
    path('translatable_db_dict/', views.ExampleModelTranslatableDBDictView.as_view(), name='translatable_db_dict'),
    path('translatable_gettext/', views.ExampleModelTranslatableGettextView.as_view(), name='translatable_gettext'),
    path('translatable_gettext_dict/', views.ExampleModelTranslatableGettextDictView.as_view(), name='translatable_gettext_dict'),
]
