import unittest

from rest_framework import status
from tests.base import (
    EndpointTestCase, TestSimpleListMixin, TestSimpleDetailMixin,
    TestIngredient, db_is_sqlite
)


class IngredientEndpointTestCase(EndpointTestCase, TestIngredient):
    BASE_URL = '/api/ingredients/'


class IngredientListTestCase(TestSimpleListMixin, IngredientEndpointTestCase):
    pass


class IngredientListTestCaseWithSearch(IngredientEndpointTestCase):

    INSTANCE_COUNT = 10

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_instances(range(1, cls.INSTANCE_COUNT + 1))

    def test_anon_request_with_search_param_ok(self):
        search_value = self.NAME_PREFIX + '001'
        request_data = dict(name=search_value)
        exp_response_data = [
            self.get_instance_data(i)
            for i in self.Model.objects.filter(name__startswith=search_value)
        ]
        assert len(exp_response_data) > 0
        self.do_anon_request_and_check_response(
            request_data, exp_response_data
        )

    @unittest.skipIf(db_is_sqlite(), 'sqlite сравнивает без учёта регистра')
    def test_anon_request_with_search_param_ok_1(self):
        exp_response_data = []
        for search_value in (
            self.NAME_PREFIX + '0', self.NAME_PREFIX.lower() + '1'
        ):
            with self.subTest(search=search_value):
                request_data = dict(name=search_value)
                self.do_anon_request_and_check_response(
                    request_data, exp_response_data
                )

    def do_anon_request_and_check_response(
        self, request_data, exp_response_data
    ):
        return super().do_request_and_check_response(
            self.client, 'get', self.BASE_URL, 
            request_data, exp_response_data, status.HTTP_200_OK
        )


class IngredientDetailTestCase(
    TestSimpleDetailMixin, IngredientEndpointTestCase
):
    pass
