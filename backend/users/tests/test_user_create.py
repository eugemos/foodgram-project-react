from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework import status

from .base import UserEndpointTestCase, TEST_HOST, left_extend_str


class UserCreateTestCase(UserEndpointTestCase):
    INPUT_FIELDS = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )

    REQUIRED_FIELDS = INPUT_FIELDS

    UNIQUE_FIELDS = {
        'email': 'Пользователь с таким email уже существует.',
        'username': 'Пользователь с таким именем уже существует.',       
    }

    MAX_LENGTHS = {
        'email': 254,
        'username': 150,
        'first_name': 150,
        'last_name': 150,
        'password': 150,
    }

    def test_request_with_correct_params_ok(self):
        # Arrange
        assert self.Model.objects.count() == 0
        request_data = self.create_test_data(1, password='ZZaaqq11'*10)
        self.extend_fields_to_max_length(request_data)
        exp_response_data = self.create_test_data(1, id=1)
        self.extend_fields_to_max_length(exp_response_data)
        # Act
        self.response = self.client.post(self.BASE_URL, request_data, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 1)
        instance = self.Model.objects.get(pk=1)
        self.check_instance(instance, response_data,)
        self.assertTrue(instance.check_password(request_data['password']))

    def test_request_without_required_param_fails(self):
        for param in self.REQUIRED_FIELDS:
            with self.subTest(what=f'Проверка реакции на отсутствие поля {param}'):
                self.subtest_request_without_required_param_fails(param)

    def subtest_request_without_required_param_fails(self, param_name):
        # Arrange
        assert self.Model.objects.count() == 0
        request_data = self.create_test_data(1, password='ZZaaqq11')
        del request_data[param_name]
        exp_response_data = {param_name: ['Обязательное поле.']}
        # Act
        self.response = self.client.post(self.BASE_URL, request_data, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 0)

    def test_request_with_too_long_param_fails(self):
        for param, max_length in self.MAX_LENGTHS.items():
            with self.subTest(f'Проверка реакции на слишком длинное значение поля {param}'):
                self.subtest_request_with_too_long_param_fails(param, max_length)

    def subtest_request_with_too_long_param_fails(self, param_name, limit):
        # Arrange
        assert self.Model.objects.count() == 0
        request_data = self.create_test_data(1, password='ZZaaqq11')
        param_value = request_data[param_name]
        param_value = left_extend_str(param_value, limit + 1)
        request_data[param_name] = param_value
        exp_response_data = {param_name: [f'Убедитесь, что это значение содержит не более {limit} символов.']}
        # Act
        self.response = self.client.post(self.BASE_URL, request_data, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 0)

    def test_request_with_non_unique_param_fails(self):
        fixture_data = self.create_test_data(1, password='ZZaaqq11')
        self.create_test_instance(fixture_data)
        for field in (f for f in self.INPUT_FIELDS if f in self.UNIQUE_FIELDS):
            with self.subTest(field=field):
                self.subtest_request_with_non_unique_param_fails(
                    field, fixture_data[field])

    def subtest_request_with_non_unique_param_fails(self, field_name, field_value):
        assert self.Model.objects.count() == 1
        request_data = self.create_test_data(2, password='ZZaaqq22')
        request_data[field_name] = field_value
        exp_response_data = {field_name: [self.UNIQUE_FIELDS[field_name]]}
        # Act
        self.response = self.client.post(self.BASE_URL, request_data, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 1)

    def test_request_with_non_unique_param_ok(self):
        fixture_data = self.create_test_data(1, password='ZZaaqq11')
        self.create_test_instance(fixture_data)
        assert self.Model.objects.count() == 1
        for n, field in enumerate(
            (f for f in self.INPUT_FIELDS if f not in self.UNIQUE_FIELDS),
            2
        ):
            with self.subTest(field=field):
                self.subtest_request_with_non_unique_param_ok(
                    field, fixture_data[field], n)

    def subtest_request_with_non_unique_param_ok(self, field_name, field_value, n):
        assert self.Model.objects.count() == n - 1
        request_data = self.create_test_data(n, password='ZZaaqq11'+str(n))
        request_data[field_name] = field_value
        exp_response_data = self.create_test_data(n, id=n)
        if field_name in exp_response_data:
            exp_response_data[field_name] = field_value       
        # Act
        self.response = self.client.post(self.BASE_URL, request_data, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        response_data = self.response.json()
        self.assertEqual(response_data, exp_response_data)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), n)
        instance = self.Model.objects.get(pk=n)
        self.check_instance(instance, response_data,)
        self.assertTrue(instance.check_password(request_data['password']))

    def extend_fields_to_max_length(self, data):
        for key in data:
            if key in self.MAX_LENGTHS:
                data[key] = left_extend_str(data[key], self.MAX_LENGTHS[key])
