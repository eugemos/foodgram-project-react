from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


TEST_HOST = 'http://testserver'


class EndpointTestCase(APITestCase):

    def do_request_and_check_response(
        self, client, method, url, request_data, exp_response_data, exp_status, **kwargs
    ):
        func = getattr(client, method)
        # Act
        self.response = func(url, request_data, format='json', **kwargs)
        # Assert on response
        with self.subTest():
            self.assertEqual(self.response.status_code, exp_status)
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        return response_data


class EndpointModelMixin:
    @classmethod
    def get_instance_data(cls, instance, **kwargs):
        data = {
            field_name: getattr(instance, field_name)
            for field_name in cls.INSTANCE_FIELDS
        }
        data.update(**kwargs)
        return data

    @classmethod
    def create_instance(cls, data, **kwargs):
        data.update(**kwargs)
        return cls.Model.objects.create(**data)

    @classmethod
    def create_instances(cls, data_seq):
        for data in data_seq:
            cls.create_instance(data)


class UserEndpointTestCase(EndpointTestCase, EndpointModelMixin):
    Model = get_user_model()
    INSTANCE_FIELDS = (
        'id', 'email', 'username', 'first_name', 'last_name'
    )
    BASE_URL = '/api/users/'

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


def get_model_pk_set(model):
    return set(instance.pk for instance in model.objects.all())
    
def left_extend_str(s, dest_size, char='q'):
    return char * (dest_size - len(s)) + s
