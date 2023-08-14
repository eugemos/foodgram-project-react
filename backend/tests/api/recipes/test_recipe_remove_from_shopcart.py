# from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import TestUser
from .recipe_lists import RecipeRemoveFromListTestCase


class RecipeRemoveFromShopcartTestCase(RecipeRemoveFromListTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user.add_to_shopping_cart(cls.recipe)

    def setUp(self):
        super().setUp()
        self.assertEqual(self.user.shopping_cart.count(), 1)

    def test_auth_user_can_remove_recipe_from_shopcart(self):
        self.check_auth_user_can_remove_recipe_from_list()

    def test_anon_user_cant_remove_recipe_from_shopcart(self):
        self.check_anon_user_cant_remove_recipe_from_list()

    def test_auth_user_cant_remove_from_shopcart_recipe_which_is_not_there(self):
        self.check_auth_user_cant_remove_from_list_recipe_which_is_not_there()

    def test_request_to_unexistent_recipe_fails(self):
        self.check_request_to_unexistent_recipe_fails()

    def check_db_changed_properly(self):
        self.assertEqual(self.user.shopping_cart.count(), 0)

    def check_db_unchanged(self):
        self.assertEqual(self.user.shopping_cart.count(), 1)
        self.assertTrue(self.user.has_in_shopping_cart(self.recipe))

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'delete', f'{self.BASE_URL}{id}/shopping_cart/',
            None, exp_response_data, exp_status
        )
