from rest_framework import serializers
from branches.models import Branch
from .models import Category, Item


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Item
        fields = ['id', 'name', 'quantity', 'quantity_unit', 'limit', 'arrival_date',
                  'category', 'branch', 'is_running_out'
                  ]
