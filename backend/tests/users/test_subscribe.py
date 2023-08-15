from rest_framework import status

from tests.base import (
    get_nth_subset, nrange, 
    TagsIngredientsMixin, TestRecipe
)
from .base import UserEndpointTestCase 


class UserSubscribeTestCase(TagsIngredientsMixin, UserEndpointTestCase):
    RECIPE_COUNT = 1
    recipe_fids = nrange(1, RECIPE_COUNT)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_instance('user')
        cls.author = cls.create_instance('author')
        cls.user_other = cls.create_instance('other')
        cls.user.subscribe_to(cls.user_other)
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

    def test_auth_user_can_subscribe_to_author(self):
        exp_response_data = self.create_data(
            fid='author', id=self.author.pk, is_subscribed=True,
            recipes_count=self.RECIPE_COUNT,
            recipes=[
                self.create_recipe_data(fid) for fid in self.recipe_fids
            ]
        )
        self.do_request_and_check_response(
            self.user_client, self.author.pk, exp_response_data, 
            status.HTTP_201_CREATED
        )
        self.assertEqual(self.user.subscribed_to.count(), 2)
        self.assertTrue(self.user.is_subscribed_to(self.author))


    
    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status, **kwargs
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}{id}/subscribe/', None, 
            exp_response_data, exp_status, **kwargs
        )