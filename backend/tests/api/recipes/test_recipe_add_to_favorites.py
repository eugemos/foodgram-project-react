from rest_framework import status

from .recipe_lists import RecipeAddToListTestCase


class RecipeAddToFavoritesTestCase(RecipeAddToListTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user.add_to_favorites(cls.recipe_other)

    def test_auth_user_can_add_recipe_to_favorites(self):
        self.check_auth_user_can_add_recipe_to_list()

    def test_anon_user_cant_add_recipe_to_favorites(self):
        self.check_anon_user_cant_add_recipe_to_list()

    def test_auth_user_cant_add_recipe_to_favorites_twice(self):
        self.check_auth_user_cant_add_recipe_to_list_twice()

    def test_request_to_unexistent_recipe_fails(self):
        self.check_request_to_unexistent_recipe_fails()

    def check_db_changed_properly(self):
        self.assertEqual(self.user.favorites.count(), 2)
        self.assertTrue(self.user.has_in_favore(self.recipe))

    def check_db_unchanged(self):
        self.assertEqual(self.user.favorites.count(), 1)
        self.assertTrue(self.user.has_in_favore(self.recipe_other))

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}{id}/favorite/',
            None, exp_response_data, exp_status
        )
