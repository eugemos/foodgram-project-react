from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status

# from . import utils

DEFAULT_PAGE_SIZE = settings.REST_FRAMEWORK['PAGE_SIZE']


class UsersViewsTestCase(APITestCase):
    Model = get_user_model()
    BASE_URL = '/api/users'

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
        # 'is_subscribed', 
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
        self.instance_count = instance_count
        self.page_size = page_size
        for n in range(instance_count):
            self.create_test_instance(self.create_test_data(n))

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
        response = self.client.get(self.BASE_URL, params, format='json', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        kwargs = dict(count=self.instance_count)
        
        if page == 1:
            kwargs.update(previous=None)
        if page == self.page_count:
            kwargs.update(next=None)

        self.check_paginator_output(data, **kwargs)       
        self.check_object_list(
            data['results'],
            self.page_size if page != self.page_count else self.last_page_size(),
            (page - 1)*self.page_size + 1
        )
    
    def get_previous_page_link(self):
        pass


    def check_paginator_output(self, data, **kwargs):
        self.check_object_is_dict_with_proper_keys(data, self.OUTPUT_PAGINATOR_FIELDS)
        self.check_dict_has_proper_items(data, **kwargs)

    def check_object_list(self, data, page_size, start_id):
        self.check_object_is_list_of_proper_length(data, page_size)
        for i in range(page_size):
            with self.subTest(i=i):
                obj = data[i]
                self.check_object_is_dict_with_proper_keys(obj, self.OUTPUT_FIELDS)
                self.assertEqual(obj['id'], i+start_id)
                self.check_dict_has_proper_items(obj, self.Model.objects.get(pk=obj['id']))
    