"""Задаёт соответствие между эндпойтами API и их обработчиками."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    GetTokenView, UserViewSet
)


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/token/login/', GetTokenView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += router.urls
