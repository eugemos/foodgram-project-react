"""Задаёт соответствие между эндпойтами приложения users
и их обработчиками.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GetTokenView, UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('auth/token/login/', GetTokenView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += router.urls
