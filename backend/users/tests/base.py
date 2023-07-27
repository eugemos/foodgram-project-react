from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


TEST_HOST = 'http://testserver'

class UserEndpointTestCase(APITestCase):
    Model = get_user_model()
    BASE_URL = '/api/users/'

    def create_test_data(self, n, **kwargs):
        data = dict(
            email=f'test_{n}@email.ru',
            username=f'test_{n}',
            first_name=f'first_name_{n}',
            last_name=f'last_name_{n}',
        )
        data.update(**kwargs)
        return data

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

    def check_object_corresponds_instance(self, obj, instance):
        self.assertIsInstance(obj, dict)
        for key in obj:
            with self.subTest(key=key):
                if hasattr(instance, key):
                    self.assertEqual(obj[key], getattr(instance, key))


def left_extend_str(s, dest_size, char='q'):
    return char * (dest_size - len(s)) + s
