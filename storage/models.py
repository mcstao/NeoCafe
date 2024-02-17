from django.db import models
from branches.models import Branch


class InventoryItem(models.Model):
    MEASUREMENT_UNIT_CHOICES = [
        ("kg", "кг"),
        ("g", "г"),
        ("l", "л"),
        ("ml", "мл"),
        ("unit", "шт"),
    ]
    CATEGORY_CHOICES = [
        ("ready_products", "Готовые продукты"),
        ("raw_materials", "Сырье"),
    ]

    name = models.CharField(max_length=100, verbose_name="Наименование")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    quantity_unit = models.CharField(
        max_length=20,
        choices=MEASUREMENT_UNIT_CHOICES,
        verbose_name="Единица измерения (Количество)",
    )
    limit = models.PositiveIntegerField(default=0, verbose_name="Лимит")
    arrival_date = models.DateField(verbose_name="Дата прихода")
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория"
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, verbose_name="Филиал"
    )
    is_running_out = models.BooleanField(
        default=False, verbose_name="Заканчивающийся продукт"
    )

    class Meta:
        ordering = ["-arrival_date", "name"]
        verbose_name_plural = "Склад"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) {self.branch}"

    def decrease_stock(self, amount):
        """
        Уменьшить количество товара на складе.
        """
        self.quantity -= amount
        self.save()

    def save(self, *args, **kwargs):
        if self.quantity <= self.limit:
            self.is_running_out = True
        else:
            self.is_running_out = False

        super().save(*args, **kwargs)