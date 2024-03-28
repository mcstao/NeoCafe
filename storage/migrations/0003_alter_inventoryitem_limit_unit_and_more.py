# Generated by Django 4.2.10 on 2024-03-28 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_inventoryitem_limit_unit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='limit_unit',
            field=models.CharField(choices=[('кг', 'кг'), ('гр', 'гр'), ('л', 'л'), ('мл', 'мл'), ('шт', 'шт')], max_length=20, verbose_name='Единица измерения (Количество)'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='quantity_unit',
            field=models.CharField(choices=[('кг', 'кг'), ('гр', 'гр'), ('л', 'л'), ('мл', 'мл'), ('шт', 'шт')], max_length=20, verbose_name='Единица измерения (Количество)'),
        ),
    ]
