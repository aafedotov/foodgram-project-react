from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, filters
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


from .serializers import (
    UserSerializer, ChangePasswordSerializer, TagSerializer,
    IngredientUnitSerializer, RecipePostSerializer,
    RecipeReadOnlySerializer, SubscribeListSerializer,
    SubscribeRecipeSerializer
)
from .mixins import (
    ListRetrieveCreateViewSet, ListRetrieveViewSet, ListViewSet
)
from .filters import IngredientFilter, RecipeFilter
from app.models import (
    Tag, Ingredient, IngredientUnit, Recipe, Subscription, RecipeFavorite
)


User = get_user_model()


class CustomSetPagination(PageNumberPagination):

    page_size_query_param = 'limit'


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

    pagination_class = CustomSetPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadOnlySerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags', 'author',)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определяем сериализаторы в зависимости от реквест методов."""
        if self.action in ('create', 'partial_update'):
            return RecipePostSerializer
        return RecipeReadOnlySerializer

    def perform_create(self, serializer):
        """Переопределяем сохранение автора рецепта."""
        author = self.request.user
        serializer.save(author=author)


class SubscribePostDestroyView(APIView):

    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs["id"])
        user = self.request.user
        if author == user:
            return Response('Нельзя подписываться на самого себя!', status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            following=author
        )
        if not created:
            return Response('Вы уже подписаны на данного автора!', status=status.HTTP_400_BAD_REQUEST)
        subscription.save()
        serializer = SubscribeListSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, requets, **kwargs):
        author = get_object_or_404(User, id=self.kwargs["id"])
        subscription = get_object_or_404(Subscription, user=self.request.user, following=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(ListViewSet):
    """Вьюсет для списка подписок."""

    pagination_class = CustomSetPagination
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeListSerializer

    def get_queryset(self):
        user = self.request.user
        subs = user.follower.all().values_list('following__id', flat=True)
        queryset = User.objects.filter(id__in=subs)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isnumeric():
            context['recipes_limit'] = int(
                self.request.query_params.get('recipes_limit'))
        return context


class FavoritePostDestroyView(APIView):
    """Представление для добавления и удаления из избранного."""

    def post(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["id"])
        user = self.request.user
        favorite, created = RecipeFavorite.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            return Response('Данный рецепт уже в избранном!',
                            status=status.HTTP_400_BAD_REQUEST
                            )
        favorite.save()
        serializer = SubscribeRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, requets, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["id"])
        favorite = get_object_or_404(RecipeFavorite, user=self.request.user,
                                     recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
