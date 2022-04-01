from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    UserSerializer, ChangePasswordSerializer, TagSerializer,
    IngredientUnitSerializer, RecipePostSerializer,
    RecipeReadOnlySerializer
)
from .mixins import ListRetrieveCreateViewSet, ListRetrieveViewSet
from .filters import IngredientFilter
from app.models import Tag, Ingredient, IngredientUnit, Recipe


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


class TagViewSet(ListRetrieveViewSet):
    """Представление для эндпоинта Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    """Представление для эндпоинта Tag."""

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    filterset_class = IngredientFilter
    queryset = IngredientUnit.objects.all()
    serializer_class = IngredientUnitSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """View-set для эндпоинта title."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadOnlySerializer
    permission_classes = [AllowAny]
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('category', 'genre', 'year', 'name')
    # filterset_class = TitleFilter

    def get_serializer_class(self):
        """Определяем сериализаторы в зависимости от реквест методов."""
        if self.action == 'create' or self.action == 'partial_update':
            return RecipePostSerializer
        return RecipeReadOnlySerializer

    def perform_create(self, serializer):
        """Переопределяем сохранение автора рецепта."""
        author = self.request.user
        serializer.save(author=author)
