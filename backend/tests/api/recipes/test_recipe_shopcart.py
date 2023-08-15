from unittest import skip

from rest_framework import status
from rest_framework.test import APIClient

from api.shopping_cart import ShoppingCart
from tests.base import (
    nrange, get_nth_subset,
    TestUser
)
from .base import RecipeEndpointTestCase

class RecipeShopcartTestCase(RecipeEndpointTestCase):
    INSTANCE_COUNT = 10
    AUTHOR_COUNT = 3
    author_fids = nrange(1, AUTHOR_COUNT)
    USER_SHOPPING_CART = (2, 3, 4, 6, 7)


    @classmethod
    def get_author_fid(cls, recipe_fid):
        r = recipe_fid % cls.AUTHOR_COUNT
        return  r if r > 0 else cls.AUTHOR_COUNT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert cls.INSTANCE_COUNT < 2**cls.TAG_COUNT
        assert cls.INSTANCE_COUNT < 2**cls.INGREDIENT_COUNT
        cls.authors = TestUser.create_instances(cls.author_fids)
        cls.user = TestUser.create_instance('user')
        # self.maxDiff = None
        for fid in nrange(1, cls.INSTANCE_COUNT):
            author = TestUser.Model.objects.get(id=cls.get_author_fid(fid))
            tags = get_nth_subset(cls.tags, fid)
            ingredients = get_nth_subset(cls.ingredients, fid)
            recipe=cls.create_instance(fid, author, tags, ingredients)

        assert cls.Model.objects.count() == cls.INSTANCE_COUNT

    def setUp(self):
        self.user_client = APIClient()
        self.user_client.force_authenticate(self.user)

    @classmethod
    def create_shopcart(cls, user, shopcart):
            for id in shopcart:
                user.add_to_shopping_cart(cls.Model.objects.get(id=id))

    def test_auth_user_can_download_shopcart(self):
        self.create_shopcart(self.user, self.USER_SHOPPING_CART)
        exp_response_data = ShoppingCart(self.user).to_text().encode('utf-8')
        self.do_request_and_check_response(self.user_client, (), status.HTTP_200_OK)
        self.assertEqual('text/plain; charset=utf-8', self.response['Content-Type'])
        self.assertEqual(
            f'attachment; filename="shopping_cart_{self.user.id}.txt"',
            self.response['Content-Disposition']
        )
        self.assertEqual(exp_response_data, self.response.content)

    def test_anon_user_cant_download_shopcart(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.do_request_and_check_response(
            self.client, exp_response_data, status.HTTP_401_UNAUTHORIZED
        )

    @skip('Это для ручной проверки')
    def test_shopcart_0(self):
        self.check_shopcart_text(self.user, (), 0)

    @skip('Это для ручной проверки')
    def test_shopcart(self):
        self.check_shopcart_text(self.user, self.USER_SHOPPING_CART, 1)

    def check_shopcart_text(self, user, shopcart, file_no):
        self.create_shopcart(user, shopcart)
        cart = ShoppingCart(user)
        with open(f'shopcart_{file_no:03}.txt', 'w') as file:
            file.write(cart.to_text())

    def do_request_and_check_response(
        self, client, exp_response_data, exp_status, **kwargs
    ):
        return super().do_request_and_check_response(
            client, 'get', f'{self.BASE_URL}download_shopping_cart/', None, 
            exp_response_data, exp_status, **kwargs
        )