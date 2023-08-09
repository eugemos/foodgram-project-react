from base64 import b64encode

from django.conf import settings
from django.core.files import File

from tests.base import EndpointTestCase, TestRecipe


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


def load_file_as_base64_str(file_name):
        with open(TEST_DATA_ROOT / file_name, 'rb') as f:
            return BASE64_PREFIX + b64encode(f.read()).decode()
