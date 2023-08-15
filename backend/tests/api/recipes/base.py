from base64 import b64encode

from django.conf import settings
from rest_framework import status

from tests.base import (
    TEST_HOST, nrange,
    EndpointTestCase, TestRecipe, TestTag, TestIngredient, TestUser
)


BASE64_PREFIX = 'data:image/png;base64,'
TEST_DATA_ROOT = settings.BASE_DIR / 'tests' / 'data'

class RecipeEndpointTestCase(EndpointTestCase, TestRecipe):
    BASE_URL = '/api/recipes/'
    INPUT_FIELDS = (
        'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
    )
    OUTPUT_FIELDS = (
        'id', 'tags', 'author', 'ingredients', 'is_favorited', 
        'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
    )

    TAG_COUNT = 5
    INGREDIENT_COUNT = 5
    tag_fids = nrange(1, TAG_COUNT)
    ingredient_fids = nrange(1, INGREDIENT_COUNT)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tags = TestTag.create_instances(cls.tag_fids)
        cls.ingredients = TestIngredient.create_instances(cls.ingredient_fids)

    @classmethod
    def ingredient_occurences_iter(cls, fids):
        return (dict(id=fid, amount=fid) for fid in fids)

    @classmethod
    def create_request_data(
        cls, *, fid, tag_fids, ingredient_fids, image_file, **kwargs
    ):
        request_data = cls.create_data(
            fid=fid,
            ingredients=[*cls.ingredient_occurences_iter(ingredient_fids)],
            tags=[*tag_fids],
            image=load_file_as_base64_str(image_file),
        )
        request_data.update(**kwargs)
        assert set(request_data.keys()) == set(cls.INPUT_FIELDS)
        return request_data

    @classmethod
    def create_exp_instance_data(
        cls, *, fid, author, tag_fids, ingredient_fids, **kwargs
    ):
        data = cls.create_data(
            fid=fid,
            author=author,
            ingredients=[*cls.ingredient_occurences_iter(ingredient_fids)],
            tags=[*tag_fids],
        )
        data.update(**kwargs)
        return data

    @classmethod
    def create_exp_response_data(
        cls, instance, *, fid, author_fid, author_id, 
        tag_fids, ingredient_fids, **kwargs
    ):
        exp_response_data = cls.create_data(
            fid=fid,
            id=instance.pk,
            tags=[TestTag.create_data(fid=fid, id=fid) for fid in tag_fids],
            author=TestUser.create_data(
                fid=author_fid, id=author_id, is_subscribed=False
            ),
            ingredients=[
                TestIngredient.create_data(fid=fid, id=fid, amount=fid)
                for fid in ingredient_fids
            ],
            is_favorited=False,
            is_in_shopping_cart=False,
            image=f'{TEST_HOST}{settings.MEDIA_URL}{instance.image.name}'
        )
        exp_response_data.update(**kwargs)
        assert set(exp_response_data.keys()) == set(cls.OUTPUT_FIELDS)
        return exp_response_data


class CheckRequestWithoutRequiredParamFailsMixin:
    def check_request_without_required_param_fails(self, client, field_name, error_message):
        request_data = self.create_request_data()
        del request_data[field_name]
        exp_response_data = {field_name: [error_message]}
        self.check_request_fails(
            client, 
            request_data, 
            exp_response_data, 
            status.HTTP_400_BAD_REQUEST
        )

    def do_checks_request_without_required_param_fails(
        self, client, required_fields, error_messages: dict={}
    ):
        for field in required_fields:
            with self.subTest(what=f'Реакция на отсутствие поля {field}'):
                self.check_request_without_required_param_fails(
                    client, field, 
                    error_messages.get(field, self.FIELD_REQUIRED_ERROR_MESSAGE)
                )


def load_file_as_base64_str(file_name):
        with open(TEST_DATA_ROOT / file_name, 'rb') as f:
            return BASE64_PREFIX + b64encode(f.read()).decode()
