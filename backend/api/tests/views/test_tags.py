from rest_framework import status

from core.tests.base import EndpointTestCase, EndpointModelMixin


class TagEndpointTestCase(EndpointTestCase, EndpointModelMixin):
    BASE_URL = '/api/tags/'

