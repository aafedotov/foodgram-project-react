from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .mixins import ListRetrieveCreateViewSet


User = get_user_model()


class CustomUserViewSet(ListRetrieveCreateViewSet):
    """View-set для эндпоинта users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # pagination_class = PageNumberPagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # search_fields = ('username',)
    # lookup_field = 'username'


class UsersMeApiView(APIView):
    """Отдельно описываем поведение для users/me."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Получаем себя при обращении на users/me."""
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)
