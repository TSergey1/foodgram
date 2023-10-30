from django.urls import include, path, re_path
from djoser import views
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet,
                    RecipesViewSet,
                    TagViewSet,
                    UserViewSet)

router = DefaultRouter()
# router.register(r'posts/(?P<id>\d+)/subscribe', FollowViewSet)
router.register(r'users', UserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipesViewSet)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
