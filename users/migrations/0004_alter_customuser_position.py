# Generated by Django 4.2.10 on 2024-03-12 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_customuser_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='position',
            field=models.CharField(choices=[('Бармен', 'Бармен'), ('Официант', 'Официант'), ('Клиент', 'Клиент'), ('Админ', 'Админ')], default='Клиент', max_length=255),
        ),
    ]
