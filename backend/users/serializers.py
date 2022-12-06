from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status

from recipes.models import Recipe
from .models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор просмотра профиля пользователя"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name",
            "last_name", "is_subscribed",
         )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Мини-сериализатор для просмотра рецептов в профиле пользователя"""
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class SubscribeSerializer(UserSerializer):
    """ Сериализатор для создания/получения подписок """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count",
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()

    def get_recipes(self, obj):
        """Показывает рецепты текущего пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj).order_by('-id')
        return RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Счетчик рецептов текущего пользователя"""
        return Recipe.objects.filter(author=obj).count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
