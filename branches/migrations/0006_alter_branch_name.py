# Generated by Django 4.2.10 on 2024-03-07 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0005_alter_branch_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]