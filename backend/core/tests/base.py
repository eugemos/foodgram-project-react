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


def get_model_pk_set(model):
    return set(instance.pk for instance in model.objects.all())
    
def left_extend_str(s, dest_size, char='q'):
    return char * (dest_size - len(s)) + s
