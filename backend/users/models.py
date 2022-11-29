from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=150
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150
    )
    email = models.EmailField(
        verbose_name="Email",
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )


class Follow(models.Model):
    """Модель для подписок на авторов"""
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
