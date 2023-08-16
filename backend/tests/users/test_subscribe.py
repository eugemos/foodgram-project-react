from rest_framework import status

from tests.base import (
    get_nth_subset, nrange, 
    TagsIngredientsMixin, TestRecipe
)
from .base import UserEndpointTestCase 


class UserSubscribeTestCase(TagsIngredientsMixin, UserEndpointTestCase):
    RECIPE_COUNT = 10
    recipe_fids = nrange(1, RECIPE_COUNT)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_instance('user')
        cls.author = cls.create_instance('author')
        cls.author_other = cls.create_instance('other')
        cls.user.subscribe_to(cls.author_other)
        for fid in cls.recipe_fids:
            tags = get_nth_subset(cls.tags, fid)
            ingredients = get_nth_subset(cls.ingredients, fid)
            recipe = TestRecipe.create_instance(fid, cls.author, tags, ingredients)

    @staticmethod
    def create_recipe_data(fid):
        data = TestRecipe.create_data(
            fid=fid,
            id=fid,
            image=TestRecipe.get_image_url(pk=fid)
        )
        del data['text']
        return data

    def setUp(self):
        super().setUp()
        self.user_client = self.create_auth_client(self.user)
        self.maxDiff = None

    def test_auth_user_can_subscribe_to_author(self):
        self.check_auth_request_ok('', self.RECIPE_COUNT)

    def test_auth_user_can_subscribe_to_author_with_params(self):
        recipes_limit = self.RECIPE_COUNT // 2
        self.check_auth_request_ok(f'?recipes_limit={recipes_limit}', recipes_limit)
    
    def test_auth_user_can_subscribe_to_author_with_params_1(self):
        recipes_limit = self.RECIPE_COUNT + 1
        self.check_auth_request_ok(f'?recipes_limit={recipes_limit}', self.RECIPE_COUNT)
    
    def test_auth_user_can_subscribe_to_author_with_zero_param(self):
        self.check_auth_request_ok(f'?recipes_limit={0}', self.RECIPE_COUNT)

    def test_auth_user_can_subscribe_to_author_with_empty_param(self):
        self.check_auth_request_ok('?recipes_limit', self.RECIPE_COUNT)

    def test_auth_user_can_subscribe_to_author_with_invalid_param(self):
        self.check_auth_request_ok('?recipes_limit=xxx', self.RECIPE_COUNT)

    def check_auth_request_ok(self, request_data, exp_recipe_count):
        exp_response_data = self.create_data(
            fid='author', id=self.author.pk, is_subscribed=True,
            recipes_count=exp_recipe_count,
            recipes=[
                self.create_recipe_data(fid) for fid in nrange(1, exp_recipe_count)
            ]
        )
        self.do_request_and_check_response(
            self.user_client, self.author.pk, request_data, exp_response_data, 
            status.HTTP_201_CREATED
        )
        self.assertEqual(self.user.subscribed_to.count(), 2)
        self.assertTrue(self.user.is_subscribed_to(self.author))

    def test_auth_user_cant_subscribe_to_himself(self):
        self.check_request_fails(
            self.user_client, self.user.pk,
            dict(errors='Нельзя подписаться на самого себя.'), 
            status.HTTP_400_BAD_REQUEST
        )

    def test_auth_user_cant_subscribe_to_author_twice(self):
        self.check_request_fails(
            self.user_client, self.author_other.pk,
            dict(errors='Вы уже подписаны на этого автора.'), 
            status.HTTP_400_BAD_REQUEST
        )

    def test_anon_user_cant_subscribe_to_author(self):
        self.check_request_fails(
            self.client, self.author.pk, self.UNAUTHORIZED_ERROR_RESPONSE_DATA, 
            status.HTTP_401_UNAUTHORIZED
        )

    def test_request_to_unexistent_author_fails(self):
        self.check_request_fails(
            self.user_client, 10, self.PAGE_NOT_FOUND_RESPONSE_DATA, 
            status.HTTP_404_NOT_FOUND
        )

    def check_request_fails(self, client, id, exp_response_data, exp_status):
        self.do_request_and_check_response(
            client, id, '', exp_response_data, exp_status
        )
        self.assertEqual(self.user.subscribed_to.count(), 1)
        self.assertFalse(self.user.is_subscribed_to(self.author))

    def do_request_and_check_response(
        self, client, id, query_params, exp_response_data, exp_status, **kwargs
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}{id}/subscribe/{query_params}', None,
            exp_response_data, exp_status, **kwargs
        )
