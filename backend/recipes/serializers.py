import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers, status

from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class Base64ImageField(serializers.ImageField):
    """Добавление изображений к рецептам"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """Добавление цвета при создании тега"""
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
           "id", "name", "measurement_unit",
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
    """Сериалайзер для создания и просмотра тегов"""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'id', 'name', "color", 'slug'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов"""
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_ingredients(self, obj):
        """Отображает ингредиенты в составе рецепта"""
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверяет добавлен ли рецепт в избранное
        у авторизованного пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет добавлен ли рецепт в корзину
        у авторизованного пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(recipe=obj).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    tags = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Tag.objects.all(),
        many=True
    )

    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        validated_data.pop("ingredients")
        ingredients = self.initial_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_amount = ingredient.pop("amount")
            ingredient_obj = Ingredient.objects.get(**ingredient)

            current_ingredient, status = (
                IngredientRecipe.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=ingredient_amount
                    )
            )
            recipe.ingredients.add(ingredient_obj)

        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class FavoriteSerializer(RecipeSerializer):
    """Сериализатор для добавления рецепта в избранное"""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в избранное',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class ShoppingCartSerializer(RecipeSerializer):
    """Сериализатор добавления рецепта в корзину"""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в корзину',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
