from django.core.files import File 

from tests.base import (
    TestIngredient, TestTag, TestUser
)
from .base import RecipeEndpointTestCase


class RecipeDetailEndpointTestCase(RecipeEndpointTestCase):
    TAGS_PER_RECIPE = 2
    INGREDIENTS_PER_RECIPE = 2
    FIXTURE_RECIPE_COUNT = 2**3
    FIXTURE_TAG_COUNT = FIXTURE_RECIPE_COUNT + TAGS_PER_RECIPE
    FIXTURE_INGREDIENT_COUNT = FIXTURE_RECIPE_COUNT + INGREDIENTS_PER_RECIPE
    FIXTURE_AUTHOR_COUNT = 2
    recipe_ids = range(1, FIXTURE_RECIPE_COUNT+1)
    tag_ids = range(1, FIXTURE_TAG_COUNT+1)
    ingredient_ids = range(1, FIXTURE_INGREDIENT_COUNT+1)
    author_ids = range(1, FIXTURE_AUTHOR_COUNT+1)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestTag.create_instances(cls.tag_ids)
        TestIngredient.create_instances(cls.ingredient_ids)
        # cls.authors = tuple(TestUser.create_instance(n) for n in cls.author_ids)
        cls.authors = TestUser.create_instances(cls.author_ids)
        cls.client_user = TestUser.create_instance(TestUser.create_data(n='client'))
        recipes = cls.create_instances(
            cls.create_data(
                n=n,
                author=cls.authors[n%2],
                image=File(open('tests/data/test.png'), name=f'recipe_{n}.png'),
            )
            for n in cls.recipe_ids
        )
        # for recipe in recipes:


    def test_fixture(self):
        self.assertEqual(self.Model.objects.count(), self.FIXTURE_RECIPE_COUNT)  
