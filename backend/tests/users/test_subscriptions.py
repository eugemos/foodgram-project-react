from rest_framework import status
from rest_framework.test import APIClient

from tests.base import (
    DEFAULT_PAGE_SIZE,
    get_nth_subset, nrange, 
    TagsIngredientsMixin, TestRecipe
)
from tests.paginator import TestPaginator
from .base import UserEndpointTestCase


class UserSubscriptionsTestCase(TagsIngredientsMixin, UserEndpointTestCase):
    RECIPE_COUNT = 30
    recipe_fids = nrange(1, RECIPE_COUNT)

    DEFAULT_SUBSCRIPTIONS = (1, 3, 5, 7, 9)

    @staticmethod
    def create_recipe_data(fid):
        data = TestRecipe.create_data(
            fid=fid,
            id=fid,
            image=TestRecipe.get_image_url(pk=fid)
        )
        del data['text']
        return data

    def prepare(self, *, 
                instance_count, 
                page_size, 
                subscriptions=DEFAULT_SUBSCRIPTIONS
    ):
        def appoint_author(recipe_fid):
            r = recipe_fid % instance_count
            id = r if r > 0 else instance_count
            return  self.Model.objects.get(id=id)

        self.maxDiff = None
        assert self.RECIPE_COUNT % instance_count == 0
        self.instance_count = instance_count
        self.subscriptions = subscriptions
        self.paginator = TestPaginator(
            self.BASE_URL, page_size=page_size, instance_count=instance_count
        )
        author_fids = nrange(1, instance_count)
        self.create_instances(author_fids)
        self.user = self.create_instance('user')
        assert self.Model.objects.count() == instance_count + 1      
        for author in (
            self.Model.objects.get(pk=fid) 
            for fid in author_fids 
            if fid in subscriptions
        ):
            self.user.subscribe_to(author)

        for fid in self.recipe_fids:
            tags = get_nth_subset(self.tags, fid)
            ingredients = get_nth_subset(self.ingredients, fid)
            recipe = TestRecipe.create_instance(fid, appoint_author(fid), tags, ingredients)

    def test_auth_user_can_get_subscriptions_without_params(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size)
        self.perform_test(
            self.create_auth_client(self.user),
            1,
        )

    def test_auth_user_can_get_subscriptions_with_recipes_limit(self):
        page_size = DEFAULT_PAGE_SIZE
        self.prepare(instance_count=page_size, page_size=page_size)
        self.perform_test(
            self.create_auth_client(self.user),
            1,
            params=dict(recipes_limit=1)
        )

    def test_anon_user_cant_get_subscriptions(self):
        self.do_request_and_check_response(
            self.client, None, self.UNAUTHORIZED_ERROR_RESPONSE_DATA,
            exp_status=status.HTTP_401_UNAUTHORIZED
        )

    # def test_list_action_without_params_1(self):
    #     page_size = DEFAULT_PAGE_SIZE
    #     self.prepare(instance_count=page_size+1, page_size=page_size)
    #     self.perform_test(self.client, 1)

    # def test_list_action_without_params_2(self):
    #     page_size = DEFAULT_PAGE_SIZE
    #     self.prepare(instance_count=page_size-1, page_size=page_size)
    #     self.perform_test(self.client, 1)

    # def test_list_action_with_params(self):
    #     page_size = 5
    #     self.prepare(instance_count=16, page_size=page_size)
    #     for page in range(1, 5):
    #         with self.subTest(page=page):
    #             self.perform_test(self.client, page, params=dict(limit=page_size, page=page))

    def perform_test(self, client, page, *, params=dict()):
        self.do_request_and_check_response(
            client,
            params,
            self.create_exp_response_data(page, params)
        )
           
    def create_exp_response_data(self, page, params):
        page_size = self.paginator.actual_page_size(page)
        start_fid = self.paginator.first_item_number(page)
        recipes_limit = params.get('recipes_limit', self.RECIPE_COUNT+1)
        return dict(
            count= len(self.subscriptions),
            previous=self.paginator.previous_page_link(page, params),
            next=self.paginator.next_page_link(page, params),
            results= [
                self.create_data(
                    fid=fid, id=fid, is_subscribed=True,
                    recipes_count=min(
                        self.RECIPE_COUNT // self.instance_count, recipes_limit
                    ),
                    recipes=[
                        self.create_recipe_data(rfid) 
                        for rfid in range(
                            fid, self.RECIPE_COUNT+1, self.instance_count
                        )
                    ][:recipes_limit]
                )
                for fid in self.subscriptions 
            ]          
        )
        
    def do_request_and_check_response(
        self, client, request_data, exp_response_data,
        exp_status=status.HTTP_200_OK
    ):
        return super().do_request_and_check_response(
            client, 'get', f'{self.BASE_URL}subscriptions/', 
            request_data, exp_response_data, exp_status,
            follow=True
        )
    