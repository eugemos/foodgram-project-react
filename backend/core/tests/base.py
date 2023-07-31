from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


TEST_HOST = 'http://testserver'


class EndpointTestCase(APITestCase):

    def do_request_and_check_response(
        self, client, method, url, request_data, exp_response_data, exp_status, **kwargs
    ):
        func = getattr(client, method)
        self.response = func(url, request_data, format='json', **kwargs)
        with self.subTest():
            self.assertEqual(self.response.status_code, exp_status)
        
        if exp_response_data == ():
            return None

        # print(f'\n{self.response.content}\n')
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        return response_data        


class TestModel:
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
        if not isinstance(data, dict):
            if data is None:
                data = cls.create_data()
            else:
                data = cls.create_data(n=data)

        data.update(**kwargs)
        return cls.Model.objects.create(**data)

    @classmethod
    def create_instances(cls, data_seq):
        for data in data_seq:
            cls.create_instance(data)

    @classmethod
    def get_pk_set(cls):
        return set(instance.pk for instance in cls.Model.objects.all())


class TestUser(TestModel):
    Model = get_user_model()
    INSTANCE_FIELDS = (
        'id', 'email', 'username', 'first_name', 'last_name'
    )

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



def get_model_pk_set(model):
    return set(instance.pk for instance in model.objects.all())
    
def left_extend_str(s, dest_size, char='q'):
    return char * (dest_size - len(s)) + s
