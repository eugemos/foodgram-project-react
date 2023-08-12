from rest_framework import status
from rest_framework.test import APIClient

from tests.base import DEFAULT_PAGE_SIZE, nrange
from tests.paginator import TestPaginator
from .base import UserEndpointTestCase


class UserListTestCase(UserEndpointTestCase):

    DEFAULT_SUBSCRIPTIONS = {1: (2, DEFAULT_PAGE_SIZE-1)}

    def prepare(self, *, 
                instance_count, 
                page_size, 
                subscriptions=DEFAULT_SUBSCRIPTIONS
    ):
        self.maxDiff = None
        self.instance_count = instance_count
        self.paginator = TestPaginator(
            self.BASE_URL, page_size=page_size, instance_count=instance_count
        )
        self.create_instances(nrange(1, instance_count))
        assert self.Model.objects.count() == instance_count       
        for user in (self.Model.objects.get(pk=pk) for pk in subscriptions):
            user.set_subscriptions(
                self.Model.objects.get(pk=pk) for pk in subscriptions[user.pk]
            )

    def test_list_action_without_params(self):
        page_size = DEFAULT_PAGE_SIZE
        subscriptions = self.DEFAULT_SUBSCRIPTIONS
        self.prepare(instance_count=page_size, page_size=page_size, subscriptions=subscriptions)
        for client_id in (0, 1, 2):
            with self.subTest(client_id=client_id):
                self.perform_test(
                    self.create_client(client_id),
                    1,
                    subscriptions.get(client_id, ())
                )

    def test_list_action_without_params_1(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size+1, page_size=page_size)
        self.perform_test(self.client, 1)

    def test_list_action_without_params_2(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size-1, page_size=page_size)
        self.perform_test(self.client, 1)

    def test_list_action_with_params(self):
        page_size = 5
        self.prepare(instance_count=16, page_size=page_size)
        for page in range(1, 5):
            with self.subTest(page=page):
                self.perform_test(self.client, page, params=dict(limit=page_size, page=page))

    def perform_test(self, client, page, subscribed=(), *, params=dict()):
        self.do_request_and_check_response(
            client,
            params,
            self.create_exp_response_data(page, params, subscribed)
        )
           
    def create_exp_response_data(self, page, params, subscribed):
        page_size = self.paginator.actual_page_size(page)
        start_fid = self.paginator.first_item_number(page)
        return dict(
            count=self.instance_count,
            previous=self.paginator.previous_page_link(page, params),
            next=self.paginator.next_page_link(page, params),
            results= [
                self.create_data(fid=fid, id=fid, is_subscribed=(fid in subscribed))
                for fid in nrange(start_fid, page_size)
            ]          
        )

    def create_client(self, user_id):
        client = APIClient()
        if user_id > 0:
            client_user = self.Model.objects.get(pk=user_id)
            client.force_authenticate(user=client_user)

        return client

    def do_request_and_check_response(
        self, client, request_data, exp_response_data,
        exp_status=status.HTTP_200_OK
    ):
        return super().do_request_and_check_response(
            client, 'get', self.BASE_URL, 
            request_data, exp_response_data, exp_status,
            follow=True
        )
    