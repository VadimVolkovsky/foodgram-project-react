from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint
#from users.models import User
from rest_framework.authtoken.models import Token


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe",
        related_name="recipes"
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
        blank=True,
        null=True
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, message='Время готовки должно быть больше 1 минуты.')
        ]
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):  # связующая модель
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиента не может быть меньше единицы'
            )
        ]
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name="favorites",
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorites",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_favorite"
            )
        ]
