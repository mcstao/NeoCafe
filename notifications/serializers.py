from rest_framework import serializers
from .models import Notification


class UserNotificationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'