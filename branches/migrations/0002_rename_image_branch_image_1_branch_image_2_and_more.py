# Generated by Django 4.2.10 on 2024-03-05 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='branch',
            old_name='image',
            new_name='image_1',
        ),
        migrations.AddField(
            model_name='branch',
            name='image_2',
            field=models.ImageField(blank=True, null=True, upload_to='branches/images'),
        ),
        migrations.AddField(
            model_name='branch',
            name='image_3',
            field=models.ImageField(blank=True, null=True, upload_to='branches/images'),
        ),
        migrations.AddField(
            model_name='branch',
            name='image_4',
            field=models.ImageField(blank=True, null=True, upload_to='branches/images'),
        ),
        migrations.AddField(
            model_name='branch',
            name='image_5',
            field=models.ImageField(blank=True, null=True, upload_to='branches/images'),
        ),
    ]
