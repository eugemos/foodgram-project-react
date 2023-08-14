from rest_framework import status

from .recipe_lists import RecipeAddToListTestCase


class RecipeAddToShopcartTestCase(RecipeAddToListTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user.add_to_shopping_cart(cls.recipe_other)

    def test_auth_user_can_add_recipe_to_shopcart(self):
        self.check_auth_user_can_add_recipe_to_list()

    def test_anon_user_cant_add_recipe_to_shopcart(self):
        self.check_anon_user_cant_add_recipe_to_list()

    def test_auth_user_cant_add_recipe_to_shopcart_twice(self):
        self.check_auth_user_cant_add_recipe_to_list_twice()

    def test_request_to_unexistent_recipe_fails(self):
        self.check_request_to_unexistent_recipe_fails()

    def check_db_changed_properly(self):
        self.assertEqual(self.user.shopping_cart.count(), 2)
        self.assertTrue(self.user.has_in_shopping_cart(self.recipe))

    def check_db_unchanged(self):
        self.assertEqual(self.user.shopping_cart.count(), 1)
        self.assertTrue(self.user.has_in_shopping_cart(self.recipe_other))

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}{id}/shopping_cart/',
            None, exp_response_data, exp_status
        )
