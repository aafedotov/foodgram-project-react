from django.urls import include, re_path, path

from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet, UsersMeApiView, ChangePasswordView, TagViewSet,
    IngredientViewSet, RecipeViewSet, SubscribePostDestroyView,
    SubscribeListViewSet, FavoritePostDestroyView
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', CustomUserViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)

urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    re_path(r'users/(?P<id>\d+)/subscribe', SubscribePostDestroyView.as_view()),
    re_path(r'recipes/(?P<id>\d+)/favorite', FavoritePostDestroyView.as_view()),
    path('users/subscriptions/', SubscribeListViewSet.as_view({'get': 'list'})),
    path('users/set_password/', ChangePasswordView.as_view()),
    path('users/me/', UsersMeApiView.as_view()),
    path('', include(router_v1.urls)),
]
