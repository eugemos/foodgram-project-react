from django.core.files import File
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import (
    TEST_HOST,
    TestIngredient, TestTag, TestUser
)
from .base import RecipeEndpointTestCase


class RecipeDetailEndpointTestCase(RecipeEndpointTestCase):
    # TAGS_PER_RECIPE = 2
    # INGREDIENTS_PER_RECIPE = 2
    # FIXTURE_RECIPE_COUNT = 2**3
    FIXTURE_TAG_COUNT = 3
    FIXTURE_INGREDIENT_COUNT = 3
    # FIXTURE_AUTHOR_COUNT = 2
    # recipe_ids = range(1, FIXTURE_RECIPE_COUNT+1)
    tag_fids = range(1, FIXTURE_TAG_COUNT+1)
    ingredient_fids = range(1, FIXTURE_INGREDIENT_COUNT+1)
    # author_ids = range(1, FIXTURE_AUTHOR_COUNT+1)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tags = TestTag.create_instances(cls.tag_fids)
        cls.ingredients = TestIngredient.create_instances(cls.ingredient_fids)
        cls.author = TestUser.create_instance('author')
        cls.client_user = TestUser.create_instance('client')
        cls.recipe = cls.create_instance(
            author=cls.author,
            image=File(open('tests/data/test.png'), name=f'recipe.png'),
        )
        cls.recipe.set_tags(cls.tags)
        for ingredient in cls.ingredients:
            cls.recipe.add_ingredient(ingredient, ingredient.pk)

        cls.base_exp_response_data = cls.create_data(
            id = cls.recipe.pk,
            tags = [TestTag.create_data(fid=fid, id=fid) for fid in cls.tag_fids],
            author = TestUser.create_data(
                fid='author', id=cls.author.pk, is_subscribed=False
            ),
            ingredients = [
                TestIngredient.create_data(fid=fid, id=fid, amount=fid)
                for fid in cls.ingredient_fids
            ],
            is_favorited=False,
            is_in_shopping_cart=False,
            image=f'{TEST_HOST}{settings.MEDIA_URL}{cls.recipe.image.name}'
        )
        assert set(cls.base_exp_response_data.keys()) == set(cls.OUTPUT_FIELDS)

    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)
        self.maxDiff = None

    def test_auth_user_can_retrieve_recipe_detail(self):
        exp_response_data = self.base_exp_response_data
        self.do_auth_request_and_check_response(
            self.recipe.pk, exp_response_data, status.HTTP_200_OK
        )

    def test_auth_user_can_retrieve_recipe_detail_1(self):
        self.set_bool_fields_to_true()
        exp_response_data = dict(
            self.base_exp_response_data,
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
        exp_response_data = self.base_exp_response_data
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
