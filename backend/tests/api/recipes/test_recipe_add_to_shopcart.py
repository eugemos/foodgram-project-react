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
        # self.author_client = APIClient()
        # self.author_client.force_authenticate(user=self.author)
        self.check_db_not_changed()

    def test_auth_user_can_add_recipe_to_shopcart(self):
        exp_response = self.create_exp_response_data(self.recipe, fid='test')
        self.do_request_and_check_response(
            self.user_client, self.recipe.pk, exp_response, status.HTTP_201_CREATED
        )
        # self.assertEqual(self.Model.objects.count(), 0)
        self.assertEqual(self.user.shopping_cart.count(), 1)
        self.assertTrue(self.user.has_in_shopping_cart(self.recipe))

    def check_request_fails(self, client, id, exp_response_data, exp_status):
        self.do_request_and_check_response(
            client, id, exp_response_data, exp_status
        )
        self.check_db_not_changed()

    def check_db_not_changed(self): 
        # self.assertEqual(self.Model.objects.count(), 1)
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