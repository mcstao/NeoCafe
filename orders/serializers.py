from rest_framework import serializers
from branches.models import Branch
from menu.models import Menu, ExtraItem
from .models import Order, OrderItem
from django.db import transaction




class OrderStaffItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    menu_id = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), source='menu', write_only=True)
    menu_quantity = serializers.IntegerField(required=True)
    extra_product = serializers.PrimaryKeyRelatedField(queryset=ExtraItem.objects.all(), many=True, required=False)

    class Meta:
        model = OrderItem
        fields = ['menu_id', 'menu_quantity', 'extra_product']


class OrderStaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model.
    """
    items = OrderStaffItemSerializer(many=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    bonuses_used = serializers.IntegerField(required=True)
    table = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = ['items', 'total_price', 'bonuses_used', 'order_type', 'table']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
