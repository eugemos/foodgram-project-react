from core.tests.base import (
    EndpointTestCase, TestSimpleListMixin, TestSimpleDetailMixin,
    TestIngredient
)


class IngredientEndpointTestCase(EndpointTestCase, TestIngredient):
    BASE_URL = '/api/ingredients/'


class IngredientListTestCase(TestSimpleListMixin, IngredientEndpointTestCase):
    pass


class IngredientDetailTestCase(
    TestSimpleDetailMixin, IngredientEndpointTestCase
):
    pass
