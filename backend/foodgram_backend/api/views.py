import io

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import (
    Tag, IngredientUnit, Recipe, Subscription, RecipeFavorite,
    RecipeCart
)
from .filters import IngredientFilter, RecipeFilter
from .mixins import (
    ListRetrieveCreateViewSet, ListRetrieveViewSet, ListViewSet
)
from .serializers import (
    UserSerializer, ChangePasswordSerializer, TagSerializer,
    IngredientUnitSerializer, RecipePostSerializer,
    RecipeReadOnlySerializer, SubscribeListSerializer,
    SubscribeRecipeSerializer
)

User = get_user_model()


class CustomSetPagination(PageNumberPagination):

    page_size_query_param = 'limit'


class CustomUserViewSet(ListRetrieveCreateViewSet):
    """View-set для эндпоинта users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UsersMeApiView(APIView):
    """Отдельно описываем поведение для users/me."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получаем себя при обращении на users/me."""

        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)


class ChangePasswordView(CreateAPIView):
    """Представление для эндпоинта смены пароля пользователя."""

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self, queryset=None):
        """Получаем в объект текущего пользователя."""

        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        """Описываем логику по смене пароля."""

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
    """Представление для эндпоинта Ингредиентов."""

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    filterset_class = IngredientFilter
    queryset = IngredientUnit.objects.all()
    serializer_class = IngredientUnitSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для эндпоинта Рецептов."""

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

    def get_queryset(self):
        """Фильтруем выборку рецептов, в зависимости от Query Params."""

        if self.request.query_params.get('is_favorited') == '1':
            user = self.request.user
            favorites = RecipeFavorite.objects.filter(
                user=user
            ).values_list('recipe__id', flat=True)
            queryset = Recipe.objects.filter(id__in=favorites)
            return queryset
        if self.request.query_params.get('is_in_shopping_cart') == '1':
            user = self.request.user
            in_cart = RecipeCart.objects.filter(
                user=user
            ).values_list('recipe__id', flat=True)
            queryset = Recipe.objects.filter(id__in=in_cart)
            return queryset
        return Recipe.objects.all()


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


class CartPostDestroyView(APIView):
    """Представление для добавления и удаления из корзины."""

    def post(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["id"])
        user = self.request.user
        cart, created = RecipeCart.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        if not created:
            return Response('Данный рецепт уже в корзине!',
                            status=status.HTTP_400_BAD_REQUEST
                            )
        cart.save()
        serializer = SubscribeRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, requets, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs["id"])
        cart = get_object_or_404(RecipeCart, user=self.request.user,
                                     recipe=recipe)
        cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartDownloadView(APIView):


    def get(self, request, **kwargs):

        buffer = io.BytesIO()

        p = canvas.Canvas(buffer)
        line = 800
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        p.setFont('FreeSans', 16)
        p.drawString(15, line, "Список покупок для выбранных рецептов:")
        p.setFont('FreeSans', 12)
        line -= 50
        user = self.request.user
        in_cart = RecipeCart.objects.filter(user=user).values_list(
            'recipe__id', flat=True)
        queryset = Recipe.objects.filter(id__in=in_cart)
        ingredients_dict = {}
        for recipe in queryset:
            ingredients = recipe.ingredient.all()
            for ingredient in ingredients:
                key = f'{str(ingredient.ingredient.name)}'
                key += f' ({str(ingredient.ingredient.measurement_unit.name)})'
                to_dict = ingredients_dict.get(key)
                if to_dict:
                    ingredients_dict[key] += ingredient.amount
                else:
                    ingredients_dict[key] = ingredient.amount
        for ingredient, amount in ingredients_dict.items():
            line -= 10
            to_print = f'{ingredient} - {amount}'
            p.drawString(15, line, to_print.capitalize())
        line -= 55
        p.setFont('FreeSans', 14)
        p.drawString(15, line, 'Список сгенерирован сервисом Продуктовый Помощник.')
        line -= 20
        p.setFont('FreeSans', 12)
        p.drawString(15, line, 'Автор: Андрей Федотов.')
        p.showPage()
        p.save()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
