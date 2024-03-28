from decimal import Decimal

from django.db import models
from django.conf import settings
from menu.models import Menu, ExtraItem
from branches.models import Branch
from users.models import CustomUser

class Table(models.Model):
    table_number = models.PositiveIntegerField()
    is_available = models.BooleanField(default=False)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Стол:{self.table_number}-Филиал:{self.branch.name}'

class Order(models.Model):
    TYPE_CHOICES = [
        ("На вынос", "На вынос"),
        ("В заведении", "В заведении"),
    ]
    STATUS_CHOICES = [
        ("Новый", "Новый"),
        ("В процессе", "В процессе"),
        ("Готово", "Готово"),
        ("Отменено", "Отменено"),
        ("Завершено", "Завершено"),
    ]

    order_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default="На вынос"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Новый")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="customer_orders",
        null=True,
        blank=True,
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    bonuses_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    waiter = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"position": "Официант"},
    )
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f"Order #{self.pk} - {self.order_type} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    extra_product = models.ManyToManyField(
        ExtraItem,
        blank=True,
        related_name="extra_order",
    )

