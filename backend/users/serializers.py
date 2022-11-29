from djoser.serializers import UserCreateSerializer, UserSerializer
# from recipes.serializers import RecipeSerializer
from rest_framework import serializers

from .models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор просмотра профиля пользователя"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name", "password",  # проверить нужен ли passsword ??
         )


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя """

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class SubscribeSerializer(UserSerializer):
    """ Сериализатор для создания/получения подписок """
    # recipes_count = serializers.SerializerMethodField()
    # recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta): 
        #fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        fields = (
            "id", "email", "username", "first_name", "last_name") #, "recipes", "recipes_count"
        read_only_fields = ('email', 'username')

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


