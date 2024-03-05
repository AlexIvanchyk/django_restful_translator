from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ExampleModelAPITests(APITestCase):
    fixtures = ['example_project/initial_data.json']

    def test_db_list_endpoint(self):
        url = reverse('example_app:translatable_db')
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "Hello")

    def test_db_list_endpoint_spanish(self):
        url = reverse('example_app:translatable_db')
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='es')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "Hola")

    def test_db_dict_list_endpoint(self):
        url = reverse('example_app:translatable_db_dict')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data[0]['name'], {"en": "Hello", "es": "Hola"})

    def test_gettext_list_endpoint(self):
        url = reverse('example_app:translatable_gettext')
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "Hello")

    def test_gettext_list_endpoint_spanish(self):
        url = reverse('example_app:translatable_gettext')
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='es')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "Hola")

    def test_gettext_dict_list_endpoint(self):
        url = reverse('example_app:translatable_gettext_dict')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data[0]['name'], {"en": "Hello", "es": "Hola"})

    def test_writeble_db_dict_list_list(self):
        url = reverse('example_app:translatable_writeble_db_dict')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data[0]['name'], {"en": "Hello", "es": "Hola"})

    def test_writeble_db_dict_retrieve(self):
        url = reverse('example_app:translatable_writeble_db_dict', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data['name'], {'en': 'Hello', 'es': 'Hola'})

    def test_writeble_db_dict_list_create(self):
        url = reverse('example_app:translatable_writeble_db_dict')
        data = {
            'name': {'es': 'Hola'},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(response.data['name'], {'en': None, 'es': 'Hola'})

    def test_writeble_db_dict_list_update(self):
        url = reverse('example_app:translatable_writeble_db_dict', kwargs={'pk': 1})
        data = {
            'name': {'es': 'Adiós'},
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data['name'], {'en': 'Hello', 'es': 'Adiós'})
