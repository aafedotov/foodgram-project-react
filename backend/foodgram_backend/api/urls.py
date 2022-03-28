from django.urls import include, re_path, path

from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', CustomUserViewSet)

urlpatterns = [
    re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    # path('', include(router_v1.urls)),
]
