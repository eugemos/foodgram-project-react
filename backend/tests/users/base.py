from tests.base import EndpointTestCase, TestUser


class UserEndpointTestCase(EndpointTestCase, TestUser):
    BASE_URL = '/api/users/'

    @classmethod
    def get_data_iter(cls, iter):
        return (cls.create_data(fid=i) for i in iter)


class AuthEndpointTestCase(EndpointTestCase, TestUser):
    BASE_URL = '/api/auth/token/'
