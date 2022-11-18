from django.contrib import admin

from .models import Recipe, Ingredient, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'get_tags',
        'author',
        'get_ingredients',
        'name',
        'image',
        'text',
        'cooking_time'
    )

    def get_tags(self, obj):  # подгружает список тегов в админку
        return ", ".join([t.name for t in obj.tags.all()])

    def get_ingredients(self, obj):  # подгружает список ингредиентов
        return ", ".join([i.ingredient.name for i in obj.ingredients.all()])


class IngredientAdmin(admin.ModelAdmin):
    list_dispaly = (
        'name',
        'measurement_unit'
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        #'color',
        'slug'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
