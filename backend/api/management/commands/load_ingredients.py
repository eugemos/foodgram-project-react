"""Содержит django-admin команду для загрузки ингредиентов в БД."""
from django.core.management.base import BaseCommand
from rest_framework.parsers import JSONParser

from api.serializers import IngredientSerializer


class Command(BaseCommand):
    """Определяет django-admin команду для загрузки ингредиентов в БД."""
    help = "Загружает ингредиенты в БД из файла в формате JSON."

    def add_arguments(self, parser):
        """Определяет аргументы команды."""
        parser.add_argument(
            'file_name', metavar='<file name>',
            help='Имя файла с ингредиентами.'
        )

    def handle(self, *args, **options):
        """Выполняет команду"""
        file_name = options['file_name']
        try:
            with open(file_name, 'rb') as file:
                data = JSONParser().parse(file)
        except Exception as e:
            return f'Ошибка: {e}'

        serializer = IngredientSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return 'Загрузка выполнена успешно.'

        return f'Файл содержит некорректные данные:\n{serializer.errors}'
