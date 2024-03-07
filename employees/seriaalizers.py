from rest_framework import serializers
from users.models import CustomUser
from users.models import EmployeeSchedule


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSchedule
        fields = '__all__'


class StaffCreateSerializer(serializers.ModelSerializer):
    schedule = EmployeeScheduleSerializer()

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "password",
            "first_name",
            "birth_date",
            "branch",
            "position",
            "schedule",
        ]

    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule')
        user = CustomUser.objects.create(**validated_data)
        schedule = EmployeeSchedule.objects.create(**schedule_data)
        user.schedule = schedule
        user.save()
        return user
