from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status

# from . import utils

DEFAULT_PAGE_SIZE = settings.REST_FRAMEWORK['PAGE_SIZE']
TEST_HOST = 'http://testserver'

class UsersViewsTestCase(APITestCase):
    Model = get_user_model()
    BASE_URL = '/api/users/'

    def create_test_instance(self, data):
        return self.Model.objects.create(**data)

    def check_object_is_dict_with_proper_keys(self, obj, keys):
        self.assertIsInstance(obj, dict)
        self.assertEqual(set(obj.keys()), set(keys))

    def check_object_is_list_of_proper_length(self, obj, length):
        self.assertIsInstance(obj, list)
        self.assertEqual(len(obj), length)

    def check_dict_has_proper_items(self, d, obj=None, **kwargs):
        if obj is not None:
            for key in d:
                with self.subTest(key=key):
                    if hasattr(obj, key):
                        self.assertEqual(d[key], getattr(obj, key))
        
        for key in kwargs:
            with self.subTest(key=key):
                self.assertEqual(d[key], kwargs[key])


class UserListViewTestCase(UsersViewsTestCase):
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

    def create_test_data(self, n):
        return dict(
            email=f'User_{n}@email.to',
            username=f'user_{n}',
            first_name = f'FirstName_{n}',
            last_name = f'LastName_{n}',
            # is_subscribed = f'State_{n}',
        )

    def test_list_action_without_params(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size)
        self._test_list_action(1)

    def test_list_action_without_params_authenticated(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size)
        self.client_user = get_user_model().objects.get(pk=1)
        self.client.force_authenticate(user=self.client_user)
        self._test_list_action(1)

    def test_list_action_without_params_1(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size+1, page_size=page_size)
        self._test_list_action(1)

    def test_list_action_with_params(self):
        self.prepare(instance_count=16, page_size=5)
        for page in range(1, 5):
            with self.subTest(page=page):
                self._test_list_action(page, dict(limit=self.page_size, page=page))

    def prepare(self, *, instance_count, page_size):
        self.client_user = AnonymousUser()
        self.instance_count = instance_count
        self.page_size = page_size
        # self.aux_test_data = {}
        for n in range(instance_count):
            instance = self.create_test_instance(self.create_test_data(n))
            # self.aux_test_data[instance.pk] = dict(is_subscribed=False)


        assert self.Model.objects.count() == instance_count
        self.underfull_page_size = instance_count % page_size
        self.page_count = (
            instance_count // page_size 
            + (self.underfull_page_size > 0)
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
            with self.subTest(i=i):
                obj = data[i]
                instance = self.Model.objects.get(pk=obj['id'])
                self.check_object_is_dict_with_proper_keys(obj, self.OUTPUT_FIELDS)
                self.assertEqual(obj['id'], i+start_id)
                self.check_dict_has_proper_items(
                    obj,
                    instance,
                    # **self.aux_test_data[obj['id']]
                    is_subscribed=self.is_client_subscribed(instance)
                )

    def is_client_subscribed(self, user):
        if self.client_user.is_authenticated:
            return user in self.client_user.subscribed_to.all()

        return False
    