from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, ChangePasswordSerializer
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


class ChangePasswordView(CreateAPIView):
    """Представление для эндпоинта смены пароля пользователя."""
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(
                    serializer.data.get("current_password")):
                return Response({"current_password": ["Неправильный пароль!"]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_204_NO_CONTENT,
                'message': 'Пароль успешно обновлен!',
                'data': []
            }
            return Response(response)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
