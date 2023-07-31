from rest_framework import status

from api.models import Tag
from core.tests.base import EndpointTestCase, TestModel


class TestTag(TestModel):
    Model = Tag
    INSTANCE_FIELDS = (
        'id', 'name', 'color', 'slug', 
    )

    @classmethod
    def create_data(cls, *, n=0, **kwargs):
        n = int(n)
        color = format(n, '56x')
        data = dict(
            name=f'name_{n}',
            color=f'#{color}',
            slug=f'slug_{n}',
        )
        data.update(**kwargs)
        return data


class TagEndpointTestCase(EndpointTestCase, TestTag):
    BASE_URL = '/api/tags/'


class TagListTestCase(TagEndpointTestCase):

    def test_anon_request_ok(self):
        self.create_instances((1,2,3))
        exp_response_data = [
            self.get_instance_data(instance) 
            for instance in self.Model.objects.all()
        ]
        self.do_anon_request_and_check_response(
            exp_response_data, status.HTTP_200_OK
        )
        
    def test_anon_request_ok_with_empty_db(self):
        self.do_anon_request_and_check_response([], status.HTTP_200_OK)

    def do_anon_request_and_check_response(
        self, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            self.client, 'get', self.BASE_URL, 
            None, exp_response_data, exp_status
        )


class TagDetailTestCase(TagEndpointTestCase):
    INSTANCE_COUNT = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_instances(range(1, cls.INSTANCE_COUNT + 1))

    def test_anon_request_to_existent_tag_ok(self):
        id = self.INSTANCE_COUNT
        exp_response_data = self.get_instance_data(self.Model.objects.get(id=id))
        self.do_anon_request_and_check_response(id, exp_response_data, status.HTTP_200_OK)

    def test_anon_request_to_unexistent_tag_fails(self):
        id = self.INSTANCE_COUNT + 1
        exp_response_data = {'detail': 'Страница не найдена.'}
        self.do_anon_request_and_check_response(id, exp_response_data, status.HTTP_404_NOT_FOUND)

    def do_anon_request_and_check_response(
        self, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            self.client, 'get', f'{self.BASE_URL}{id}/', 
            None, exp_response_data, exp_status
        )    
