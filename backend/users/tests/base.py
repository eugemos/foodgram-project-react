from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


TEST_HOST = 'http://testserver'

class UserEndpointTestCase(APITestCase):
    Model = get_user_model()
    BASE_URL = '/api/users/'

    def create_test_instance(self, data):
        return self.Model.objects.create(**data)

    def check_object_is_dict_with_proper_keys(self, obj, keys):
        self.assertIsInstance(obj, dict)
        self.assertEqual(set(obj.keys()), set(keys))

    def check_object_is_list_of_proper_length(self, obj, length):
        self.assertIsInstance(obj, list)
        self.assertEqual(len(obj), length)

    def check_dict_has_proper_items(self, d, obj=None, **kwargs):
        if obj is not None:
            for key in d:
                with self.subTest(key=key):
                    if hasattr(obj, key):
                        self.assertEqual(d[key], getattr(obj, key))
        
        for key in kwargs:
            with self.subTest(key=key):
                self.assertEqual(d[key], kwargs[key])
