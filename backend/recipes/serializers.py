from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework.validators import UniqueTogetherValidator
import webcolors

from .models import Recipe, Ingredient, Tag, IngredientRecipe, Follow
from .models import User
from rest_framework import status


class Base64ImageField(serializers.ImageField):
    """Добавление изображений к рецептам"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов ингредиентов"""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = (
           "id", "name", "measurement_unit"
        )


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор поля игредиентов при создании новых рецептов"""

    class Meta:
        model = Ingredient
        fields = (
           "id", "name", "measurement_unit", #"amount"
        )



class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связной модели IngredientRecipe"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'id', 'name', "color", 'slug'
        )


# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = (
#             "email", "id", "username", "first_name", "last_name" # ,"is_subscribted"
#          )


class CustomUserSerializer(UserSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name", "password",
         )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Tag.objects.all(),
        many=True
    )

    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    author = CustomUserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        tags_temp = validated_data.pop("tags")  # вырезали ненужное
        ingredients_temp = validated_data.pop("ingredients") # вырезали ненужное
        tags = self.initial_data.pop('tags')  # список тегов
        ingredients = self.initial_data.pop("ingredients")   # список ингредиентов
        recipe = Recipe.objects.create(**validated_data)  # создаем рецепт без тегов и ингредиентов
        for ingredient in ingredients:
            print(f'Печатаем ингредиент {ingredient}')
            ingredient_amount = ingredient.pop("amount")  # вырезаем amount
            ingredient_obj = Ingredient.objects.get(**ingredient)  # достаем объект ингредиента

        # создаем объект в связной таблице ингредиентов:
            current_ingredient, status = ( 
                IngredientRecipe.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=ingredient_amount
                    )
            )
            recipe.ingredients.add(ingredient_obj) # добавляем ингредиент в рецепт
        
        for tag in tags: #перебираем теги
            tag_obj = Tag.objects.get(id=tag)  # достаем объект тега
            recipe.tags.add(tag_obj)  # добавляем тег в рецепт
        return recipe
    
    def to_representation(self, instance):
        return RecipeSerializer(instance).data


# class FollowSerializer(serializers.ModelSerializer):
#     """Сериайлайзер для GET запросов на подписки"""
#     class Meta:
#         model = Follow
#         fields = ('user', 'author')


# class FollowSerializer(serializers.ModelSerializer):
#     user = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     author = serializers.SlugRelatedField(
#         slug_field='username',
#         queryset=User.objects.all()
#     )

#     class Meta:
#         model = Follow
#         fields = '__all__'
#         validators = (
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'author',),
#                 message="Вы уже подписаны на данного автора"
#             ),
#         )


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
