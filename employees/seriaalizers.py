from rest_framework import serializers
from users.models import CustomUser
from users.models import EmployeeSchedule


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSchedule
        fields = [
            "monday",
            "monday_start_time",
            "monday_end_time",
            "tuesday",
            "tuesday_start_time",
            "tuesday_end_time",
            "wednesday",
            "wednesday_start_time",
            "wednesday_end_time",
            "thursday",
            "thursday_start_time",
            "thursday_end_time",
            "friday",
            "friday_start_time",
            "friday_end_time",
            "saturday",
            "saturday_start_time",
            "saturday_end_time",
            "sunday",
            "sunday_start_time",
            "sunday_end_time",
        ]


class StaffCreateSerializer(serializers.ModelSerializer):
    schedule = EmployeeScheduleSerializer()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "position",
            "email",
            "username",
            "password",
            "first_name",
            "birth_date",
            "branch",
            "schedule",
        ]

    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule')
        user = CustomUser.objects.create(**validated_data)
        schedule = EmployeeSchedule.objects.create(**schedule_data)
        user.schedule = schedule
        user.save()
        return user
