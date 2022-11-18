from rest_framework import serializers
import base64
from django.core.files.base import ContentFile
from rest_framework.validators import UniqueTogetherValidator

from .models import Recipe, Ingredient, Tag, User, IngredientRecipe, Follow


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredienSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
           "id", "name", "measurement_unit"
        )


class IngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientRecipe
        fields = (
           "id", "name", "measurement_unit", "amount"
        )

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit



class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'slug'
        )

    # def to_representation(self, instance):
    #     return TagSerializer(instance).data



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name" # ,"is_subscribted"
         )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientPostSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Tag.objects.all(),
        many=True
    )

    ingredients = IngredientPostSerializer(many=True, required=False)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        print(f"Печатаем IT: {self.initial_data}")
        print(f"Печатаем VD: {self.validated_data}")
        tags_temp = validated_data.pop("tags")  # вырезали ненужное
        ingredients_temp = validated_data.pop("ingredients") # вырезали ненужное
        print(f'Смотрим тип ingredients_temp: {type(ingredients_temp)}')
        # ingredint_amount = ingredients_temp.remove("amount")
        ingredients = self.initial_data.pop("ingredients")   # список ингредиентов
        print(f"Печатаем Ingredients из IT: {ingredients}")
        tags = self.initial_data.pop('tags')  # список тегов
        print(f"Печатаем IT_2: {self.initial_data}")
        print(f"Печатаем VD_2: {self.validated_data}")
        recipe = Recipe.objects.create(**validated_data)  # создаем рецепт без тегов и ингредиентов
        tag_obj = Tag.objects.get(id=tags[0])  # достаем объект тега
        print(f"Печатаем ingredients: {ingredients}")
        for ingredient in ingredients:
            ingredient_amount = ingredient.pop("amount") # вырезаем amount
            ingredient_obj = Ingredient.objects.get(**ingredient)  # достаем объект ингредиента

        # создаем объект в связной таблице:
            current_ingredient, status = ( 
                IngredientRecipe.objects.get_or_create(
                    ingredient=ingredient_obj,
                    amount=ingredient_amount
                    )
            )
            recipe.ingredients.add(current_ingredient) # добавляем ингредиент в рецепт

        recipe.tags.add(tag_obj)  # добавляем теги в рецепт
        
        return recipe
    
    def to_representation(self, instance):
        return RecipeSerializer(instance).data





class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following',),
                message="Вы уже подписаны на данного автора"
            ),
        )

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data