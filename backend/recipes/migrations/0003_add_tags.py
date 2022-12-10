from django.db import migrations

INITIAL_TAGS = [
    {'color': '#228B22', 'name': 'завтрак', 'slug': 'breakfast'},
    {'color': '#00FF00', 'name': 'обед', 'slug': 'lunch'},
    {'color': '#F0E68C', 'name': 'ужин', 'slug': 'dinner'},
]


def add_tags(apps, schema_editor):
    tag_obj = apps.get_model("recipes", "Tag")
    for tag in INITIAL_TAGS:
        new_tag = tag_obj(**tag)
        new_tag.save()


def remove_tags(apps, schema_editor):
    tag_obj = apps.get_model("recipes", "Tag")
    for tag in INITIAL_TAGS:
        tag_obj.objects.get(name=tag['name']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_tags,
            remove_tags
        )
    ]
