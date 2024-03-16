from rest_framework import serializers
from branches.models import Branch
from menu.models import Menu, ExtraItem
from .models import Order, OrderItem
from django.db import transaction


class OrderMenuHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["image", "name", "description", "price"]


class OrderExtraProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraItem
        fields = ["name", "price"]


class MTOSerializer(serializers.ModelSerializer):
    menu_detail = OrderMenuHistorySerializer(source="menu", read_only=True)
    extra_product_detail = OrderExtraProductSerializer(
        source="extra_product", read_only=True, many=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_detail",
            "menu",
            "menu_quantity",
            "extra_product",
            "extra_product_detail",
            "extra_product_quantity",
        ]


class OrderSerializer(serializers.ModelSerializer):
    cashback = serializers.SerializerMethodField()
    items = MTOSerializer(many=True)

    def get_cashback(self, obj):
        return obj.apply_cashback()

    class Meta:
        model = Order
        fields = [
            "id",
            "order_type",
            "branch",
            "user",
            "bonuses_used",
            "created",
            "total_price",
            "cashback",
            "items",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        bonuses_amount = validated_data.pop("bonuses_used", 0)

        try:
            with transaction.atomic():
                order = Order.objects.create(**validated_data)

                for item in items_data:
                    extra_product_datas = item.pop("extra_product", [])
                    order_item = OrderItem.objects.create(order=order, **item)
                    for extra_product_id in extra_product_datas:
                        extra_product = ExtraItem.objects.get(id=extra_product_id)
                        order_item.extra_product.add(extra_product)

                if bonuses_amount > 0:
                    order.apply_bonuses(bonuses_amount)
        except Exception as e:
            raise e

        return order


class OrderBranchInHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ("image", "name")


class OrderHistorySerializer(serializers.ModelSerializer):
    branch = OrderBranchInHistorySerializer()
    items = MTOSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "branch",
            "bonuses_used",
            "created",
            "items",
        ]


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
    is_dine_in = serializers.BooleanField(required=True)
    table = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = ['items', 'total_price', 'bonuses_used', 'is_dine_in', 'table']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
