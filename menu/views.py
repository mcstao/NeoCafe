from rest_framework import serializers, viewsets
from .models import Category, Menu, ExtraItem
from .serializers import CategorySerializer, MenuSerializer, ExtraItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def perform_create(self, serializer):
        category_id = self.request.data.get('category')
        if category_id:
            category = Category.objects.get(pk=category_id)
            serializer.save(category=category)
        else:
            serializer.save()

    def perform_update(self, serializer):
        category_id = self.request.data.get('category')
        if category_id:
            category = Category.objects.get(pk=category_id)
            serializer.save(category=category)
        else:
            serializer.save()


class ExtraItemViewSet(viewsets.ModelViewSet):
    queryset = ExtraItem.objects.all()
    serializer_class = ExtraItemSerializer

    def perform_create(self, serializer):
        category_id = self.request.data.get('choice_category')
        if category_id:
            category = Category.objects.get(pk=category_id)
            serializer.save(choice_category=category)
        else:
            serializer.save()

    def perform_update(self, serializer):
        category_id = self.request.data.get('choice_category')
        if category_id:
            category = Category.objects.get(pk=category_id)
            serializer.save(choice_category=category)
        else:
            serializer.save()
