from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Tag, Ingredient, Recipe


TEST_HOST = 'http://testserver'
DEFAULT_PAGE_SIZE = settings.REST_FRAMEWORK['PAGE_SIZE']


class EndpointTestCase(APITestCase):
    FIELD_REQUIRED_ERROR_MESSAGE = 'Обязательное поле.'
    NULL_FIELD_DISALLOWED_ERROR_MESSAGE = 'Это поле не может быть пустым.'
    NULL_LIST_DISALLOWED_ERROR_MESSAGE = 'Этот список не может быть пустым.'
    TOO_WIDESPREAD_PASSWORD_ERROR_MESSAGE = (
        'Введённый пароль слишком широко распространён.'
    )
    TOO_LONG_VALUE_ERROR_MESSAGE_TEMPLATE = (
        'Убедитесь, что это значение содержит не более {} символов.'
    )
    TOO_SMALL_VALUE_ERROR_MESSAGE_TEMPLATE = (
        'Убедитесь, что это значение больше либо равно {}.'
    )
    UNAUTHORIZED_ERROR_MESSAGE = 'Учетные данные не были предоставлены.'
    FORBIDDEN_ERROR_MESSAGE = 'У вас недостаточно прав для выполнения данного действия.'
    PAGE_NOT_FOUND_ERROR_MESSAGE = 'Страница не найдена.'
    UNAUTHORIZED_ERROR_RESPONSE_DATA = dict(detail=UNAUTHORIZED_ERROR_MESSAGE)
    FORBIDDEN_ERROR_RESPONSE_DATA = dict(detail=FORBIDDEN_ERROR_MESSAGE)
    PAGE_NOT_FOUND_RESPONSE_DATA = dict(detail=PAGE_NOT_FOUND_ERROR_MESSAGE)

    def do_request_and_check_response(
        self, client, method, url, request_data, 
        exp_response_data, exp_status, **kwargs
    ):
        func = getattr(client, method)
        self.response = func(url, request_data, format='json', **kwargs)
        with self.subTest():
            self.assertEqual(exp_status, self.response.status_code)
        
        if exp_response_data == ():
            return None

        # print(f'\n{self.response.content}\n')
        response_data = self.response.json()
        with self.subTest():
            self.assertEqual(exp_response_data, response_data)
        return response_data        


class TestSimpleListMixin:
    
    def test_anon_request_ok(self):
        INSTANCE_COUNT = 3
        self.create_instances(range(1, INSTANCE_COUNT+1))
        exp_response_data = [
            self.get_instance_data(instance) 
            for instance in self.Model.objects.all()
        ]
        self.do_anon_request_and_check_response(
            exp_response_data, status.HTTP_200_OK
        )
        
    def test_anon_request_ok_with_empty_db(self):
        self.do_anon_request_and_check_response([], status.HTTP_200_OK)

    def do_anon_request_and_check_response(
        self, exp_response_data, exp_status, *, request_data=None
    ):
        return super().do_request_and_check_response(
            self.client, 'get', self.BASE_URL, 
            request_data, exp_response_data, exp_status
        )


