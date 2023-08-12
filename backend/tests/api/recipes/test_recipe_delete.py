from rest_framework import status
from rest_framework.test import APIClient

from api.models import IngredientOccurence
from tests.base import (
    nrange, TestIngredient, TestTag, TestUser
)
from .base import RecipeEndpointTestCase


class RecipeDeleteEndpointTestCase(RecipeEndpointTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = TestUser.create_instance('author')
        cls.user = TestUser.create_instance('user')
        cls.recipe = cls.create_recipe(
            'any', cls.author, cls.tags, cls.ingredients
        )
        cls.user.add_to_favorites(cls.recipe)
        cls.user.add_to_shopping_cart(cls.recipe)

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)
        self.author_client = APIClient()
        self.author_client.force_authenticate(user=self.author)
        self.check_db_not_changed()

    def test_author_can_delete_recipe(self):
        self.do_request_and_check_response(
            self.author_client, self.recipe.pk, (), status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(self.Model.objects.count(), 0)
        self.assertEqual(IngredientOccurence.objects.count(), 0)
        self.assertEqual(self.user.favorites.count(), 0)
        self.assertEqual(self.user.shopping_cart.count(), 0)

    def test_non_author_cant_delete_recipe(self):
        self.check_request_fails(
            self.user_client, self.recipe.pk,
            self.FORBIDDEN_ERROR_RESPONSE_DATA, status.HTTP_403_FORBIDDEN
        )

    def test_anon_user_cant_delete_recipe(self):
        self.check_request_fails(
            self.client, self.recipe.pk,
            self.UNAUTHORIZED_ERROR_RESPONSE_DATA, status.HTTP_401_UNAUTHORIZED
        )

    def test_request_to_unexistent_recipe_fails(self):
        for id in (0, self.recipe.pk + 1):
            for n, client in enumerate((self.user_client, self.author_client)):
                with self.subTest(id=id, client=n):
                    self.check_request_fails(
                        client, id, self.PAGE_NOT_FOUND_RESPONSE_DATA,
                        status.HTTP_404_NOT_FOUND
                    )

    def check_request_fails(self, client, id, exp_response_data, exp_status):
        self.do_request_and_check_response(
            client, id, exp_response_data, exp_status
        )
        self.check_db_not_changed()

    def check_db_not_changed(self):
        self.assertEqual(self.Model.objects.count(), 1)
        self.assertEqual(
            IngredientOccurence.objects.count(), self.INGREDIENT_COUNT
        )
        self.assertEqual(self.user.favorites.count(), 1)
        self.assertEqual(self.user.shopping_cart.count(), 1)

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'delete', f'{self.BASE_URL}{id}/',
            None, exp_response_data, exp_status
        )
