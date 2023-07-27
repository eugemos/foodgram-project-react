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

    def check_data_is_dict_with_proper_keys(self, data, keys):
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data.keys()), set(keys))

    def check_data_is_list_of_proper_length(self, data, length):
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), length)

    def check_data_is_dict_with_proper_items(self, data, instance=None, **kwargs):
        if instance is not None:
            for key in data:
                with self.subTest(key=key):
                    if hasattr(instance, key):
                        self.assertEqual(data[key], getattr(instance, key))
        
        for key in kwargs:
            with self.subTest(key=key):
                self.assertEqual(data[key], kwargs[key])

    def check_instance(self, instance, data):
        self.check_data_is_dict_with_proper_items(data, instance)


def left_extend_str(s, dest_size, char='q'):
    return char * (dest_size - len(s)) + s