class TestSimpleDetailMixin:
    INSTANCE_COUNT = 3

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_instances(range(1, cls.INSTANCE_COUNT + 1))

    def test_anon_request_to_existent_tag_ok(self):
        for id in(1, (1 + self.INSTANCE_COUNT) // 2, self.INSTANCE_COUNT):
            with self.subTest(id=id):
                exp_response_data = self.get_instance_data(
                    self.Model.objects.get(id=id)
                )
                self.do_anon_request_and_check_response(
                    id, exp_response_data, status.HTTP_200_OK
                )

    def test_anon_request_to_unexistent_tag_fails(self):
        for id in (0, self.INSTANCE_COUNT + 1):
            with self.subTest(id=id):
                exp_response_data = self.PAGE_NOT_FOUND_RESPONSE_DATA
                self.do_anon_request_and_check_response(
                    id, exp_response_data, status.HTTP_404_NOT_FOUND
                )

    def do_anon_request_and_check_response(
        self, id, exp_response_data, exp_status
    ):
        return super().do_request_and_check_response(
            self.client, 'get', f'{self.BASE_URL}{id}/', 
            None, exp_response_data, exp_status
        )    


class TestModel:
    @classmethod
    def get_instance_data(cls, instance, **kwargs):
        data = {
            field_name: getattr(instance, field_name)
            for field_name in cls.INSTANCE_FIELDS
        }
        data.update(**kwargs)
        return data

    @classmethod
    def do_create_instance(cls, data):
        return cls.Model.objects.create(**data)

    @classmethod
    def create_instance(cls, data=None, **kwargs):
        if not isinstance(data, dict):
            if data is None:
                data = cls.create_data()
            else:
                data = cls.create_data(fid=data)

        data.update(**kwargs)
        return cls.do_create_instance(data)

    @classmethod
    def create_instances(cls, data_seq):
        return tuple(cls.create_instance(data) for data in data_seq)

    @classmethod
    def get_pk_set(cls):
        return set(instance.pk for instance in cls.Model.objects.all())

    def check_only_instance_created(self, initial_pk_set):
        result_pk_set = self.get_pk_set()
        self.assertTrue(initial_pk_set <= result_pk_set)
        new_pks = tuple(result_pk_set - initial_pk_set)
        self.assertEqual(len(new_pks), 1)
        return self.Model.objects.get(pk=new_pks[0])


class TestUser(TestModel):
    Model = get_user_model()
    INSTANCE_FIELDS = (
        'id', 'email', 'username', 'first_name', 'last_name'
    )

    @classmethod
    def do_create_instance(cls, data):
        return cls.Model.objects.create_user(**data)

    @classmethod
    def create_data(cls, *, fid='test', **kwargs):
        fids = format(fid % 1000, '03') if isinstance(fid, int) else str(fid)
        data = dict(
            email=f'mail_{fids}@email.any',
            username=f'user_{fids}',
            first_name=f'first_name_{fids}',
            last_name=f'last_name_{fids}',
        )
        data.update(**kwargs)
        return data

class TestTag(TestModel):
    Model = Tag
    INSTANCE_FIELDS = (
        'id', 'name', 'color', 'slug', 
    )

    @classmethod
    def create_data(cls, *, fid=1, **kwargs):
        fids = format(fid % 1000, '03') if isinstance(fid, int) else str(fid)
        fidn = fid if isinstance(fid, int) else hash(fid)
        color = format(fidn % 2**20, '5>6x')
        data = dict(
            name=f'name_{fids}',
            color=f'#{color}',
            slug=f'slug_{fids}',
        )
        data.update(**kwargs)
        return data

class TestIngredient(TestModel):
    Model = Ingredient
    INSTANCE_FIELDS = (
        'id', 'name', 'measurement_unit',
    )
    NAME_PREFIX = 'No'

    @classmethod
    def create_data(cls, *, fid='test', **kwargs):
        fids = format(fid % 1000, '03') if isinstance(fid, int) else str(fid)
        data = dict(
            name=f'{cls.NAME_PREFIX}{fids}_ingredient',
            measurement_unit=f'measure_{fids}',
        )
        data.update(**kwargs)
        return data


class TestRecipe(TestModel):
    Model = Recipe
    INSTANCE_FIELDS = ('id', 'name', 'text', 'cooking_time', 'author')

    @classmethod
    def get_instance_data(cls, instance, **kwargs):
        data = super().get_instance_data(
            instance,
            tags = [tag.id for tag in instance.tags.all()],
            ingredients = [
                dict(id=i.ingredient.id, amount=i.amount) 
                for i in instance.ingredients.all()
            ]
        )
        data.update(*kwargs)
        return data

    @classmethod
    def create_data(cls, *, fid=1, **kwargs):
        fids = format(fid % 1000, '03') if isinstance(fid, int) else str(fid)
        data = dict(
            name=f'recipe_{fids}',
            text=f'rext_{fids}',
            cooking_time=fid if isinstance(fid, int) else (hash(fid) % 1000) + 1,
            # author & image отсутствуют - так надо!
        )
        data.update(**kwargs)
        return data
 
    
def left_extend_str(s, dest_size, char='q'):
    return char * (dest_size - len(s)) + s

def db_is_sqlite():
    return settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'

def nrange(start, length):
    return range(start, start+length)

def get_nth_subset(sec, n):
    sec_len = len(sec)
    # for n in range(2**sec_len):
    assert n < 2**sec_len
    mask = format(n, f'0{sec_len}b')
    return (sec[i] for i in range(sec_len) if mask[i]=='1')
