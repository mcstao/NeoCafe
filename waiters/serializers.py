from django.contrib.auth import get_user_model
from rest_framework import serializers

from employees.seriaalizers import EmployeeScheduleSerializer
User = get_user_model()



class WaiterProfileSerializer(serializers.ModelSerializer):
    schedule = EmployeeScheduleSerializer(read_only=True)
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "birth_date",
            "schedule",

        )
