from django.db import models
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Recipe(models.Model):
    tags = 
    author = 
    ingredients = 
    is_favorited = 
    is_in_shopping_cart = 
    name = 
    image = 
    text = 
    cooking_time = 

    class Meta:
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("_detail", kwargs={"pk": self.pk})
