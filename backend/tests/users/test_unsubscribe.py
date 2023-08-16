from rest_framework import status

from .base import UserEndpointTestCase 


class UserUnsubscribeTestCase(UserEndpointTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_instance('user')
        cls.author = cls.create_instance('author')
        cls.author_other = cls.create_instance('other')
        cls.user.subscribe_to(cls.author)

    def setUp(self):
        super().setUp()
        self.user_client = self.create_auth_client(self.user)

    def test_auth_user_can_unsubscribe_from_author(self):
        self.do_request_and_check_response(
            self.user_client, self.author.pk, 
            status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(self.user.subscribed_to.count(), 0)
        self.assertFalse(self.user.is_subscribed_to(self.author))

    def test_auth_user_cant_subscribe_from_author_which_not_subscribed_to(self):
        self.check_request_fails(
            self.user_client, self.author_other.pk,
            dict(errors='Вы не подписаны на этого автора.'), 
            status.HTTP_400_BAD_REQUEST
        )

    def test_anon_user_cant_unsubscribe_from_author(self):
        self.check_request_fails(
            self.client, self.author.pk, self.UNAUTHORIZED_ERROR_RESPONSE_DATA, 
            status.HTTP_401_UNAUTHORIZED
        )

    def test_request_to_unexistent_author_fails(self):
        self.check_request_fails(
            self.user_client, 10, self.PAGE_NOT_FOUND_RESPONSE_DATA, 
            status.HTTP_404_NOT_FOUND
        )

    def check_request_fails(self, client, id, exp_response_data, exp_status):
        self.do_request_and_check_response(
            client, id, exp_status
        )
        self.assertEqual(self.user.subscribed_to.count(), 1)
        self.assertTrue(self.user.is_subscribed_to(self.author))

    def do_request_and_check_response(
        self, client, id, exp_status, **kwargs
    ):
        return super().do_request_and_check_response(
            client, 'delete', f'{self.BASE_URL}{id}/subscribe/', None,
            (), exp_status, **kwargs
        )
