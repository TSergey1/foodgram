from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet,
                    FollowViewSet,
                    RecipesViewSet,
                    TagViewSet,
                    UserViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet)
# router.register(
#     r'users/(?P<user_id>\d+)/subscribe',
#     FollowViewSet,
#     basename='subscribe'
# )
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipesViewSet)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
