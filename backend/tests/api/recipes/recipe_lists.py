from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import TEST_HOST, TestUser
from .base import RecipeEndpointTestCase


class RecipeAddToListTestCase(RecipeEndpointTestCase):
    OUTPUT_FIELDS = (
        'id', 'name', 'image', 'cooking_time',
    )

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

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

    @classmethod
    def create_exp_response_data(
        cls, instance, *, fid, **kwargs
    ):
        data = cls.create_data(
            fid=fid,
            id=instance.pk,
            image=f'{TEST_HOST}{settings.MEDIA_URL}{instance.image.name}'
        )
        data.update(**kwargs)
        del data['text']
        # cls.assertEqual(set(data.keys()), set(cls.OUTPUT_FIELDS))
        assert set(data.keys()) == set(cls.OUTPUT_FIELDS)
        return data

    def check_auth_user_can_add_recipe_to_list(self):
        exp_response_data = self.create_exp_response_data(self.recipe, fid='test')
        self.do_request_and_check_response(
            self.user_client, self.recipe.pk, exp_response_data,
            status.HTTP_201_CREATED
        )
        self.check_db_changed_properly()

    def check_anon_user_cant_add_recipe_to_list(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.check_request_fails(
            self.client, self.recipe.pk, exp_response_data,
            status.HTTP_401_UNAUTHORIZED
        )

    def check_auth_user_cant_add_recipe_to_list_twice(self):
        exp_response_data = dict(errors='Этот рецепт уже есть в этом списке.')
        self.check_request_fails(
            self.user_client, self.recipe_other.pk, exp_response_data,
            status.HTTP_400_BAD_REQUEST
        )

    def check_request_to_unexistent_recipe_fails(self):
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
        self.check_db_unchanged()


class RecipeRemoveFromListTestCase(RecipeEndpointTestCase):
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

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

    def check_auth_user_can_remove_recipe_from_list(self):
        self.do_request_and_check_response(
            self.user_client, self.recipe.pk, (),
            status.HTTP_204_NO_CONTENT
        )
        self.check_db_changed_properly()

    def check_anon_user_cant_remove_recipe_from_list(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.check_request_fails(
            self.client, self.recipe.pk, exp_response_data,
            status.HTTP_401_UNAUTHORIZED
        )

    def check_auth_user_cant_remove_from_list_recipe_which_is_not_there(self):
        exp_response_data = dict(errors='Этого рецепта нет в этом списке.')
        self.check_request_fails(
            self.user_client, self.recipe_other.pk, exp_response_data,
            status.HTTP_400_BAD_REQUEST
        )

    def check_request_to_unexistent_recipe_fails(self):
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
        self.check_db_unchanged()
