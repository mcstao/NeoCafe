from django.core.validators import MinLengthValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, default="Выпечка", unique=True, validators=[
                            MinLengthValidator(3)])
    image = models.ImageField(upload_to='menu/images', verbose_name="Фото категории", null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Menu(models.Model):

    CATEGORY_CHOICES = [
        ("Готовые продукты", "Готовые продукты"),
        ("Сырье", "Сырье"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название")
    image = models.ImageField(upload_to='menu/images', verbose_name="Фото блюда", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 verbose_name='Категория', null=True
                                 )
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")
    available = models.BooleanField(default=True, verbose_name="В наличии")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    meal_type = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, verbose_name="Тип блюда"
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["-created"]),
        ]
        verbose_name_plural = "Меню"

    def __str__(self):
        return f"{self.category}: {self.name}"


class ExtraItem(models.Model):
    MILK = 'Milk'
    SYRUP = 'Syrup'
    TYPE_CHOICES = [
        (MILK, 'Молоко'),
        (SYRUP, 'Сиропы')
    ]

    choice_category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="extra_products", null=True
    )
    type_extra_product = models.CharField(
        max_length=20, choices=TYPE_CHOICES, null=True, verbose_name="Доп. Продукт"
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Название доп. продукта")
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Доп. Продукты"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    MEASUREMENT_UNIT_CHOICES = [
        ('гр', 'гр'),
        ('кг', 'кг'),
        ('мл', 'мл'),
        ('л', 'л'),
        ('шт', 'шт')
    ]

    menu_item = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=225)
    quantity = models.PositiveIntegerField()
    measurement_unit = models.CharField(
        max_length=15, choices=MEASUREMENT_UNIT_CHOICES)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Состав блюда"

    def __str__(self):
        return f"{self.name} ({self.quantity}{self.measurement_unit})"


class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.name} ({self.quantity})"
