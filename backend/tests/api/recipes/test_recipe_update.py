import re
import unittest

from django.core.files import File
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from api.models import IngredientOccurence
from tests.base import (
    TEST_HOST, nrange,
    TestIngredient, TestTag, TestUser
)
from .base import (
    RecipeEndpointTestCase, CheckRequestWithoutRequiredParamFailsMixin,
    load_file_as_base64_str,
)


class RecipeUpdateTestCase(
    CheckRequestWithoutRequiredParamFailsMixin,
    RecipeEndpointTestCase
):
    TAG_COUNT = RecipeEndpointTestCase.TAG_COUNT
    INGREDIENT_COUNT = RecipeEndpointTestCase.INGREDIENT_COUNT
    NEW_TAG_COUNT = TAG_COUNT + 1
    NEW_INGREDIENT_COUNT = INGREDIENT_COUNT + 1
    new_tag_fids = nrange(TAG_COUNT+1, NEW_TAG_COUNT)
    new_ingredient_fids = nrange(INGREDIENT_COUNT+1, NEW_INGREDIENT_COUNT)
    REQUIRED_FIELDS = (
        'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_tags = TestTag.create_instances(cls.new_tag_fids)
        new_ingredients = TestIngredient.create_instances(cls.new_ingredient_fids)
        cls.author = TestUser.create_instance('author')
        cls.user = TestUser.create_instance('user')
        cls.recipe = cls.create_recipe(
            'old', cls.author, cls.tags, cls.ingredients
        )

    def setUp(self):
        super().setUp()
        self.author_client = APIClient()
        self.author_client.force_authenticate(user=self.author)
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)
        self.maxDiff = None
    
    def test_author_can_update_recipe(self):
        initial_pk_set = self.get_pk_set()
        request_data = self.create_request_data(fid='new')
        with self.subTest():
            self.do_request_and_check_response(
                self.author_client, self.recipe.pk, 
                request_data, (), status.HTTP_200_OK
            )
        response_data = self.response.json()
        # print(f'\n{response_data}\n')
        # Assert on DB
        self.assertEqual(initial_pk_set, self.get_pk_set())
        instance = self.Model.objects.get(pk=self.recipe.pk)
        exp_instance_data = self.create_exp_instance_data(fid='new', id=self.recipe.pk)
        self.assertEqual(exp_instance_data, self.get_instance_data(instance))
        self.assertTrue(re.fullmatch(
            'recipe/recipe(_[0-9a-zA-Z]{7})?.png', instance.image.name
        ))
        self.assertEqual(IngredientOccurence.objects.count(), self.NEW_INGREDIENT_COUNT)
        # Assert on Response
        exp_response_data = self.create_exp_response_data(instance, fid='new')
        self.assertEqual(exp_response_data, response_data)

    def test_anon_user_cant_update_recipe(self):
        self.check_request_fails(
            self.client, 
            self.create_request_data(fid='new'), 
            self.UNAUTHORIZED_ERROR_RESPONSE_DATA, 
            status.HTTP_401_UNAUTHORIZED
        )

    def test_non_author_cant_update_recipe(self):
        self.check_request_fails(
            self.user_client, 
            self.create_request_data(fid='new'), 
            self.FORBIDDEN_ERROR_RESPONSE_DATA, 
            status.HTTP_403_FORBIDDEN
        )
        
    def test_request_without_required_param_fails(self):
        self.do_checks_request_without_required_param_fails(
            self.author_client, 
            self.REQUIRED_FIELDS,
            {'image': 'Ни одного файла не было отправлено.'}
        )
        
    def test_request_to_unexistent_recipe_fails(self):
        request_data = self.create_request_data(fid='new')
        exp_response_data = self.PAGE_NOT_FOUND_RESPONSE_DATA
        self.do_request_and_check_response(
            self.author_client, self.recipe.pk+1, 
            request_data, exp_response_data, status.HTTP_404_NOT_FOUND
        )

    def test_request_with_invalid_param_fails(self):
        # При обновлении рецепта используется тот же самый сериализатор,
        # что и при создании. Так как для операции создания рецепта все 
        # возможные ошибочные ситуации уже протестированы, то тестировать
        # тоже самое ещё и при обновлении рецепта является избыточным.
        pass
    
    def check_request_fails(self, client, request_data, exp_response_data, exp_status):
        initial_pk_set = self.get_pk_set()
        exp_instance_data = self.get_instance_data(self.recipe)
        exp_image_name = self.recipe.image.name
        with self.subTest():
            self.do_request_and_check_response(
                client, self.recipe.pk, 
                request_data, exp_response_data, exp_status
            )
        # Assert on DB
        self.assertEqual(initial_pk_set, self.get_pk_set())
        instance = self.Model.objects.get(pk=self.recipe.pk)
        self.assertEqual(exp_instance_data, self.get_instance_data(instance))
        self.assertEqual(exp_image_name, instance.image.name)
        self.assertEqual(IngredientOccurence.objects.count(), self.INGREDIENT_COUNT)

    def create_request_data(self, *, fid='any', **kwargs):
        return super().create_request_data(
            fid=fid,
            tag_fids=self.new_tag_fids, 
            ingredient_fids=self.new_ingredient_fids,
            image_file='new.png', 
            **kwargs
        )

    def create_exp_instance_data(self, *, fid, **kwargs):
        return super().create_exp_instance_data(
            fid=fid, author=self.author, tag_fids=self.new_tag_fids,
            ingredient_fids=self.new_ingredient_fids, **kwargs
        )

    def create_exp_response_data(self, instance, *, fid, **kwargs):
        return super().create_exp_response_data(
            instance, fid=fid, author_fid='author', author_id=self.author.id,
            tag_fids=self.new_tag_fids, 
            ingredient_fids=self.new_ingredient_fids, **kwargs
        )

    def do_request_and_check_response(
        self, client, id, request_data, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'patch', f'{self.BASE_URL}{id}/',
            request_data, exp_response_data, exp_status
        )
