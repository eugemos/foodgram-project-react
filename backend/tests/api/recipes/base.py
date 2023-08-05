from base64 import b64encode

from django.conf import settings

from tests.base import EndpointTestCase, TestRecipe


BASE64_PREFIX = 'data:image/png;base64,'
TEST_DATA_ROOT = settings.BASE_DIR / 'tests' / 'data'

class RecipeEndpointTestCase(EndpointTestCase, TestRecipe):
    BASE_URL = '/api/recipes/'


def load_file_as_base64_str(file_name):
        with open(TEST_DATA_ROOT / file_name, 'rb') as f:
            return BASE64_PREFIX + str(b64encode(f.read()))
