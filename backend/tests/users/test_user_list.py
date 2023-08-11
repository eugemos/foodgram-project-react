from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from tests.base import TEST_HOST, DEFAULT_PAGE_SIZE, nrange
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
        self.page_size = page_size
        self.create_instances(self.get_data_iter(nrange(1, self.instance_count)))

        assert self.Model.objects.count() == instance_count
        self.underfull_page_size = instance_count % page_size
        self.page_count = (
            instance_count // page_size 
            + (self.underfull_page_size > 0)
        )

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
        self.prepare(instance_count=16, page_size=5)
        for page in range(1, 5):
            with self.subTest(page=page):
                self.perform_test(self.client, page, params=dict(limit=self.page_size, page=page))

    def perform_test(self, client, page, subscribed=(), *, params=dict()):
        self.do_request_and_check_response(
            client,
            params,
            self.create_exp_response_data(page, params, subscribed)
        )
           
    def create_exp_response_data(self, page, params, subscribed):
        page_size = self.page_size if page != self.page_count else self.last_page_size()
        start_fid = (page - 1)*self.page_size + 1
        return dict(
            count=self.instance_count,
            previous=self.previous_page_link(page, params),
            next=self.next_page_link(page, params),
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

    def previous_page_link(self, page, request_params):
        if page <= 1:
            return None

        link = TEST_HOST + self.BASE_URL        
        params = []
        if 'limit' in request_params:
            params.append(f'limit={request_params["limit"]}')

        prev_page = page - 1
        if prev_page > 1:
            params.append(f'page={prev_page}')

        param_str = '&'.join(params)
        return f'{link}?{param_str}' if param_str else link

    def next_page_link(self, page, request_params):
        if page >= self.page_count:
            return None

        link = TEST_HOST + self.BASE_URL        
        params = []
        if 'limit' in request_params:
            params.append(f'limit={request_params["limit"]}')

        next_page = page + 1
        params.append(f'page={next_page}')
        param_str = '&'.join(params)
        return f'{link}?{param_str}'

    def last_page_size(self):
        return (
            self.page_size 
            if self.underfull_page_size == 0
            else self.underfull_page_size
        )
    
    def do_request_and_check_response(
        self, client, request_data, exp_response_data,
        exp_status=status.HTTP_200_OK
    ):
        return super().do_request_and_check_response(
            client, 'get', self.BASE_URL, 
            request_data, exp_response_data, exp_status,
            follow=True
        )
    