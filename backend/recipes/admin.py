from django.contrib import admin

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User


class IngredientInLine(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    verbose_name = 'Ингредиент'
    verbose_name_plural = "Ингредиенты"


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_tags',
        'author',
        'get_ingredients',
        'name',
        'image',
        'text',
        'cooking_time',
        'get_in_favorited',
    )
    inlines = [
        IngredientInLine,
    ]
    list_filter = ('author', 'name', 'tags',)

    @admin.display(description='Теги')
    def get_tags(self, obj):
        """Отображает в админке теги каждого рецепта"""
        return ", ".join(
            [t for t in obj.tags.values_list('name', flat=True)])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        """Отображает в админке ингредиенты каждого рецепта"""
        return ", ".join(
            [i for i in obj.ingredients.values_list('name', flat=True)])

    @admin.display(description='В избранном')
    def get_in_favorited(self, obj):
        """Отображает в админке кол-во добавлений рецепта в избранное"""
        return obj.favorites.all().count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_filter = ('email', 'username',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
