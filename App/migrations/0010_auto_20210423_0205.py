# Generated by Django 3.2 on 2021-04-23 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0009_auto_20210423_0202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.BooleanField(choices=[(0, 0), (1, 1)], default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.BooleanField(choices=[(True, 0), (False, 1)], default=True),
        ),
    ]