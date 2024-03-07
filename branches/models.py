from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Schedule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    monday = models.BooleanField(default=False)
    monday_start_time = models.TimeField(null=True, blank=True)
    monday_end_time = models.TimeField(null=True, blank=True)

    tuesday = models.BooleanField(default=False)
    tuesday_start_time = models.TimeField(null=True, blank=True)
    tuesday_end_time = models.TimeField(null=True, blank=True)

    wednesday = models.BooleanField(default=False)
    wednesday_start_time = models.TimeField(null=True, blank=True)
    wednesday_end_time = models.TimeField(null=True, blank=True)

    thursday = models.BooleanField(default=False)
    thursday_start_time = models.TimeField(null=True, blank=True)
    thursday_end_time = models.TimeField(null=True, blank=True)

    friday = models.BooleanField(default=False)
    friday_start_time = models.TimeField(null=True, blank=True)
    friday_end_time = models.TimeField(null=True, blank=True)

    saturday = models.BooleanField(default=False)
    saturday_start_time = models.TimeField(null=True, blank=True)
    saturday_end_time = models.TimeField(null=True, blank=True)

    sunday = models.BooleanField(default=False)
    sunday_start_time = models.TimeField(null=True, blank=True)
    sunday_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = "branches"


class Branch(models.Model):
    image = models.ImageField(upload_to="branches/images", blank=True, null=True)
    image_2 = models.ImageField(upload_to="branches/images", blank=True, null=True)
    image_3 = models.ImageField(upload_to="branches/images", blank=True, null=True)
    image_4 = models.ImageField(upload_to="branches/images", blank=True, null=True)
    image_5 = models.ImageField(upload_to="branches/images", blank=True, null=True)

    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="branch"
    )
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = PhoneNumberField()
    link_to_map = models.URLField()
    counts_of_tables = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.name}"
