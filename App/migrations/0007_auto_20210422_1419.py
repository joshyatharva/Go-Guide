# Generated by Django 3.2 on 2021-04-22 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0006_guide_charges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destination',
            name='destination_image',
            field=models.ImageField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.BooleanField(choices=[(0, 'on'), (1, 'off')], default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.BooleanField(choices=[(True, 'on'), (False, 'off')], default=True),
        ),
    ]