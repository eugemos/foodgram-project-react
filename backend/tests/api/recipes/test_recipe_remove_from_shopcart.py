# from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import TestUser
from .base import RecipeEndpointTestCase


class RecipeRemoveFromShopcartTestCase(RecipeEndpointTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = TestUser.create_instance('author')
        cls.user = TestUser.create_instance('user')
        cls.recipe = cls.create_recipe(
            'test', cls.author, cls.tags, cls.ingredients
        )
        cls.recipe_other = cls.create_recipe(
            'other', cls.user, cls.tags, cls.ingredients
        )
        cls.user.add_to_shopping_cart(cls.recipe)

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)
        self.assertEqual(self.user.shopping_cart.count(), 1)

    def test_auth_user_can_remove_recipe_from_shopcart(self):
        self.do_request_and_check_response(
            self.user_client, self.recipe.pk, (),
            status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(self.user.shopping_cart.count(), 0)

    def test_anon_user_cant_remove_recipe_from_shopcart(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.check_request_fails(
            self.client, self.recipe.pk, exp_response_data,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_auth_user_cant_remove_from_shopcart_recipe_which_is_not_there(self):
        exp_response_data = dict(errors='Этого рецепта нет в этом списке.')
        self.check_request_fails(
            self.user_client, self.recipe_other.pk, exp_response_data,
            status.HTTP_400_BAD_REQUEST
        )

    def test_request_to_unexistent_recipe_fails(self):
        exp_response_data = self.PAGE_NOT_FOUND_RESPONSE_DATA
        self.check_request_fails(
            self.user_client, 10, exp_response_data,
            status.HTTP_404_NOT_FOUND
        )

    def check_request_fails(
        self, client, id, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            client, id, exp_response_data, exp_status
        )
        self.assertEqual(self.user.shopping_cart.count(), 1)
        self.assertTrue(self.user.has_in_shopping_cart(self.recipe))

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'delete', f'{self.BASE_URL}{id}/shopping_cart/',
            None, exp_response_data, exp_status
        )
