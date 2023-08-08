from tests.base import EndpointTestCase, TestUser


class UserEndpointTestCase(EndpointTestCase, TestUser):
    BASE_URL = '/api/users/'

    @classmethod
    def get_data_iter(cls, iter):
        return (cls.create_data(fid=i) for i in iter)

    def check_data_is_dict_with_proper_keys(self, data, keys):
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data.keys()), set(keys))

    def check_data_is_list_of_proper_length(self, data, length):
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), length)

    def check_data_is_dict_with_proper_items(self, data, instance=None, **kwargs):
        if instance is not None:
            for key in data:
                with self.subTest(key=key):
                    if hasattr(instance, key):
                        self.assertEqual(data[key], getattr(instance, key))
        
        for key in kwargs:
            with self.subTest(key=key):
                self.assertEqual(data[key], kwargs[key])


class AuthEndpointTestCase(EndpointTestCase, TestUser):
    BASE_URL = '/api/auth/token/'
