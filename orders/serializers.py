import logging

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from branches.models import Branch
from menu.models import Menu, ExtraItem
from menu.serializers import MenuSerializer
from services.menu.menu import update_ingredient_storage_on_cooking
from .models import Order, OrderItem, Table
from django.db import transaction

logger = logging.getLogger(__name__)


class OrderStaffItemSerializer(serializers.ModelSerializer):
    menu_detail = serializers.SerializerMethodField(read_only=True)
    menu_id = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all())

    class Meta:
        model = OrderItem
        fields = ['menu_id', 'menu_detail', 'quantity', 'extra_product']

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
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    table = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, allow_blank=False, write_only=True)
    order_type = serializers.ChoiceField(choices=Order.TYPE_CHOICES, allow_blank=False, write_only=True)

    class Meta:
        model = Order
        fields = ['items', 'total_price', 'order_type', 'table', 'waiter', 'status']
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        validated_data['Официант'] = self.context['request'].user

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])

        # Обновляем поля заказа
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.waiter = validated_data.get('waiter', instance.waiter)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Обрабатываем изменения в пунктах заказа
        existing_items = {item.id: item for item in instance.items.all()}
        updated_items = {}

        # Обновляем или добавляем новые пункты заказа
        for item_data in items_data:
            item_id = item_data.get('id')
            menu_id = item_data.get('menu_id', None)
            new_quantity = item_data.get('quantity', 0)

            if item_id and item_id in existing_items:
                # Если ID предоставлен и элемент существует, обновляем количество
                item = existing_items[item_id]
                additional_quantity = new_quantity - item.quantity
                item.quantity = new_quantity
                item.save()
                updated_items[item_id] = item
                # Обновляем ингредиенты на складе для дополнительного количества
                if additional_quantity > 0:
                    update_ingredient_storage_on_cooking(menu_id, instance.branch.id, additional_quantity)
            else:
                # Проверяем, существует ли уже пункт заказа с таким же меню
                item = instance.items.filter(menu_id=menu_id).first()
                if item:
                    # Увеличиваем количество существующего пункта
                    additional_quantity = new_quantity
                    item.quantity += additional_quantity
                    item.save()
                else:
                    # Создаем новый пункт заказа
                    item = OrderItem.objects.create(order=instance, menu_id=menu_id, quantity=new_quantity)
                    additional_quantity = new_quantity
                updated_items[item.id] = item
                # Обновляем ингредиенты на складе для нового или увеличенного количества
                if additional_quantity > 0:
                    update_ingredient_storage_on_cooking(menu_id, instance.branch.id, additional_quantity)


        # Пересчитываем общую стоимость заказа
        total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
        instance.total_price = total_price

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
        instance.bonuses_used = validated_data.get('bonuses_used', instance.bonuses_used)
        instance.save()

        # Обрабатываем изменения в пунктах заказа
        for item_data in items_data:

            menu_id = item_data.get('menu_id')
            new_quantity = item_data.get('quantity')



            if not menu_id:
                raise serializers.ValidationError({'menu_id': 'Menu ID is required.'})

            try:
                menu_item = Menu.objects.get(id=menu_id)
            except Menu.DoesNotExist:
                raise serializers.ValidationError({'menu_id': 'Menu item does not exist.'})

            # Поиск существующего OrderItem
            item = instance.items.filter(menu=menu_item).first()

            if item:
                # Если пункт заказа уже существует, прибавляем новое количество к существующему
                item.quantity += new_quantity
                item.save()
            else:
                # Если пункта заказа нет, создаем новый с указанным количеством
                OrderItem.objects.create(order=instance, menu=menu_item, quantity=new_quantity)

            # Обновляем ингредиенты на складе для добавленного количества
            if new_quantity > 0:
                update_ingredient_storage_on_cooking(menu_id, instance.branch.id, new_quantity)

        instance.bonuses_used = validated_data.get('bonuses_used', 0)
        if instance.bonuses_used > instance.user.bonus:
            raise serializers.ValidationError("Недостаточно бонусов.")
        # Логика начисления бонусов при изменении статуса заказа, если необходимо
        if instance.status == "Завершено" and not instance.bonuses_applied:
            instance.user.bonus += instance.total_price  # Начисляем бонусы
            instance.bonuses_applied = True  # Флаг, предотвращающий повторное начисление
            total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
            instance.total_price = total_price - instance.bonuses_used
            instance.user.save()

        return instance