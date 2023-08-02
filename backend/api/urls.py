from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import GetTokenView
from .views import TagViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/token/login/', GetTokenView.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    # path('', views.index, name='index'), 
]

urlpatterns += router.urls
