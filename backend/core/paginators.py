"""Содержит пажинаторы, используемые другими приложениями."""
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Стандартный пажинатор для всего сайта."""
    page_size_query_param = 'limit'
