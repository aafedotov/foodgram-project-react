from rest_framework import viewsets

from users.models import CustomUser
from .serializers import CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    """View-set для эндпоинта users."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # pagination_class = PageNumberPagination
    # permission_classes = [OnlyAdminPermission]
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # search_fields = ('username',)
    # lookup_field = 'username'
