"""Задаёт соответствие между эндпойтами API и их обработчиками."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    GetTokenView, UserViewSet
)


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('auth/token/login/', GetTokenView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += router.urls
