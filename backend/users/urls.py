from django.urls import path, include
from recipes.views import CustomUserViewSet, FollowList, FollowCreate  #FollowViewSet, 
from rest_framework.authtoken import views
from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'subscriptions', FollowViewSet)
# router.register(r'(?P<user_id>\d+)/subscribe',
#                 FollowViewSet, basename='follows')


urlpatterns = [
   # path('users/', include(router.urls)),
    path('users/subscriptions/', FollowList.as_view()),
    path('users/<user_id>/subscribe/', FollowCreate.as_view()),
    # path('users/', CustomUserViewSet.as_view(
    #     {"post": "create", "get": "list"})),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),

] 

