# Generated by Django 4.2.10 on 2024-03-28 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0009_remove_menu_meal_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extraitem',
            name='price',
        ),
    ]
