from rest_framework import status
from rest_framework.test import APIClient

from .base import UserEndpointTestCase


class UserProfileTestCase(UserEndpointTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_user = cls.create_instance(
            cls.create_data()
        )
       
    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)

    def test_anonymous_request_fails(self):
        exp_response_data = dict(detail='Учетные данные не были предоставлены.')
        self.do_anon_request_and_check_response(
            exp_response_data, status.HTTP_401_UNAUTHORIZED
        )

    def test_authorized_request_ok(self):
        exp_response_data = self.get_instance_data(
            self.client_user, is_subscribed=False
        )
        self.do_auth_request_and_check_response(
            exp_response_data, status.HTTP_200_OK
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
            client, 'get', f'{self.BASE_URL}me/', 
            None, exp_response_data, exp_status
        )
