import logging
from decimal import Decimal
from typing import List

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from branches.models import Branch
from menu.models import Menu, ExtraItem
from menu.serializers import MenuSerializer
from services.menu.menu import update_ingredient_storage_on_cooking
from .models import Order, OrderItem, Table

logger = logging.getLogger(__name__)


class OrderStaffItemSerializer(serializers.ModelSerializer):
    menu_detail = serializers.SerializerMethodField(read_only=True)
    menu_id = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_id', 'menu_detail', 'quantity', 'extra_product']

    @extend_schema_field(serializers.CharField())
    def get_menu_detail(self, obj):
        return MenuSerializer(obj.menu).data


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_available', 'branch']


class OrderStaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model.
    """
    items = OrderStaffItemSerializer(many=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    table = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, allow_blank=False, write_only=True)
    order_type = serializers.ChoiceField(choices=Order.TYPE_CHOICES, allow_blank=False, write_only=True)
    created = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'items', 'total_price', 'order_type', 'table', 'waiter', 'status', 'branch', 'created',
                  'updated_at', 'completed_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        validated_data['Официант'] = self.context['request'].user

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])

        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.waiter = validated_data.get('waiter', instance.waiter)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        for item_data in items_data:
            menu_id = item_data['menu_id']
            new_quantity = item_data['quantity']

            menu_item = Menu.objects.get(id=menu_id)

            # Поиск существующего OrderItem
            item = instance.items.filter(menu=menu_item).first()

            if item:
                # Если пункт заказа уже существует, обновляем количество и пересчитываем его стоимость

                item.quantity += new_quantity
                item.save()

            else:
                # Если пункта заказа нет, создаем новый и добавляем его стоимость к общей
                OrderItem.objects.create(order=instance, menu=menu_item, quantity=new_quantity)

            # Обновляем ингредиенты на складе для добавленного количества
            if new_quantity > 0:
                update_ingredient_storage_on_cooking(menu_id, instance.branch.id, new_quantity)

        # Расчет общей стоимости заказа
        total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
        instance.total_price = max(total_price, Decimal(0))
        instance.save()

        if instance.status == "Завершено":
            instance.completed_at = timezone.now()
        instance.save()

        return instance


class OrderCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for customer orders.
    """
    items = OrderStaffItemSerializer(many=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    bonuses_used = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), required=False, allow_null=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, allow_blank=False, write_only=True)
    order_type = serializers.ChoiceField(choices=Order.TYPE_CHOICES, allow_blank=False, write_only=True)
    created = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    completed_at = serializers.DateTimeField(allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'items', 'total_price', 'bonuses_used', 'order_type', 'table', 'user', 'status', 'branch',
                  'created',
                  'updated_at', 'completed_at']

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
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.status = validated_data.get('status', instance.status)
        instance.bonuses_used = validated_data.get('bonuses_used', instance.bonuses_used)

        # Проверка наличия бонусов у пользователя
        if instance.bonuses_used > instance.user.bonus:
            raise serializers.ValidationError("Недостаточно бонусов у пользователя.")

        # Пересчет общей стоимости заказа

        for item_data in items_data:
            menu_id = item_data['menu_id']
            new_quantity = item_data['quantity']

            menu_item = Menu.objects.get(id=menu_id)

            # Поиск существующего OrderItem
            item = instance.items.filter(menu=menu_item).first()

            if item:
                # Если пункт заказа уже существует, обновляем количество и пересчитываем его стоимость

                item.quantity += new_quantity
                item.save()
                # Обновляем общую стоимость, учитывая разницу в количестве

            else:
                # Если пункта заказа нет, создаем новый и добавляем его стоимость к общей
                OrderItem.objects.create(order=instance, menu=menu_item, quantity=new_quantity)

            # Обновляем ингредиенты на складе для добавленного количества
            if new_quantity > 0:
                update_ingredient_storage_on_cooking(menu_id, instance.branch.id, new_quantity)

        # Расчет общей стоимости заказа
        total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
        instance.total_price = max(total_price - instance.bonuses_used, Decimal(0))
        instance.save()

        # Обновление бонусов пользователя
        if instance.status == "Завершено":
            instance.user.bonus -= instance.bonuses_used
            instance.user.bonus += instance.total_price  # Начисляем бонусы за заказ
            instance.user.save()
            instance.completed_at = timezone.now()
        instance.save()

        return instance


class TableDetailSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_available', 'orders']

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_orders(self, obj):
        active_statuses = ['Новый', 'В процессе', 'Готово']
        orders = obj.order_set.filter(status__in=active_statuses)
        return OrderStaffSerializer(orders, many=True).data


class OrderDetailedListSerializer(serializers.ModelSerializer):
    items = OrderStaffItemSerializer(many=True, read_only=True)
    table_detail = TableSerializer(source='table', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_type', 'status', 'user', 'total_price', 'branch',
                  'bonuses_used', 'waiter', 'created', 'table', 'items', 'table_detail']
