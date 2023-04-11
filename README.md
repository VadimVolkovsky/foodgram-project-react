### Описание проекта

Сайт Foodgram, «Продуктовый помощник» - это онлайн-сервис кулинарных рецептов.

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Основные возможности проекта
- Просмотр списка рецептов
- Создание, удаление и редактирование собственных рецептов
- Добавление рецептов в избранное
- Добавления рецептов в список покупок
- Возможность подписки на других авторов
- Получение списка необходимых к покупке ингредиентов

### Инструкция по запуску проекта
**Клонируйте репозиторий:**
```
git clone git@github.com:VadimVolkovsky/foodgram-project-react.git
```

**Установите и активируйте виртуальное окружение:**
для MacOS:
```
python3 -m venv venv
```

для Windows:
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```
**Установите зависимости из файла requirements.txt:**
```
pip install -r requirements.txt
```

**Примените миграции:**
```
python manage.py migrate
```

**Сборка контейнеров:**

Находясь в директории /infra разверните контейнеры при помощи docker-compose:
```
docker-compose up -d --build
```

**Выполните миграции:**
```
docker-compose exec backend python manage.py migrate
```

**Создайте суперпользователя:**
```
docker-compose exec backend python manage.py createsuperuser
```

**Соберите статику:**
```
docker-compose exec backend python manage.py collectstatic --no-input
```

**Остановка проекта:**
```
docker-compose down
```

### Примеры запросов:
**POST | Создание рецепта: **
http://127.0.0.1:8000/api/recipes/
```
Request:
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
```
Response:
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```

**POST | Подписаться на пользователя:**
http://127.0.0.1:8000/api/users/{id}/subscribe/
```
Response:

{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```


#### Автор проекта:

**Vadim Volkovsky**
