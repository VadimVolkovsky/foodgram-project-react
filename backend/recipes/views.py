# from django.shortcuts import render
from collections import OrderedDict
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404

from .models import Ingredient, Recipe, Tag, User, Follow
from .serializers import (RecipeSerializer, TagSerializer, IngredientSerializer,
    IngredientPostSerializer, RecipePostSerializer, UserSerializer, CustomUserSerializer, SubscribeSerializer)
    #FollowPostSerializer)
from rest_framework import status


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    # def get_serializer_class(self):
    #     if self.request.method in ['POST', 'PUT', 'PATCH']:
    #         return CustomUserCreateSerializer
    #     return UserSerializer

    def get_queryset(self):
        new_queryset = User.objects.all()
        return new_queryset

    @action(detail=True, methods=['post', 'delete']) #permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Метод для подписки/отписки на авторов"""
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)#, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Метод для просмотра своих подписок"""
        user = request.user
        queryset = User.objects.filter(following__user=user)
        #pages = self.paginate_queryset(queryset)
        pages = queryset
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        #return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipePostSerializer
        return RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return IngredientPostSerializer
        return IngredientSerializer


#class FollowViewSet(viewsets.ModelViewSet):

# class FollowViewSet(mixins.CreateModelMixin,
#                     mixins.ListModelMixin,
#                     viewsets.GenericViewSet):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer

#     def get_queryset(self):
#         """Возвращает все подписки пользователя, сделавшего запрос"""
#         new_queryset = Follow.objects.filter(user=self.request.user)
#         return new_queryset

#     def create(self, request, *args, **kwargs):
#         user = self.request.user,
#         author = User.objects.get(id=kwargs['user_id'])
#         request.data["user"]=user
#         request.data["author"]=author
#         serializer = FollowSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED) 
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

        

    # def perform_create(self, serializer):
    #     return serializer.save(user=self.request.user)
    
# class FollowList(generics.ListAPIView):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer


# class FollowCreate(generics.CreateAPIView):
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer

#     def post(self, request, *args, **kwargs):
#         user = self.request.user
#         author = User.objects.get(id=kwargs['user_id'])
#         return Follow.objects.get_or_create(user=user, author=author)

    