import json

from django.db import migrations

file = open('./data/ingredients.json', encoding="utf-8")
INITIAL_INGREDIENTS = json.load(file)


def add_ingredients(apps, schema_editor):
    ingredient_obj = apps.get_model("recipes", "Ingredient")
    for ingredient in INITIAL_INGREDIENTS:
        new_ingredient = ingredient_obj(**ingredient)
        new_ingredient.save()


def remove_ingredients(apps, schema_editor):
    ingredient_obj = apps.get_model("recipes", "Ingredient")
    for ingredient in INITIAL_INGREDIENTS:
        ingredient_obj.objects.get(name=ingredient['name']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_add_tags'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            remove_ingredients
        )
    ]
