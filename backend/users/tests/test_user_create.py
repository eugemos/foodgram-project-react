from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework import status

from .base import UserEndpointTestCase, TEST_HOST, left_extend_str, get_model_pk_set


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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.instance = cls.create_instance(
            cls.create_data(password='ZZaaqq11')
        )

    def test_request_with_correct_params_ok(self):
        request_data = self.create_data(n='other', password='ZZaaqq11'*10)
        self.extend_fields_to_max_length(request_data)
        exp_response_data = self.create_data(n='other', id=2)
        self.extend_fields_to_max_length(exp_response_data)
        self.check_create_reqest_ok(request_data, exp_response_data)

    def test_request_without_required_param_fails(self):
        for field in self.REQUIRED_FIELDS:
            with self.subTest(what=f'Проверка реакции на отсутствие поля {field}'):
                self.subtest_request_without_required_param_fails(field)

    def test_request_with_too_long_param_fails(self):
        for field, max_length in self.MAX_LENGTHS.items():
            with self.subTest(f'Проверка реакции на слишком длинное значение поля {field}'):
                self.subtest_request_with_too_long_param_fails(field, max_length)

    def test_request_with_non_unique_username_fails(self):
        self.check_request_with_non_unique_param_fails('username')

    def test_request_with_non_unique_email_fails(self):
        self.check_request_with_non_unique_param_fails('email')

    def test_request_with_non_unique_first_name_ok(self):
        self.check_request_with_non_unique_param_ok('first_name')

    def test_request_with_non_unique_last_name_ok(self):
        self.check_request_with_non_unique_param_ok('last_name')

    def test_request_with_non_unique_password_ok(self):
        self.check_request_with_non_unique_param_ok('password')

    def test_request_with_invalid_email_fails(self):
        self.check_request_with_invalid_param_fails(
            'email', 
            'email.ru', 
            'Введите правильный адрес электронной почты.'
        )

    def test_request_with_invalid_username_fails(self):
        self.check_request_with_invalid_param_fails(
            'username',
            'user%name', 
            'Введите правильное имя пользователя. '
            'Оно может содержать только буквы, цифры и знаки @/./+/-/_.'
        )

    def subtest_request_without_required_param_fails(self, field_name):
        request_data = self.create_data(n='other', password='ZZaaqq11')
        del request_data[field_name]
        exp_response_data = {field_name: ['Обязательное поле.']}
        self.check_create_reqest_fails(request_data, exp_response_data)

    def subtest_request_with_too_long_param_fails(self, field_name, limit):
        sample_data = self.create_data(n='sample', password='ZZaaqq11')
        self.check_request_with_invalid_param_fails(
            field_name,
            left_extend_str(sample_data[field_name], limit + 1),
            f'Убедитесь, что это значение содержит не более {limit} символов.'
        )

    def check_request_with_non_unique_param_fails(self, field_name):
        assert field_name in self.UNIQUE_FIELDS
        self.check_request_with_invalid_param_fails(
            field_name,
            getattr(self.instance, field_name),
            self.UNIQUE_FIELDS[field_name]
        )

    def check_request_with_non_unique_param_ok(self, field_name):
        assert field_name not in self.UNIQUE_FIELDS
        request_data = self.create_data(n='other', password='ZZaaqq22')
        request_data[field_name] = getattr(self.instance, field_name)
        exp_response_data = self.create_data(n='other', id=2)
        if field_name in exp_response_data:
            exp_response_data[field_name] = getattr(self.instance, field_name)

        self.check_create_reqest_ok(request_data, exp_response_data)

    def check_request_with_invalid_param_fails(self, field_name, field_value, error_msg):
        request_data = self.create_data(n='other', password='ZZaaqq22')
        request_data[field_name] = field_value
        exp_response_data = {field_name: [error_msg]}
        self.check_create_reqest_fails(request_data, exp_response_data)

    def check_create_reqest_ok(self, request_data, exp_response_data):
        initial_model_pk_set = get_model_pk_set(self.Model)
        # Act, Assert on response
        response_data = self.do_request_and_check_response(request_data, exp_response_data, status.HTTP_201_CREATED)
        # Assert on DB
        result_model_pk_set = get_model_pk_set(self.Model)
        self.assertTrue(initial_model_pk_set <= result_model_pk_set)
        new_model_pks = tuple(result_model_pk_set - initial_model_pk_set)
        self.assertEqual(len(new_model_pks), 1)
        instance = self.Model.objects.get(pk=new_model_pks[0])
        self.assertEqual(self.get_instance_data(instance), response_data)
        self.assertTrue(instance.check_password(request_data['password']))

    def check_create_reqest_fails(self, request_data, exp_response_data):
        initial_model_pk_set = get_model_pk_set(self.Model)
        # Act, Assert on response
        self.do_request_and_check_response(request_data, exp_response_data, status.HTTP_400_BAD_REQUEST)
        # Assert on DB
        result_model_pk_set = get_model_pk_set(self.Model)
        self.assertEqual(initial_model_pk_set, result_model_pk_set)

    def do_request_and_check_response(self, request_data, exp_response_data, exp_status):
        return super().do_request_and_check_response(
            self.client, 
            'post', 
            self.BASE_URL, 
            request_data, 
            exp_response_data, 
            exp_status
        )

    def extend_fields_to_max_length(self, data):
        for key in data:
            if key in self.MAX_LENGTHS:
                data[key] = left_extend_str(data[key], self.MAX_LENGTHS[key])
