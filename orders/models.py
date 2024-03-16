from decimal import Decimal

from django.db import models
from django.conf import settings
from menu.models import Menu, ExtraItem
from branches.models import Branch
from users.models import CustomUser
from services.orders.ord_services import OrderService


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
        limit_choices_to={"position": "waiter"},
    )
    created = models.DateTimeField(auto_now_add=True)

    def apply_cashback(self):
        return OrderService.apply_cashback(self)

    def apply_bonuses(self, bonuses_amount):
        return OrderService.apply_bonuses(self, bonuses_amount)

    def set_in_process(self):
        return OrderService.set_in_process(self)

    def set_completed(self):
        return OrderService.set_completed(self)

    def set_cancelled(self):
        return OrderService.set_cancelled(self)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="order_items")
    menu_quantity = models.PositiveIntegerField(default=1)
    extra_product = models.ManyToManyField(
        ExtraItem,
        blank=True,
        related_name="extra_order",
    )
    extra_product_quantity = models.PositiveIntegerField(default=0)

    def get_cost(self):
        menu_cost = (
            max(Decimal("0"), self.menu.price) * self.menu_quantity
            if self.menu
            else Decimal("0")
        )
        extra_cost = (
            max(Decimal("0"), self.extra_product.price) * self.extra_product_quantity
            if self.extra_product
            else Decimal("0")
        )
        return menu_cost + extra_cost
