from base64 import b64encode, b64decode

from django.core.files import File 
from django.core.files.base import ContentFile 
from core.tests.base import TestRecipe, TestUser


def load_file_as_base64_bytes(file_name):
    file = open(file_name, 'rb')
    content = file.read()
    file.close()
    b = b64encode(content)
    return b
    # s= b.decode()
    # return s

def load_base64_file_as_bytes(file_name):
    file = open(file_name, 'rb')
    content = file.read()
    file.close()
    b = b64decode(content)
    return b

def encode64(in_file_name, out_file_name):
    out_file = open(out_file_name, 'wb')
    out_file.write(load_file_as_base64_bytes(in_file_name))
    out_file.close()

def decode64(in_file_name, out_file_name):
    out_file = open(out_file_name, 'wb')
    out_file.write(load_base64_file_as_bytes(in_file_name))
    out_file.close()

def proba(file_name):
    if TestUser.Model.objects.count() > 0:
        author = TestUser.Model.objects.all()[0]
    else:
        author = TestUser.create_instance(TestUser.create_data())
    # f = File(open(file_name), name='proba.txt')
    f = ContentFile('This is '+file_name, )#name='proba.txt')
    return TestRecipe.create_instance(TestRecipe.create_data(n=1), image=f, author=author)
    # from api.tests.views.recipes.proba import proba
    # r = proba('api\\urls.py')
