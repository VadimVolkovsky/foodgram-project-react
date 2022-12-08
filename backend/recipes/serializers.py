from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from users.serializers import CustomUserSerializer

from .fields import Base64ImageField, Hex2NameColor
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов ингредиентов"""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связной модели IngredientRecipe"""
    id = serializers.IntegerField(source='ingredient.id')
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
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipes'
    )
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
        many=True,
        required=True
    )

    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        """Валидация поля ингредиентов при создании рецепта"""
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать как минимум один ингредиент'
            )
        ingredients_id_list = []
        for item in value:
            if item['amount'] == 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть равным нулю'
                )
            ingredient_id = item['ingredient']['id']
            if ingredient_id in ingredients_id_list:
                raise serializers.ValidationError(
                    'Указано несколько одинаковых ингредиентов'
                )
            ingredients_id_list.append(ingredient_id)
        return value

    def validate_tags(self, value):
        """Валидаци поля тегов при создании рецепта"""
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать как минимум один тег'
            )
        return value

    def _create_ingredient_recipe_objects(self, ingredients, recipe):
        """Вспомогательный метод для создания
        объектов модели IngredientRecipe"""
        for ingredient in ingredients:
            ingredient_amount = ingredient.pop("amount")
            ingredient_obj = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )
            IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient_amount
            )
            recipe.ingredients.add(ingredient_obj)
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self._create_ingredient_recipe_objects(ingredients, recipe)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._create_ingredient_recipe_objects(ingredients, recipe=instance)
        return instance

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
