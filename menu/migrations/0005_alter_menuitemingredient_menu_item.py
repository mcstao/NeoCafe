# Generated by Django 4.2.10 on 2024-03-05 17:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_alter_category_image_alter_menu_meal_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitemingredient',
            name='menu_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='menu.menu'),
        ),
    ]
