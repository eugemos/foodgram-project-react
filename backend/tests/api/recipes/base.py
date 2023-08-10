from base64 import b64encode

from django.conf import settings
from django.core.files import File

from tests.base import (
    TEST_HOST,
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

    @classmethod
    def ingredient_occurences_iter(cls, fids):
        return (dict(id=fid, amount=fid) for fid in fids)

    @classmethod
    def create_recipe(
        cls, fid, author, tags, ingredients, image='test.png'
    ):
        recipe = cls.create_instance(
            fid,
            author=author,
            image=File(open(f'tests/data/{image}'), name='recipe.png'),
        )
        recipe.set_tags(tags)
        for ingredient in ingredients:
            recipe.add_ingredient(ingredient, ingredient.pk)

        return recipe

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


def load_file_as_base64_str(file_name):
        with open(TEST_DATA_ROOT / file_name, 'rb') as f:
            return BASE64_PREFIX + b64encode(f.read()).decode()
