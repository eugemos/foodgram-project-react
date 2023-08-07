from django.core.files import File 

from tests.base import (
    TestIngredient, TestTag, TestUser
)
from .base import RecipeEndpointTestCase


class RecipeDetailEndpointTestCase(RecipeEndpointTestCase):
    # TAGS_PER_RECIPE = 2
    # INGREDIENTS_PER_RECIPE = 2
    # FIXTURE_RECIPE_COUNT = 2**3
    FIXTURE_TAG_COUNT = 3
    FIXTURE_INGREDIENT_COUNT = 3
    # FIXTURE_AUTHOR_COUNT = 2
    # recipe_ids = range(1, FIXTURE_RECIPE_COUNT+1)
    tag_ids = range(1, FIXTURE_TAG_COUNT+1)
    ingredient_ids = range(1, FIXTURE_INGREDIENT_COUNT+1)
    # author_ids = range(1, FIXTURE_AUTHOR_COUNT+1)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tags = TestTag.create_instances(cls.tag_ids)
        cls.ingredients = TestIngredient.create_instances(cls.ingredient_ids)
        # cls.authors = tuple(TestUser.create_instance(n) for n in cls.author_ids)
        cls.author = TestUser.create_instance('author')
        cls.client_user = TestUser.create_instance(TestUser.create_data(n='client'))
        cls.recipe = cls.create_instance(
            author=cls.author,
            image=File(open('tests/data/test.png'), name=f'recipe.png'),
        )
        cls.recipe.set_tags(cls.tags)
        for ingredient in cls.ingredients:
            cls.recipe.add_ingredient(ingredient, ingredient.pk)

    def test_fixture(self):
        self.assertEqual(self.Model.objects.count(), 1)  
