from django.core.files import File
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import (
    TEST_HOST, nrange,
    TestIngredient, TestTag, TestUser
)
from .base import RecipeEndpointTestCase


class RecipeDetailEndpointTestCase(RecipeEndpointTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = TestUser.create_instance('author')
        cls.client_user = TestUser.create_instance('client')
        cls.recipe = cls.create_instance(
            'any', cls.author, cls.tags, cls.ingredients
        )

    @classmethod
    def create_exp_response_data(cls):
        return super().create_exp_response_data(
            cls.recipe, fid='any', author_fid='author', author_id=cls.author.pk, 
            tag_fids=cls.tag_fids, ingredient_fids=cls.ingredient_fids
        )

    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)
        self.maxDiff = None

    def test_auth_user_can_retrieve_recipe_detail(self):
        exp_response_data = self.create_exp_response_data()
        self.do_auth_request_and_check_response(
            self.recipe.pk, exp_response_data, status.HTTP_200_OK
        )

    def test_auth_user_can_retrieve_recipe_detail_1(self):
        self.set_bool_fields_to_true()
        exp_response_data = dict(
            self.create_exp_response_data(),
            author = TestUser.create_data(
                fid='author', id=self.author.pk, is_subscribed=True
            ),
            is_favorited=True,
            is_in_shopping_cart=True
        )
        self.do_auth_request_and_check_response(
            self.recipe.pk, exp_response_data, status.HTTP_200_OK
        )

    def test_anon_user_can_retrieve_recipe_detail(self):
        self.set_bool_fields_to_true()
        exp_response_data = self.create_exp_response_data()
        self.do_anon_request_and_check_response(
            self.recipe.pk, exp_response_data, status.HTTP_200_OK
        )
    
    def test_request_to_unexistent_recipe_fails(self):
        exp_response_data = self.PAGE_NOT_FOUND_RESPONSE_DATA
        for id in (0, self.recipe.pk + 1):
            with self.subTest(id=id):
                self.do_anon_request_and_check_response(
                    id, exp_response_data, status.HTTP_404_NOT_FOUND
                )
                self.do_auth_request_and_check_response(
                    id, exp_response_data, status.HTTP_404_NOT_FOUND
                )

    def set_bool_fields_to_true(self):
        self.client_user.subscribe_to(self.author)
        self.client_user.add_to_favorites(self.recipe)
        self.client_user.add_to_shopping_cart(self.recipe)

    def do_anon_request_and_check_response(
        self, id, exp_response_data, exp_status
    ):
        return self.do_request_and_check_response(
            self.client, id, exp_response_data, exp_status
        )

    def do_auth_request_and_check_response(
        self, id, exp_response_data, exp_status
    ):
        return self.do_request_and_check_response(
            self.auth_client, id, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'get', f'{self.BASE_URL}{id}/',
            None, exp_response_data, exp_status
        )
