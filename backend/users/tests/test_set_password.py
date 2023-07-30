from rest_framework import status
from rest_framework.test import APIClient

from .base import UserEndpointTestCase


class SetPasswordTestCase(UserEndpointTestCase):

    CURRENT_PASSWORD = 'ZZaaqq11'
    NEW_PASSWORD = 'XXssww22'

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
        exp_response_data = dict(detail='Учетные данные не были предоставлены.')
        self.do_anon_request_and_check_response(
            self.REQUEST_DATA, exp_response_data, status.HTTP_401_UNAUTHORIZED
        )

    def test_authorized_request_ok(self):
        self.do_auth_request_and_check_response(
            self.REQUEST_DATA, (), status.HTTP_204_NO_CONTENT
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
