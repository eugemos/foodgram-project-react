from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import TEST_HOST, TestUser
from .base import RecipeEndpointTestCase


class RecipeAddToShopcartTestCase(RecipeEndpointTestCase):
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
        cls.create_recipe(
            'other', cls.user, cls.tags, cls.ingredients
        )

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)
        self.assertEqual(self.user.shopping_cart.count(), 0)

    def test_auth_user_can_add_recipe_to_shopcart(self):
        exp_response_data = self.create_exp_response_data(self.recipe, fid='test')
        self.do_request_and_check_response(
            self.user_client, self.recipe.pk, exp_response_data,
            status.HTTP_201_CREATED
        )
        self.assertEqual(self.user.shopping_cart.count(), 1)
        self.assertTrue(self.user.has_in_shopping_cart(self.recipe))

    def test_anon_user_cant_add_recipe_to_shopcart(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.do_request_and_check_response(
            self.client, self.recipe.pk, exp_response_data,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(self.user.shopping_cart.count(), 0)

    def test_auth_user_cant_add_recipe_to_shopcart_twice(self):
        self.user.add_to_shopping_cart(self.recipe)
        exp_response_data = dict(errors='Этот рецепт уже есть в этом списке.')
        self.do_request_and_check_response(
            self.user_client, self.recipe.pk, exp_response_data,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(self.user.shopping_cart.count(), 1)

    def test_request_to_unexistent_recipe_fails(self):
        exp_response_data = self.PAGE_NOT_FOUND_RESPONSE_DATA
        self.do_request_and_check_response(
            self.user_client, 10, exp_response_data,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(self.user.shopping_cart.count(), 0)

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

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}{id}/shopping_cart/',
            None, exp_response_data, exp_status
        )