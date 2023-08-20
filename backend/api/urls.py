"""Задаёт соответствие между эндпойтами приложения api
и их обработчиками.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include('users.urls')),
]

urlpatterns += router.urls
