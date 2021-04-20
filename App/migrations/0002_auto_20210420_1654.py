# Generated by Django 3.2 on 2021-04-20 16:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='guide',
            old_name='user',
            new_name='user_details',
        ),
        migrations.RenameField(
            model_name='tourist',
            old_name='user',
            new_name='user_details',
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.BooleanField(blank=True, choices=[(0, 'Male'), (1, 'Female')], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')]),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(default='default.png', upload_to=''),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.BooleanField(choices=[(True, 'Tourist'), (False, 'Guide')], default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique='True'),
        ),
    ]
