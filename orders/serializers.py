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
    bonuses_used = serializers.IntegerField(required=False)
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

        existing_items = {item.id: item for item in instance.items.all()}
        updated_items = {}

        # Обновляем или добавляем новые пункты заказа
        for item_data in items_data:
            item_id = item_data.get('id')
            menu_id = item_data.get('menu').id

            if item_id in existing_items:
                # Если ID предоставлен и элемент существует, обновляем количество
                item = existing_items[item_id]
                item.quantity = item_data.get('quantity', item.quantity)
                item.save()
                updated_items[item_id] = item
            else:
                # Проверяем, существует ли уже пункт заказа с таким же меню
                item = instance.items.filter(menu_id=menu_id).first()
                if item:
                    # Увеличиваем количество существующего пункта
                    item.quantity += item_data.get('quantity', 0)
                    item.save()
                else:
                    # Создаем новый пункт заказа
                    item = OrderItem.objects.create(order=instance, **item_data)
                updated_items[item.id] = item


        # Пересчитываем общую стоимость заказа
        total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
        instance.total_price = total_price - instance.bonuses_used

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
        instance.bonuses_used = validated_data.data.get('bonuses_used', instance.bonuses_used)
        instance.save()

        # Обрабатываем изменения в пунктах заказа
        existing_items = {item.id: item for item in instance.items.all()}
        updated_items = {}

        # Обновляем или добавляем новые пункты заказа
        for item_data in items_data:
            item_id = item_data.get('id')
            menu_id = item_data.get('menu').id

            if item_id in existing_items:
                # Если ID предоставлен и элемент существует, обновляем количество
                item = existing_items[item_id]
                item.quantity = item_data.get('quantity', item.quantity)
                item.save()
                updated_items[item_id] = item
            else:
                # Проверяем, существует ли уже пункт заказа с таким же меню
                item = instance.items.filter(menu_id=menu_id).first()
                if item:
                    # Увеличиваем количество существующего пункта
                    item.quantity += item_data.get('quantity', 0)
                    item.save()
                else:
                    # Создаем новый пункт заказа
                    item = OrderItem.objects.create(order=instance, **item_data)
                updated_items[item.id] = item

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