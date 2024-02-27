from django.contrib.auth import get_user_model
from rest_framework import serializers

from menu.serializers import CategorySerializer

User = get_user_model()


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "birth_date",
            "bonus",
        )



class CustomerEditProfileSerializer(serializers.Serializer):


    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(read_only=True)
    birth_date = serializers.DateField(required=True)

class ChangeBranchSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField()
