# Generated by Django 4.2.10 on 2024-03-15 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_order_type_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='table',
            field=models.IntegerField(blank=True, null=True, verbose_name='Номер стола'),
        ),
    ]
