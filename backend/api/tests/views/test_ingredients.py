from rest_framework import status
from core.tests.base import (
    EndpointTestCase, TestSimpleListMixin, TestSimpleDetailMixin,
    TestIngredient
)


class IngredientEndpointTestCase(EndpointTestCase, TestIngredient):
    BASE_URL = '/api/ingredients/'


class IngredientListTestCase(TestSimpleListMixin, IngredientEndpointTestCase):
    INSTANCE_COUNT = 10

    def test_anon_request_with_search_param_ok(self):
        search_value = self.NAME_PREFIX + '1'
        request_data = dict(name=search_value)
        exp_response_data = [
            self.get_instance_data(i)
            for i in self.Model.objects.filter(name__startswith=search_value)
        ]
        self.do_anon_request_and_check_response(
            exp_response_data, status.HTTP_200_OK, request_data=request_data
        )
        print(f'\n{self.response.json()}\n')

    def test_anon_request_with_search_param_ok_1(self):
        exp_response_data = []
        for search_value in (self.NAME_PREFIX + '3', self.NAME_PREFIX.lower()+'1'):
            with self.subTest(search=search_value):
                request_data = dict(name=search_value)
                self.do_anon_request_and_check_response(
                    exp_response_data, status.HTTP_200_OK, request_data=request_data
                )



class IngredientDetailTestCase(
    TestSimpleDetailMixin, IngredientEndpointTestCase
):
    pass
