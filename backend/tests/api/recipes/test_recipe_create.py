import re
import unittest

from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Tag, Ingredient
from tests.base import (
    TEST_HOST, left_extend_str, nrange,
    TestTag, TestIngredient, TestUser
)
from .base import (
    RecipeEndpointTestCase, CheckRequestWithoutRequiredParamFailsMixin,
    load_file_as_base64_str,
)

class RecipeCreateEndpointTestCase(
    CheckRequestWithoutRequiredParamFailsMixin,
    RecipeEndpointTestCase
):
    REQUIRED_FIELDS = (
        'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
    )
    NON_NULL_FIELDS = REQUIRED_FIELDS
    NON_EMPTY_STRING_FIELDS = ('name', 'text')
    MAX_LENGTHS = {'name': 200}
    MIN_VALUES = {'cooking_time': 1}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_user = TestUser.create_instance('client')

    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)
        self.maxDiff = None

    def test_auth_user_can_create_recipe(self):
        for fid in range(1, 3):
            with self.subTest(fid=fid):
                self.subtest_auth_user_can_create_recipe(fid)

    def test_anon_user_cant_create_recipe(self):
        initial_pk_set = self.get_pk_set()
        request_data = self.create_request_data()
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.do_anon_request_and_check_response(
            request_data, exp_response_data, status.HTTP_401_UNAUTHORIZED
        )

    def test_request_with_name_of_max_length_ok(self):
        initial_pk_set = self.get_pk_set()
        request_data = self.create_request_data(name='q'*self.MAX_LENGTHS['name'])
        self.do_auth_request_and_check_response(
            request_data, (), status.HTTP_201_CREATED
        )
        self.check_only_instance_created(initial_pk_set)

    def test_request_without_required_param_fails(self):
        self.do_checks_request_without_required_param_fails(
            self.auth_client, 
            self.REQUIRED_FIELDS,
            {'image': 'Ни одного файла не было отправлено.'}
        )

    def test_request_with_null_param_fails(self):
        for field in self.NON_NULL_FIELDS:
            with self.subTest(field=field):
                self.check_request_with_invalid_param_fails(
                    field, None, self.NULL_FIELD_DISALLOWED_ERROR_MESSAGE
                )

    def test_request_with_empty_ingredients_fails(self):
        self.check_request_with_invalid_param_fails(
            'ingredients', 
            [], 
            self.NULL_LIST_DISALLOWED_ERROR_MESSAGE,
            non_field_error=True
        )

    @unittest.skip('Надо разобраться с сообщением об ошибке')
    def test_request_with_nonexistent_ingredient_fails(self):
        print('\nBEGIN\n')
        request_data = self.create_request_data()
        request_data.update(
            ingredients=[dict(id=self.FIXTURE_INGREDIENT_COUNT+1, amount=1)]
        )
        exp_response_data = {}
        self.check_auth_request_fails(
            request_data, exp_response_data, status.HTTP_404_NOT_FOUND
        )

    def test_request_with_invalid_amount_of_ingredient_fails(self):
        min_amount = 1
        request_data = self.create_request_data()
        request_data.update(
            ingredients=[dict(id=1, amount=min_amount-1)]
        )
        error_message = (
            self.TOO_SMALL_VALUE_ERROR_MESSAGE_TEMPLATE.format(min_amount)
        )
        exp_response_data = {
            'ingredients': [
                {'amount': [error_message]}
            ]
        }
        self.check_auth_request_fails(request_data, exp_response_data)

    @unittest.skip('Надо разобраться с сообщением об ошибке')
    def test_request_with_nonexistent_tag_fails(self):
        print('\nBEGIN\n')
        request_data = self.create_request_data()
        request_data.update(
            tags=[self.FIXTURE_TAG_COUNT + 1]
        )
        exp_response_data = {}
        self.check_auth_request_fails(
            request_data, exp_response_data, status.HTTP_404_NOT_FOUND
        )

    def test_request_with_empty_tags_fails(self):
        self.check_request_with_invalid_param_fails(
            'tags', 
            [], 
            self.NULL_LIST_DISALLOWED_ERROR_MESSAGE
        )

    def test_request_with_empty_string_param_fails(self):
        for field in self.NON_EMPTY_STRING_FIELDS:
            with self.subTest(field=field):
                self.check_request_with_invalid_param_fails(
                    field, '', self.NULL_FIELD_DISALLOWED_ERROR_MESSAGE
                )

    def test_request_with_invalid_image_fails(self):
        self.check_request_with_invalid_param_fails(
            'image', '', 'Загруженный файл не является корректным файлом.'
        )

    def test_request_with_too_long_name_fails(self):
        max_length = self.MAX_LENGTHS['name']
        self.check_request_with_invalid_param_fails(
            'name', 
            'q' * (max_length + 1), 
            self.TOO_LONG_VALUE_ERROR_MESSAGE_TEMPLATE.format(max_length)
        )

    def test_request_with_too_small_cooking_time_fails(self):
        min_value = self.MIN_VALUES['cooking_time']
        self.check_request_with_invalid_param_fails(
            'cooking_time', 
            min_value - 1,
            self.TOO_SMALL_VALUE_ERROR_MESSAGE_TEMPLATE.format(min_value)
        )

    def subtest_auth_user_can_create_recipe(self, fid):
        initial_pk_set = self.get_pk_set()
        request_data = self.create_request_data(fid=fid)
        with self.subTest():
            self.do_auth_request_and_check_response(
                request_data, (), status.HTTP_201_CREATED
            )
        response_data = self.response.json()
        # print(f'\n{response_data}\n')
        # Assert on DB
        instance = self.check_only_instance_created(initial_pk_set)
        exp_instance_data = self.create_exp_instance_data(fid=fid, id = response_data['id'])
        self.assertEqual(exp_instance_data, self.get_instance_data(instance))
        self.assertTrue(re.fullmatch(
            'recipe/recipe(_[0-9a-zA-Z]{7})?.png', instance.image.name
        ))
        # Assert on Response
        exp_response_data = self.create_exp_response_data(instance, fid=fid)
        self.assertEqual(exp_response_data, response_data)

    def check_request_with_invalid_param_fails(
        self, field_name, field_value, error_msg, *, non_field_error=False
    ):
        request_data = self.create_request_data()
        request_data[field_name] = field_value
        exp_response_data = {
            field_name: 
                dict(non_field_errors=[error_msg])
                if non_field_error
                else [error_msg]
        }
        self.check_auth_request_fails(request_data, exp_response_data)

    def check_auth_request_fails(
        self, request_data, exp_response_data, 
        exp_status=status.HTTP_400_BAD_REQUEST
    ):
        self.check_request_fails(
            self.auth_client, request_data, exp_response_data, exp_status
        )

    def check_request_fails(
        self, client, request_data, exp_response_data,
        exp_status
    ):
        initial_pk_set = self.get_pk_set()
        # Act, Assert on response
        self.do_request_and_check_response(
            client, request_data, exp_response_data, exp_status
        )
        # Assert on DB
        result_pk_set = self.get_pk_set()
        self.assertEqual(initial_pk_set, result_pk_set)

    def create_request_data(self, *, fid=1, **kwargs):
        return super().create_request_data(
            fid=fid,
            tag_fids=self.tag_fids, 
            ingredient_fids=self.ingredient_fids,
            image_file='test.png', 
            **kwargs
        )

    def create_exp_instance_data(self, *, fid=1, **kwargs):
        return super().create_exp_instance_data(
            fid=fid, author=self.client_user, tag_fids=self.tag_fids,
            ingredient_fids=self.ingredient_fids, **kwargs
        )
    
    def create_exp_response_data(self, instance, *, fid=1, **kwargs):
        return super().create_exp_response_data(
            instance, fid=fid, author_fid='client', author_id=self.client_user.id, 
            tag_fids=self.tag_fids, ingredient_fids=self.ingredient_fids, **kwargs 
        )

    def do_auth_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        return self.do_request_and_check_response(
            self.auth_client, request_data, exp_response_data, exp_status
        )

    def do_anon_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        return self.do_request_and_check_response(
            self.client, request_data, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, request_data, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', self.BASE_URL, 
            request_data, exp_response_data, exp_status
        )
