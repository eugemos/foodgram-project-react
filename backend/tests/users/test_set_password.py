from rest_framework import status
from rest_framework.test import APIClient

from tests.base import left_extend_str
from .base import UserEndpointTestCase 


class SetPasswordTestCase(UserEndpointTestCase):
    MAX_PASSWORD_LENGTH = 150
    CURRENT_PASSWORD = left_extend_str('ZZaaqq11'*10, MAX_PASSWORD_LENGTH)
    NEW_PASSWORD = left_extend_str('XXssww22'*10, MAX_PASSWORD_LENGTH)

    REQUEST_DATA = dict(
        new_password=NEW_PASSWORD,
        current_password=CURRENT_PASSWORD
    )
       
    def setUp(self):
        super().setUp()
        self.client_user = self.create_instance(
            self.create_data(password=self.CURRENT_PASSWORD)
        )
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)

    def test_anonymous_request_fails(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        self.do_anon_request_and_check_response(
            self.REQUEST_DATA, exp_response_data, status.HTTP_401_UNAUTHORIZED
        )

    def test_authorized_request_ok(self):
        self.do_auth_request_and_check_response(
            self.REQUEST_DATA, (), status.HTTP_204_NO_CONTENT
        )
        self.assertTrue(
            self.client_user.check_password(self.REQUEST_DATA['new_password'])
        )

    def test_request_with_invalid_password_fails(self):
        self.check_request_with_invalid_param_fails(
            'current_password', 
            self.CURRENT_PASSWORD[1:], 
            'Неправильный пароль.'
        )

    def test_request_with_too_long_new_password_fails(self):
        self.check_request_with_invalid_param_fails(
            'new_password', 
            self.NEW_PASSWORD + 'q', 
            'Убедитесь, что это значение содержит не более '
            f'{self.MAX_PASSWORD_LENGTH} символов.'
        )

    def test_request_with_too_weak_new_password_fails(self):
        self.check_request_with_invalid_param_fails(
            'new_password', 
            'q'*8, 
            'Введённый пароль слишком широко распространён.'
        )

    def test_request_without_current_password_fails(self):
        self.check_request_without_required_param_fails('current_password')

    def test_request_without_new_password_fails(self):
        self.check_request_without_required_param_fails('new_password')

    def check_request_with_invalid_param_fails(
        self, field_name, field_value, error_msg
    ):
        request_data = self.REQUEST_DATA.copy()
        request_data[field_name] = field_value
        exp_response_data = {field_name: [error_msg]}
        self.check_request_fails(request_data, exp_response_data)

    def check_request_without_required_param_fails(self, field_name):
        request_data = self.REQUEST_DATA.copy()
        del request_data[field_name]
        exp_response_data = {field_name: ['Обязательное поле.']}
        self.check_request_fails(request_data, exp_response_data)

    def check_request_fails(self, request_data, exp_response_data):
        self.do_auth_request_and_check_response(
            request_data, exp_response_data, status.HTTP_400_BAD_REQUEST
        )
        self.assertTrue(
            self.client_user.check_password(self.CURRENT_PASSWORD)
        )

    def do_anon_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.client, request_data, exp_response_data, exp_status
        )

    def do_auth_request_and_check_response(
        self, request_data, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.auth_client, request_data, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, request_data, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}set_password/', 
            request_data, exp_response_data, exp_status
        )
