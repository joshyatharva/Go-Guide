# Generated by Django 3.2 on 2021-04-23 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0014_auto_20210423_0311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='blog_image',
            field=models.ImageField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=100),
        ),
    ]
