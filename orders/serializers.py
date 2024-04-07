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
from services.menu.menu import update_ingredient_storage_on_cooking, update_extra_product_storage
from users.models import CustomUser
from .models import Order, OrderItem, Table, OrderItemExtraProduct

logger = logging.getLogger(__name__)


class ExtraProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderItemExtraProduct
        fields = ['id', 'quantity']


class OrderStaffItemSerializer(serializers.ModelSerializer):
    menu_detail = serializers.SerializerMethodField(read_only=True)
    menu_id = serializers.IntegerField()
    extra_product = ExtraProductSerializer(source='orderitemextraproduct_set', many=True, required=False)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_id', 'menu_detail', 'quantity', 'extra_product']


    @extend_schema_field(serializers.CharField())
    def get_menu_detail(self, obj):
        return MenuSerializer(obj.menu).data


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['extra_product'] = ExtraProductSerializer(instance.orderitemextraproduct_set.all(), many=True).data
        return representation

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
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), required=False, allow_null=True)
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, allow_blank=False)
    order_type = serializers.ChoiceField(choices=Order.TYPE_CHOICES, allow_blank=False)
    created = serializers.DateTimeField(required=False, format="%d.%m.%Y %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(required=False, format="%d.%m.%Y %H:%M", read_only=True)
    completed_at = serializers.DateTimeField(allow_null=True, required=False, format="%d.%m.%Y %H:%M", read_only=True)
    bonuses_used = serializers.IntegerField(required=False, allow_null=True, min_value=0)

    class Meta:
        model = Order
        fields = ['id', 'items', 'total_price', 'order_type', 'table', 'waiter', 'status', 'branch', 'created',
                  'updated_at', 'completed_at', 'user', 'bonuses_used']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        table_id = validated_data.pop('table', None)
        print(f"Current user: {self.context['request'].user}")
        waiter = self.context['request'].user
        order_type = validated_data.get('order_type')



        table = Table.objects.get(id=table_id) if table_id else None

        if table and not table.is_available:
            raise serializers.ValidationError({"table": "Стол не доступен."})

        if order_type == "В заведении" and table:
            table.is_available = False
            table.save()

        order = Order.objects.create(**validated_data, waiter=waiter, table=table)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)


        return order

    def update(self, instance, validated_data):
        print(f"Received data for update: {validated_data}")
        items_data = validated_data.pop('items', [])

        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.waiter = validated_data.get('waiter', instance.waiter)
        instance.status = validated_data.get('status', instance.status)


        for item_data in items_data:
            menu_id = item_data['menu_id']
            new_quantity = item_data['quantity']

            menu_item = Menu.objects.get(id=menu_id)

            item = instance.items.filter(menu=menu_item).first()

            if item:

                item.quantity += new_quantity
                item.save()

            else:
                OrderItem.objects.create(order=instance, menu=menu_item, quantity=new_quantity)
            extra_products_data = item_data.pop('orderitemextraproduct_set', [])
            print(f"Extra products data: {extra_products_data}")

            for extra_product_data in extra_products_data:
                extra_product_id = extra_product_data['id']
                extra_product_quantity = extra_product_data['quantity']

                print(f"Processing extra product ID: {extra_product_id} with quantity: {extra_product_quantity}")

                extra = ExtraItem.objects.get(id=extra_product_id)
                print(f"Retrieved ExtraItem: {extra}")

                extra_product = OrderItemExtraProduct.objects.filter(
                    order_item=item,
                    extra_product=extra
                ).first()

                if extra_product:
                    print(
                        f"Found existing OrderItemExtraProduct: {extra_product} with current quantity: {extra_product.quantity}. Updating quantity.")
                    extra_product.quantity += extra_product_quantity
                    extra_product.save()
                    print(f"Updated quantity: {extra_product.quantity}")
                else:
                    print(
                        f"Creating new OrderItemExtraProduct for ExtraItem ID: {extra_product_id} with quantity: {extra_product_quantity}")
                    OrderItemExtraProduct.objects.create(
                        order_item=item,
                        extra_product=extra,
                        quantity=extra_product_quantity
                    )
                    print("OrderItemExtraProduct created.")

                if extra_product_quantity > 0:
                    print(
                        f"Calling update_extra_product_storage for ExtraItem ID: {extra_product_id} with quantity: {extra_product_quantity}")
                    update_extra_product_storage(extra_product_id, instance.branch.id, extra_product_quantity)
                    print("update_extra_product_storage called.")



            if new_quantity > 0:
                update_ingredient_storage_on_cooking(menu_id, instance.branch.id, new_quantity)

        total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
        instance.total_price = max(total_price - instance.bonuses_used, Decimal(0))

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
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, allow_blank=False)
    order_type = serializers.ChoiceField(choices=Order.TYPE_CHOICES, allow_blank=False)
    created = serializers.DateTimeField(required=False, format="%d.%m.%Y %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(required=False, format="%d.%m.%Y %H:%M", read_only=True)
    completed_at = serializers.DateTimeField(allow_null=True, required=False, format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'items', 'total_price', 'bonuses_used', 'order_type', 'user', 'status', 'branch',
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


        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.table = validated_data.get('table', instance.table)
        instance.status = validated_data.get('status', instance.status)
        instance.bonuses_used = validated_data.get('bonuses_used', instance.bonuses_used)

        if instance.bonuses_used > instance.user.bonus:
            raise serializers.ValidationError("Недостаточно бонусов у пользователя.")

        for item_data in items_data:
            menu_id = item_data['menu_id']
            new_quantity = item_data['quantity']

            menu_item = Menu.objects.get(id=menu_id)

            item = instance.items.filter(menu=menu_item).first()

            if item:

                item.quantity += new_quantity
                item.save()

            else:
                OrderItem.objects.create(order=instance, menu=menu_item, quantity=new_quantity)

            extra_products_data = item_data.pop('orderitemextraproduct_set', [])
            print(f"Extra products data: {extra_products_data}")

            for extra_product_data in extra_products_data:
                extra_product_id = extra_product_data['id']
                extra_product_quantity = extra_product_data['quantity']

                print(f"Processing extra product ID: {extra_product_id} with quantity: {extra_product_quantity}")

                extra = ExtraItem.objects.get(id=extra_product_id)
                print(f"Retrieved ExtraItem: {extra}")

                extra_product = OrderItemExtraProduct.objects.filter(
                    order_item=item,
                    extra_product=extra
                ).first()

                if extra_product:
                    print(
                        f"Found existing OrderItemExtraProduct: {extra_product} with current quantity: {extra_product.quantity}. Updating quantity.")
                    extra_product.quantity += extra_product_quantity
                    extra_product.save()
                    print(f"Updated quantity: {extra_product.quantity}")
                else:
                    print(
                        f"Creating new OrderItemExtraProduct for ExtraItem ID: {extra_product_id} with quantity: {extra_product_quantity}")
                    OrderItemExtraProduct.objects.create(
                        order_item=item,
                        extra_product=extra,
                        quantity=extra_product_quantity
                    )
                    print("OrderItemExtraProduct created.")

                if extra_product_quantity > 0:
                    print(
                        f"Calling update_extra_product_storage for ExtraItem ID: {extra_product_id} with quantity: {extra_product_quantity}")
                    update_extra_product_storage(extra_product_id, instance.branch.id, extra_product_quantity)
                    print("update_extra_product_storage called.")

            if new_quantity > 0:
                update_ingredient_storage_on_cooking(menu_id, instance.branch.id, new_quantity)

        total_price = sum(item.menu.price * item.quantity for item in instance.items.all())
        instance.total_price = max(total_price - instance.bonuses_used, Decimal(0))

        if instance.bonuses_used > instance.user.bonus:
            raise serializers.ValidationError("Недостаточно бонусов.")

        if instance.status == "Завершено":
            instance.user.bonus -= instance.bonuses_used
            instance.user.bonus += instance.total_price
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
