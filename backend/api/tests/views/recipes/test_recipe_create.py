from rest_framework import status

from api.models import Tag, Ingredient
from core.tests.base import (
    TestTag, TestIngredient, TestUser
)
from .base import (
    RecipeEndpointTestCase,
    load_file_as_base64_str,
)

INPUT_FIELDS = (
    'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
)
OUTPUT_FIELDS = (
    'id', 'tags', 'author', 'ingredients', 'is_favorited', 
    'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
)

class RecipeCreateEndpointTestCase(RecipeEndpointTestCase):
    FIXTURE_TAG_COUNT = 3
    FIXTURE_INGREDIENT_COUNT = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestTag.create_instances(range(1, cls.FIXTURE_TAG_COUNT+1))
        TestIngredient.create_instances(range(1, cls.FIXTURE_INGREDIENT_COUNT+1))
        cls.client_user = TestUser.create_instance(TestUser.create_data(n='client'))

    def test_auth_user_can_create_recipe(self):
        tag_ids = range(1, self.FIXTURE_TAG_COUNT)
        ingredient_ids = range(1, self.FIXTURE_INGREDIENT_COUNT)
        request_data = self.create_data(
            n=1,
            ingredients = [dict(id=i, amount=i) for i in ingredient_ids],
            tags = [id for id in tag_ids],
            image = load_file_as_base64_str('test.png')
        )
        assert set(request_data.keys()) == set(INPUT_FIELDS)
        exp_response_data = self.create_data(
            n=1,
            id = 1,
            tags = [TestTag.get_instance_data(Tag.objects.get(id=i)) for i in tag_ids],
            author = TestUser.get_instance_data(self.client_user, is_subscribed=False),
            ingredients = [
                TestIngredient.get_instance_data(
                    Ingredient.objects.get(id=i),
                    amount=i
                )
                for i in ingredient_ids
            ],
            is_favorited=False,
            is_in_shopping_cart=False,
            image='XXX'
        )
        assert set(exp_response_data.keys()) == set(OUTPUT_FIELDS)
        self.do_auth_request_and_check_response(request_data, (), status.HTTP_200_OK)

    def do_auth_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        return self.do_request_and_check_response(
            self.client, request_data, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, request_data, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', self.BASE_URL, 
            request_data, exp_response_data, exp_status
        )