from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APIClient

from .base import UserEndpointTestCase 


class UserProfileTestCase(UserEndpointTestCase):
    CLIENT_USER_ID = 1
    SAMPLE_USER_ID = 2
    UNEXISTENT_USER_ID = 100

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_user = cls.create_instance(
            cls.create_data(n='client', id=cls.CLIENT_USER_ID)
        )
        cls.sample_user = cls.create_instance(
            cls.create_data(n='sample', id=cls.SAMPLE_USER_ID)
        )
        cls.client_user.subscribe_to(cls.sample_user)
       
    def setUp(self):
        super().setUp()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.client_user)

    def test_request_to_unexistent_user_fails(self):
        exp_response_data = dict(detail='Страница не найдена.')
        self.do_auth_request_and_check_response(
            self.UNEXISTENT_USER_ID,
            exp_response_data,
            status.HTTP_404_NOT_FOUND
        )

    def test_anonymous_request_fails(self):
        exp_response_data = self.UNAUTHORIZED_ERROR_RESPONSE_DATA
        for id in (self.client_user.id, self.UNEXISTENT_USER_ID):
            with self.subTest(id=id):
                self.do_anon_request_and_check_response(
                    id, exp_response_data, status.HTTP_401_UNAUTHORIZED
                )

    def test_authorized_request_ok(self):
        for instance in (self.client_user, self.sample_user):
            with self.subTest(id=instance.id):
                exp_response_data = self.create_exp_response_data(instance)
                self.do_auth_request_and_check_response(
                    instance.id, exp_response_data, status.HTTP_200_OK
                )


    def do_anon_request_and_check_response(
        self, id, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.client, id, exp_response_data, exp_status
        )

    def do_auth_request_and_check_response(
        self, id, exp_response_data, exp_status
    ):
        self.do_request_and_check_response(
            self.auth_client, id, exp_response_data, exp_status
        )

    def do_request_and_check_response(
        self, client, id, exp_response_data, exp_status
    ):
        super().do_request_and_check_response(
            client, 'get', f'{self.BASE_URL}{id}/', 
            None, exp_response_data, exp_status
        )

    def create_exp_response_data(self, instance):
        return self.get_instance_data(
            instance,
            is_subscribed=self.client_user.is_subscribed_to(instance)
        )
