from rest_framework import serializers, viewsets
from .models import Category, Menu, ExtraItem
from .serializers import CategorySerializer, MenuSerializer, ExtraItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class ExtraItemViewSet(viewsets.ModelViewSet):
    queryset = ExtraItem.objects.all()
    serializer_class = ExtraItemSerializer

