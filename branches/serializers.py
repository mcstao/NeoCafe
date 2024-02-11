from rest_framework import serializers
from .models import Schedule, Branch


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer()

    class Meta:
        model = Branch
        fields = '__all__'

    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule')
        schedule = Schedule.objects.create(**schedule_data)
        branch = Branch.objects.create(schedule=schedule, **validated_data)
        return branch
