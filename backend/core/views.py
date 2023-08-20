"""Содержит функции отображения кастомных страниц для ошибок."""
from django.shortcuts import render
from rest_framework import status


def page_not_found(request, exception):
    """Отображает кастомную страницу для ошибки 404."""
    context = {'path': request.path}
    return render(
        request, 'core/templates/404.html',
        context, status=status.HTTP_404_NOT_FOUND
    )
