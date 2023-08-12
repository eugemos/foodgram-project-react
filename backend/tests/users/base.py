from tests.base import EndpointTestCase, TestUser


class UserEndpointTestCase(EndpointTestCase, TestUser):
    BASE_URL = '/api/users/'


class AuthEndpointTestCase(EndpointTestCase, TestUser):
    BASE_URL = '/api/auth/token/'
