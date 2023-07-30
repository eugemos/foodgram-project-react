from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .base import AuthEndpointTestCase


class GetTokenTestCase(AuthEndpointTestCase):
    def setUp(self):
        super().setUp()
        self.client_user = self.create_instance(
            self.create_data()
        )
        token = Token.objects.create(user=self.client_user)
        self.auth_client = APIClient()
        self.auth_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_authorized_request_ok(self):
        self.do_auth_request_and_check_response(
            (), status.HTTP_204_NO_CONTENT
        )
        self.assertFalse(
            Token.objects.filter(user=self.client_user).exists()
        )

    def test_anonymous_request_fails(self):
        exp_response_data = dict(
            detail='Учетные данные не были предоставлены.'
        )
        self.do_anon_request_and_check_response(
            exp_response_data, status.HTTP_401_UNAUTHORIZED
        )
        self.assertTrue(
            Token.objects.filter(user=self.client_user).exists()
        )

    def do_anon_request_and_check_response(
        self, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.client, exp_response_data, exp_status
        )

    def do_auth_request_and_check_response(
        self, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.auth_client, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            client, 'post', f'{self.BASE_URL}logout/', 
            None, exp_response_data, exp_status
        )
