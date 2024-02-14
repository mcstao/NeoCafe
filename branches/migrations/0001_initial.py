

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('monday', models.BooleanField(default=False)),
                ('monday_start_time', models.TimeField(blank=True, null=True)),
                ('monday_end_time', models.TimeField(blank=True, null=True)),
                ('tuesday', models.BooleanField(default=False)),
                ('tuesday_start_time', models.TimeField(blank=True, null=True)),
                ('tuesday_end_time', models.TimeField(blank=True, null=True)),
                ('wednesday', models.BooleanField(default=False)),
                ('wednesday_start_time', models.TimeField(blank=True, null=True)),
                ('wednesday_end_time', models.TimeField(blank=True, null=True)),
                ('thursday', models.BooleanField(default=False)),
                ('thursday_start_time', models.TimeField(blank=True, null=True)),
                ('thursday_end_time', models.TimeField(blank=True, null=True)),
                ('friday', models.BooleanField(default=False)),
                ('friday_start_time', models.TimeField(blank=True, null=True)),
                ('friday_end_time', models.TimeField(blank=True, null=True)),
                ('saturday', models.BooleanField(default=False)),
                ('saturday_start_time', models.TimeField(blank=True, null=True)),
                ('saturday_end_time', models.TimeField(blank=True, null=True)),
                ('sunday', models.BooleanField(default=False)),
                ('sunday_start_time', models.TimeField(blank=True, null=True)),
                ('sunday_end_time', models.TimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='branches/images')),
                ('name', models.CharField(default='NeoCafe', max_length=100)),
                ('address', models.TextField()),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('link_to_map', models.URLField()),
                ('counts_of_tables', models.PositiveSmallIntegerField(default=0)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branch', to='branches.schedule')),
            ],
        ),
    ]
