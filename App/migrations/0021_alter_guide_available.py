# Generated by Django 3.2 on 2021-04-24 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0020_guide_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guide',
            name='available',
            field=models.BooleanField(default=False),
        ),
    ]
