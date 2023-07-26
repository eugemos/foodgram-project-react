from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework import status

from .base import UserEndpointTestCase, TEST_HOST

DEFAULT_PAGE_SIZE = settings.REST_FRAMEWORK['PAGE_SIZE']


class UserListTestCase(UserEndpointTestCase):
    OUTPUT_FIELDS = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'is_subscribed', 
    )

    OUTPUT_PAGINATOR_FIELDS = (
        'count',
        'next',
        'previous',
        'results',
    )

    DEFAULT_SUBSCRIPTIONS = {1: (2,)}

    def create_test_data(self, n):
        return dict(
            email=f'User_{n}@email.to',
            username=f'user_{n}',
            first_name = f'FirstName_{n}',
            last_name = f'LastName_{n}',
        )

    def test_list_action_without_params(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size)
        self._test_list_action(1)

    def test_list_action_without_params_authenticated(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size, client_user_id=1, subscriptions={1: (2,4,6)})
        self._test_list_action(1)

    def test_list_action_without_params_1(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size+1, page_size=page_size)
        self._test_list_action(1)

    def test_list_action_without_params_2(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size-1, page_size=page_size)
        self._test_list_action(1)

    def test_list_action_with_params(self):
        self.prepare(instance_count=16, page_size=5)
        for page in range(1, 5):
            with self.subTest(page=page):
                self._test_list_action(page, dict(limit=self.page_size, page=page))

    def prepare(self, *, 
                instance_count, 
                page_size, 
                client_user_id=None, 
                subscriptions=DEFAULT_SUBSCRIPTIONS):
        self.client_user = AnonymousUser()
        self.instance_count = instance_count
        self.page_size = page_size
        for n in range(instance_count):
            instance = self.create_test_instance(self.create_test_data(n))

        assert self.Model.objects.count() == instance_count
        self.underfull_page_size = instance_count % page_size
        self.page_count = (
            instance_count // page_size 
            + (self.underfull_page_size > 0)
        )
        if client_user_id:
            self.client_user = self.Model.objects.get(pk=client_user_id)
            self.client.force_authenticate(user=self.client_user)
           
        for user in (self.Model.objects.get(pk=pk) for pk in subscriptions):
            user.set_subscriptions(
                self.Model.objects.get(pk=pk) for pk in subscriptions[user.pk]
            )
            

    def last_page_size(self):
        return (
            self.page_size 
            if self.underfull_page_size == 0
            else self.underfull_page_size
        )

    def _test_list_action(self, page, params=dict()):
        self.response = self.client.get(self.BASE_URL, params, format='json', follow=True)
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.check_paginator_output(
            count=self.instance_count,
            previous=self.previous_page_link(page, params),
            next=self.next_page_link(page, params),
        )       
        self.check_object_list(
            self.page_size if page != self.page_count else self.last_page_size(),
            (page - 1)*self.page_size + 1
        )
    
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


    def check_paginator_output(self, **kwargs):
        data = self.response.json()
        self.check_object_is_dict_with_proper_keys(data, self.OUTPUT_PAGINATOR_FIELDS)
        self.check_dict_has_proper_items(data, **kwargs)

    def check_object_list(self, page_size, start_id):
        data = self.response.json()['results']
        self.check_object_is_list_of_proper_length(data, page_size)
        for i in range(page_size):
            obj = data[i]
            pk = obj['id']
            instance = self.Model.objects.get(pk=pk)
            with self.subTest(what=f'Проверка {i}-го элемента страницы (pk={pk})'):               
                self.check_object_is_dict_with_proper_keys(obj, self.OUTPUT_FIELDS)
                self.assertEqual(pk, i+start_id)
                self.check_dict_has_proper_items(
                    obj,
                    instance,
                    is_subscribed=self.is_client_subscribed(instance)
                )

    def is_client_subscribed(self, user):
        return (self.client_user.is_authenticated 
                and self.client_user.is_subscribed_to(user))
    