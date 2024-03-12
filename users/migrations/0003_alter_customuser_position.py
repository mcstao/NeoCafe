# Generated by Django 4.2.10 on 2024-03-12 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_expiration_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='position',
            field=models.CharField(choices=[('Бармен', 'Бармен'), ('Официант', 'Официант'), ('Клиент', 'Клиент'), ('Админ', 'Админ')], default='client', max_length=255),
        ),
    ]
