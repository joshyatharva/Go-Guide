# Generated by Django 3.2 on 2021-04-24 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0021_alter_guide_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='guide',
            name='rating',
            field=models.FloatField(default=0),
        ),
    ]