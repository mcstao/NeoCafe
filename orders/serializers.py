from rest_framework import serializers
from branches.models import Branch
from menu.models import Menu, ExtraItem
from .models import Order, OrderItem, Table
from django.db import transaction




class OrderStaffItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    menu_id = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), source='menu', write_only=True)
    quantity = serializers.IntegerField(required=True)
    extra_product = serializers.PrimaryKeyRelatedField(queryset=ExtraItem.objects.all(), many=True, required=False)

    class Meta:
        model = OrderItem
        fields = ['menu_id', 'quantity', 'extra_product']

class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_available', 'branch']

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
        fields = ['items', 'total_price', 'bonuses_used', 'order_type', 'table', 'waiter']
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        validated_data['Официант'] = self.context['request'].user
        validated_data['bonuses_used'] = 0  # Официанты не используют бонусы

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class OrderCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for customer orders.
    """
    items = OrderStaffItemSerializer(many=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    bonuses_used = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Order
        fields = ['items', 'total_price', 'bonuses_used', 'order_type', 'table', 'user', 'status']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data.pop('waiter', None)

        bonuses_used = validated_data.get('bonuses_used', 0)
        if bonuses_used > user.bonus:
            raise serializers.ValidationError("Недостаточно бонусов.")

        order = Order.objects.create(**validated_data)

        total_price = 0
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total_price += item.menu.price * item.quantity

        total_price = max(total_price - bonuses_used, 0)
        user.bonus -= bonuses_used
        user.save()

        order.total_price = total_price
        order.save()

        return order

    def update(self, instance, validated_data):
        # Проверяем изменение статуса заказа
        status = validated_data.get('status', instance.status)
        if status == "Завершено" and instance.status != "Завершено":
            # Начисляем бонусы пользователю 1 к 1 от итоговой стоимости заказа
            instance.user.bonus += instance.total_price
            instance.user.save()

        return super().update(instance, validated_data)