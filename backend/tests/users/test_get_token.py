from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .base import AuthEndpointTestCase


class GetTokenTestCase(AuthEndpointTestCase):
    USER_PASSWORD = 'ZZaaqq11'
    EXP_ERROR_RESPONSE_DATA = {
        'non_field_errors': [
            'Невозможно войти с предоставленными учетными данными.'
        ]
    }

    def setUp(self):
        super().setUp()
        self.user = self.create_instance(password=self.USER_PASSWORD)
        self.request_data = dict(
            password=self.USER_PASSWORD,
            email=self.user.email,
        )
        
    def test_normal_request_ok(self):
        self.do_anon_request_and_check_response(
            self.request_data, (), status.HTTP_201_CREATED
        )
        self.assertTrue(Token.objects.filter(user=self.user).exists())
        token = Token.objects.get(user=self.user).key
        exp_response_data = dict(auth_token=token)
        self.assertEqual(exp_response_data, self.response.json())

    def test_with_invalid_password_fails(self):
        self.check_request_with_invalid_param_fails(
            'password',
            'q'+self.USER_PASSWORD,
        )

    def test_with_invalid_email_fails(self):
        self.check_request_with_invalid_param_fails(
            'email',
            'q'+self.user.email,
        )

    def test_without_password_fails(self):
        self.check_request_without_required_param_fails('password')

    def test_without_email_fails(self):
        self.check_request_without_required_param_fails('email')

    def check_request_with_invalid_param_fails(
        self, field_name, field_value
    ):
        request_data = self.request_data.copy()
        request_data[field_name] = field_value
        self.check_request_fails(request_data, self.EXP_ERROR_RESPONSE_DATA)

    def check_request_without_required_param_fails(self, field_name):
        request_data = self.request_data.copy()
        del request_data[field_name]
        self.check_request_fails(request_data, self.EXP_ERROR_RESPONSE_DATA)

    def check_request_fails(self, request_data, exp_response_data):
        self.do_anon_request_and_check_response(
            request_data, exp_response_data, status.HTTP_400_BAD_REQUEST
        )
        self.assertFalse(
            Token.objects.filter(user=self.user).exists()
        )

    def do_anon_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.client, request_data, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, request_data, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}login/',
            request_data, exp_response_data, exp_status
        )
