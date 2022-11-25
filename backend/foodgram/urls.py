from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from recipes.views import RecipeViewSet, TagViewSet, IngredientViewSet, CustomUserViewSet #FollowViewSet, UserViewSet
from django.conf.urls.static import static
from django.conf import settings

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', CustomUserViewSet)
#router.register(r'follow', FollowViewSet)
#router.register(r'users', UserViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
