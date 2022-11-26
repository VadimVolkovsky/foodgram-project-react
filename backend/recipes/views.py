# from django.shortcuts import render
from collections import OrderedDict
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404

from .models import Ingredient, Recipe, Tag, User, Follow, Favorite
from .serializers import (RecipeSerializer, TagSerializer, IngredientSerializer,
    IngredientPostSerializer, RecipePostSerializer, UserSerializer, CustomUserSerializer, SubscribeSerializer, FavoriteSerializer)
from rest_framework import status


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipePostSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        """Метод для добавления рецепта в избранное"""
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                recipe, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        if request.method == "DELETE":
            favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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

