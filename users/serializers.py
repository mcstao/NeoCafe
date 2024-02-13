from rest_framework import serializers

from users.models import CustomUser


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email"]

    def create(self, validated_data):
        validated_data["position"] = "client"
        return CustomUser.objects.create(**validated_data)


class CustomerLoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ["phone_number"]


class CustomerOtpSerializer(serializers.ModelSerializer):
    otp = serializers.ImageField()

    class Meta:
        model = CustomUser
        fields = ["otp"]


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class WaiterLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
