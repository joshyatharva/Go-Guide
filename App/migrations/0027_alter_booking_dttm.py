# Generated by Django 3.2 on 2021-04-25 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0026_booking_dttm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='dttm',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]