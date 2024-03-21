from rest_framework import serializers
from .models import Schedule, Branch


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = [
            "title",
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

    def update(self, instance, validated_data):
        schedule_data = validated_data.pop('schedule', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if schedule_data is not None:
            for attr, value in schedule_data.items():
                setattr(instance.schedule, attr, value)
            instance.schedule.save()

        return instance

