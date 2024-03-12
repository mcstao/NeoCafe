from django.contrib.auth import get_user_model
from rest_framework import serializers

from menu.models import Menu
from menu.serializers import CategorySerializer
from orders.models import OrderItem
from orders.serializers import OrderHistorySerializer
from services.customer.order import get_my_opened_orders_data, get_my_closed_orders_data

User = get_user_model()


class CustomerProfileSerializer(serializers.ModelSerializer):
    orders = OrderHistorySerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "birth_date",
            "bonus",
            "orders"
        )


class CustomerEditProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(read_only=True)
    birth_date = serializers.DateField(required=True)


class ChangeBranchSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField()


from rest_framework import serializers
from menu.models import Menu

class MenuSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        model = Menu
        fields = ['id', 'name', 'price', 'image', 'available', 'category']


class MenuItemDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'description', 'price', 'image', 'ingredients', 'available', 'category']

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        return [{'id': ingredient.id, 'name': ingredient.name, 'quantity': ingredient.quantity,
                 'measurement_unit': ingredient.measurement_unit} for ingredient in ingredients]


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='menu.name')
    item_price = serializers.DecimalField(source='menu.price', max_digits=7, decimal_places=2)
    item_total_price = serializers.SerializerMethodField()
    item_image = serializers.ImageField(source='menu.image', required=False)
    item_id = serializers.IntegerField(source='menu.id')
    item_category = serializers.CharField(source='menu.category.name')
    extra_product_names = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'item_name', 'item_price', 'menu_quantity', 'item_total_price', 'item_image', 'item_id', 'item_category', 'extra_product_names']

    def get_item_total_price(self, obj):
        return obj.menu.price * obj.menu_quantity

    def get_extra_product_names(self, obj):
        return [extra_item.name for extra_item in obj.extra_product.all()]


class UserOrdersSerializer(serializers.Serializer):
    opened_orders = serializers.SerializerMethodField()
    closed_orders = serializers.SerializerMethodField()

    class Meta:
        fields = ["opened_orders", "closed_orders"]

    def get_opened_orders(self, obj):
        orders = get_my_opened_orders_data(obj)
        return OrderHistorySerializer(orders, many=True).data

    def get_closed_orders(self, obj):
        orders = get_my_closed_orders_data(obj)
        return OrderHistorySerializer(orders, many=True).data