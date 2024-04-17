from django.db import models

from branches.models import Branch
from orders.models import Order
from storage.models import InventoryItem
from users.models import CustomUser


class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    read = models.BooleanField(default=False)
    table = models.CharField(blank=True, default="", max_length=20)

    recipient = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.title} - {self.status}"