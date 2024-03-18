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

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])

        # Обновляем поля заказа
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.bonuses_used = validated_data.get('bonuses_used', instance.bonuses_used)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.waiter = validated_data.get('waiter', instance.waiter)
        instance.save()

        # Обновляем или создаем пункты заказа (items)
        for item_data in items_data:
            item_id = item_data.get('id', None)
            if item_id:
                # Обновляем существующий пункт заказа
                item = OrderItem.objects.get(id=item_id, order=instance)
                item.menu = item_data.get('menu', item.menu)
                item.quantity = item_data.get('quantity', item.quantity)
                item.save()
            else:
                # Создаем новый пункт заказа
                OrderItem.objects.create(order=instance, **item_data)

        return instance

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

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.save()

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])

        # Обновляем основные данные заказа
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Обрабатываем изменения в пунктах заказа
        for item_data in items_data:
            item_id = item_data.get('id', None)
            if item_id:
                item = OrderItem.objects.get(id=item_id, order=instance)
                item.menu = item_data.get('menu', item.menu)
                item.quantity = item_data.get('quantity', item.quantity)
                item.save()
            else:
                OrderItem.objects.create(order=instance, **item_data)

        # Логика начисления бонусов при изменении статуса заказа, если необходимо
        if instance.status == "Завершено" and not instance.bonuses_applied:
            instance.user.bonus += instance.total_price  # Начисляем бонусы
            instance.bonuses_applied = True  # Флаг, предотвращающий повторное начисление
            instance.user.save()

        return instance