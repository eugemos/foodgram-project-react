from rest_framework import status
from rest_framework.test import APIClient

from tests.base import (
    TEST_HOST, DEFAULT_PAGE_SIZE,
    nrange, get_nth_subset,
    TestUser
)
from tests.paginator import TestPaginator
from .base import RecipeEndpointTestCase


class RecipeListTestCase(RecipeEndpointTestCase):

    AUTHOR_COUNT = 3
    author_fids = nrange(1, AUTHOR_COUNT)
    USER_SUBSCRIPTIONS = (2,)
    USER_FAVORITES = (1, 3, 5, 7)
    USER_SHOPPING_CART = (2, 3, 4, 6, 7)

    @classmethod
    def get_author_fid(cls, recipe_fid):
        r = recipe_fid % cls.AUTHOR_COUNT
        return  r if r > 0 else cls.AUTHOR_COUNT

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authors = TestUser.create_instances(cls.author_fids)
        cls.user = TestUser.create_instance('user')
        for author_id in cls.USER_SUBSCRIPTIONS:
            cls.user.subscribe_to(TestUser.Model.objects.get(pk=author_id))

    def setUp(self):
        super().setUp()
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.user)

    def prepare(self, *, 
                instance_count, 
                page_size,
                user_favorites=USER_FAVORITES,
                user_shopping_cart=USER_SHOPPING_CART
    ):
        assert instance_count < 2**self.TAG_COUNT
        assert instance_count < 2**self.INGREDIENT_COUNT
        self.maxDiff = None
        self.instance_count = instance_count
        self.paginator = TestPaginator(
            self.BASE_URL, page_size=page_size, instance_count=instance_count
        )
        for fid in nrange(1, instance_count):
            author = TestUser.Model.objects.get(id=self.get_author_fid(fid))
            tags = get_nth_subset(self.tags, fid)
            ingredients = get_nth_subset(self.ingredients, fid)
            recipe=self.create_recipe(fid, author, tags, ingredients)
            if fid in user_favorites:
                self.user.add_to_favorites(recipe)
            if fid in user_shopping_cart:
                self.user.add_to_shopping_cart(recipe)

        assert self.Model.objects.count() == instance_count

    def test_list_action_without_params(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size)
        self.perform_test(page=1)

    def test_list_action_without_params_1(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size+1, page_size=page_size)
        self.perform_test(page=1)

    def test_list_action_without_params_2(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size-1, page_size=page_size)
        self.perform_test(page=1)

    def test_list_action_with_paginator_params(self):
        page_size = 5
        self.prepare(instance_count=16, page_size=page_size)
        for page in range(1, 5):
            with self.subTest(page=page):
                self.perform_test(
                    page=page,
                    params=dict(limit=page_size, page=page)
                )

    def test_list_action_with_filter_params(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=10, page_size=page_size)
        tests = [
            dict(
                params={},
                anon=nrange(1, page_size),
                auth=nrange(1, page_size),
            ),
            dict(
                params=dict(is_favorited=0, is_in_shopping_cart=0),
                anon=nrange(1, page_size),
                auth=nrange(1, page_size),
            ),
            dict(
                params=dict(is_favorited=1),
                anon=(),
                auth=self.USER_FAVORITES,
            ),
            dict(
                params=dict(is_in_shopping_cart=1),
                anon=(),
                auth=self.USER_SHOPPING_CART,
            ),
            dict(
                params=dict(is_favorited=1, is_in_shopping_cart=1),
                anon=(),
                auth=(3, 7),
            ),
            dict(
                params=dict(author=1),
                anon=(1, 4, 7, 10),
                auth=(1, 4, 7, 10),
            ),
            dict(
                params=dict(author=''), #'a', '0', '20'
                anon=(),
                auth=(),
            ),
            dict(
                params=dict(tags=['slug_003', 'slug_004', 'slug_005', ]),
                anon=(7,),
                auth=(7,),
            ),
            dict(
                params=dict(tags='slug_002', author=2),
                anon=(8,),
                auth=(8,),
            ),
        ]

        for test in tests:
            params = test['params']
            results = test.get('anon', None)
            if results is not None:
                with self.subTest(params=params, user='anon'):
                    self.do_request_and_check_filtered_result(
                        self.client, params, len(results), results
                    )
            results = test.get('auth', None)
            if results is not None:
                with self.subTest(params=params, user='auth'):
                    self.do_request_and_check_filtered_result(
                        self.user_client, params, len(results), results
                    )
        
    def perform_test(
        self, *, page, params=dict(), 
    ):
        with self.subTest(client='anon'):
            self.perform_test_for_anon(page=page, params=params)
        with self.subTest(client='user'):
            self.perform_test_for_user(page=page, params=params)

    def perform_test_for_anon(self, *, page, params):
        self.do_request_and_check_response(
            self.client,
            params,
            self.create_exp_response_data(
                page, params, (), (), ()
            )
        )

    def perform_test_for_user(self, *, page, params):
        self.do_request_and_check_response(
            self.user_client,
            params,
            self.create_exp_response_data(
                page, params, self.USER_SUBSCRIPTIONS, self.USER_FAVORITES,
                self.USER_SHOPPING_CART
            )
        )  

    def create_exp_response_data(
        self, page, params, subscribed, favorites, shopping_cart
    ):
        page_size = self.paginator.actual_page_size(page)
        start_fid = self.paginator.first_item_number(page)
        return dict(
            count=self.instance_count,
            previous=self.paginator.previous_page_link(page, params),
            next=self.paginator.next_page_link(page, params),
            results= [
                super(RecipeListTestCase, self).create_exp_response_data(
                    self.Model.objects.get(id=fid),
                    fid=fid, 
                    author_fid=author_fid, 
                    author_id=author_fid, 
                    tag_fids=get_nth_subset(self.tag_fids, fid),
                    ingredient_fids=get_nth_subset(self.ingredient_fids, fid),
                    author=TestUser.create_data(
                        fid=author_fid, 
                        id=author_fid, 
                        is_subscribed=(author_fid in subscribed)
                    ),
                    is_favorited=(fid in favorites),
                    is_in_shopping_cart=(fid in shopping_cart)
                )
                for fid, author_fid in (
                    (fid, self.get_author_fid(fid)) 
                    for fid in nrange(start_fid, page_size)
                )
            ]          
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

    def do_request_and_check_filtered_result(
        self, client, params, exp_count, exp_results
    ):
        response = client.get(self.BASE_URL, params, format='json', follow=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        response_data = response.json()
        with self.subTest():
            self.assertEqual(exp_count, response_data['count'])
        self.assertEqual(
            set(exp_results),
            {item['id'] for item in response_data['results']}
        )