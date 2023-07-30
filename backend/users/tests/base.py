from django.contrib.auth import get_user_model

from core.tests.base import EndpointTestCase, EndpointModelMixin


class UserEndpointTestCase(EndpointTestCase, EndpointModelMixin):
    Model = get_user_model()
    INSTANCE_FIELDS = (
        'id', 'email', 'username', 'first_name', 'last_name'
    )
    BASE_URL = '/api/users/'

    @classmethod
    def create_instance(cls, data, **kwargs):
        data.update(**kwargs)
        return cls.Model.objects.create_user(**data)

    @classmethod
    def create_data(cls, *, n='test', **kwargs):
        data = dict(
            email=f'mail_{n}@email.any',
            username=f'user_{n}',
            first_name=f'first_name_{n}',
            last_name=f'last_name_{n}',
        )
        data.update(**kwargs)
        return data

    @classmethod
    def get_data_iter(cls, iter):
        return (cls.create_data(n=i) for i in iter)

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


class AuthEndpointTestCase(UserEndpointTestCase):
    BASE_URL = '/api/auth/token/'
