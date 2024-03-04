from django.contrib.auth import get_user_model
from rest_framework import serializers

from menu.serializers import CategorySerializer
from orders.serializers import OrderHistorySerializer

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
