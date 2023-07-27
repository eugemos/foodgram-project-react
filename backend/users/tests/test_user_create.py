from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework import status

from .base import UserEndpointTestCase, TEST_HOST, left_extend_str


class UserCreateTestCase(UserEndpointTestCase):
    REQUIRED_FIELDS = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
    )

    MAX_LENGTHS = {
        'email': 254,
        'username': 150,
        'first_name': 150,
        'last_name': 150,
        'password': 150,
    }

    def extend_fields_to_max_length(self, data):
        for key in data:
            if key in self.MAX_LENGTHS:
                data[key] = left_extend_str(data[key], self.MAX_LENGTHS[key])

    def test_create_action_with_correct_params(self):
        # Arrange
        assert self.Model.objects.count() == 0
        request_obj = self.create_test_data(1, password='ZZaaqq11'*10)
        self.extend_fields_to_max_length(request_obj)
        exp_response_obj = self.create_test_data(1, id=1)
        self.extend_fields_to_max_length(exp_response_obj)
        # Act
        self.response = self.client.post(self.BASE_URL, request_obj, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        response_obj = self.response.json()
        self.assertEqual(response_obj, exp_response_obj)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 1)
        instance = self.Model.objects.get(pk=1)
        self.check_object_corresponds_instance(response_obj, instance)
        self.assertTrue(instance.check_password(request_obj['password']))

    def test_create_action_without_required_param(self):
        for param in self.REQUIRED_FIELDS:
            with self.subTest(what=f'Проверка реакции на отсутствие поля {param}'):
                self._test_create_action_without_required_param(param)

    def _test_create_action_without_required_param(self, param_name):
        # Arrange
        assert self.Model.objects.count() == 0
        request_obj = self.create_test_data(1, password='ZZaaqq11')
        del request_obj[param_name]
        exp_response_obj = {param_name: ['Обязательное поле.']}
        # Act
        self.response = self.client.post(self.BASE_URL, request_obj, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = self.response.json()
        self.assertEqual(response_obj, exp_response_obj)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 0)

    def test_create_action_with_too_long_param(self):
        for param, max_length in self.MAX_LENGTHS.items():
            with self.subTest(f'Проверка реакции на слишком длинное значение поля {param}'):
                self._test_create_action_with_too_long_param(param, max_length)

    def _test_create_action_with_too_long_param(self, param_name, limit):
        # Arrange
        assert self.Model.objects.count() == 0
        request_obj = self.create_test_data(1, password='ZZaaqq11')
        param_value = request_obj[param_name]
        param_value = left_extend_str(param_value, limit + 1)
        request_obj[param_name] = param_value
        exp_response_obj = {param_name: [f'Убедитесь, что это значение содержит не более {limit} символов.']}
        # Act
        self.response = self.client.post(self.BASE_URL, request_obj, format='json')
        # Assert on response
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)
        response_obj = self.response.json()
        self.assertEqual(response_obj, exp_response_obj)
        # Assert on DB
        self.assertEqual(self.Model.objects.count(), 0)

