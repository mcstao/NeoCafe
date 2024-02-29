from rest_framework import serializers
from menu.models import Category, Menu, ExtraItem, Ingredient


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity', 'measurement_unit']


class MenuSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'image', 'category', 'description', 'price', 'available', 'branch', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        menu = Menu.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(menu_item=menu, **ingredient_data)

        return menu


class ExtraItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraItem
        fields = ['name', 'price', 'type_extra_product', 'choice_category']


