import re

from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Tag, Ingredient
from tests.base import (
    TEST_HOST,
    TestTag, TestIngredient, TestUser
)
from .base import (
    RecipeEndpointTestCase,
    load_file_as_base64_str,
)

INPUT_FIELDS = (
    'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
)
OUTPUT_FIELDS = (
    'id', 'tags', 'author', 'ingredients', 'is_favorited', 
    'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
)

class RecipeCreateEndpointTestCase(RecipeEndpointTestCase):
    FIXTURE_TAG_COUNT = 3
    FIXTURE_INGREDIENT_COUNT = 3
    tag_ids = range(1, FIXTURE_TAG_COUNT+1)
    ingredient_ids = range(1, FIXTURE_INGREDIENT_COUNT+1)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestTag.create_instances(cls.tag_ids)
        TestIngredient.create_instances(cls.ingredient_ids)
        cls.client_user = TestUser.create_instance(TestUser.create_data(n='client'))

    @classmethod
    def ingredient_occurences(cls):
        return (dict(id=i, amount=i) for i in cls.ingredient_ids)

    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)
        self.maxDiff = None

    def test_auth_user_can_create_recipe(self):
        for n in range(1, 3):
            with self.subTest(n=n):
                self.do_test_auth_user_can_create_recipe(n)

    def do_test_auth_user_can_create_recipe(self, n):
        initial_pk_set = self.get_pk_set()
        request_data = self.create_request_data(n=n)
        with self.subTest():
            self.do_auth_request_and_check_response(
                request_data, (), status.HTTP_201_CREATED
            )
        response_data = self.response.json()
        # print(f'\n{response_data}\n')
        # Assert on DB
        instance = self.check_only_instance_created(initial_pk_set)
        exp_instance_data = self.create_exp_instance_data(n=n, id = response_data['id'])
        self.assertEqual(exp_instance_data, self.get_instance_data(instance))
        self.assertTrue(re.fullmatch(
            'recipe/recipe(_[0-9a-zA-Z]{7})?.png', instance.image.name
        ))
        # Assert on Response
        exp_response_data = self.create_exp_response_data(instance, n=n)
        self.assertEqual(exp_response_data, response_data)

    def create_request_data(self, *, n=1, **kwargs):
        request_data = self.create_data(
            n=n,
            ingredients = [*self.ingredient_occurences()],
            tags = [*self.tag_ids],
            image = load_file_as_base64_str('test.png'),
            **kwargs
        )
        assert set(request_data.keys()) == set(INPUT_FIELDS)
        return request_data

    def create_exp_instance_data(self, *, n=1, **kwargs):
        return self.create_data(
            n=n,
            author = self.client_user,
            ingredient_occurences = [*self.ingredient_occurences()],
            tag_ids = [*self.tag_ids],
            **kwargs
        )
    
    def create_exp_response_data(self, instance, *, n=1, **kwargs):
        exp_response_data = self.create_data(
            n=n,
            id = instance.pk,
            tags = [TestTag.get_instance_data(Tag.objects.get(id=i)) for i in self.tag_ids],
            author = TestUser.get_instance_data(self.client_user, is_subscribed=False),
            ingredients = [
                TestIngredient.get_instance_data(
                    Ingredient.objects.get(id=i),
                    amount=i
                )
                for i in self.ingredient_ids
            ],
            is_favorited=False,
            is_in_shopping_cart=False,
            image=f'{TEST_HOST}{settings.MEDIA_URL}{instance.image.name}'
        )
        assert set(exp_response_data.keys()) == set(OUTPUT_FIELDS)
        return exp_response_data


    def do_auth_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        return self.do_request_and_check_response(
            self.auth_client, request_data, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, request_data, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', self.BASE_URL, 
            request_data, exp_response_data, exp_status
        )