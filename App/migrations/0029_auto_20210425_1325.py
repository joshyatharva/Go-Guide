# Generated by Django 3.2 on 2021-04-25 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0028_alter_booking_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='guide',
            name='bio',
            field=models.TextField(default='Apparently, this user prefers to keep an air of mystery about them.'),
        ),
        migrations.AddField(
            model_name='guide',
            name='fb',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='guide',
            name='insta',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='guide',
            name='twitter',
            field=models.URLField(blank=True, null=True),
        ),
    ]
