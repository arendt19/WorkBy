# Generated by Django 5.1.7 on 2025-04-19 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dark_mode',
            field=models.BooleanField(default=True, verbose_name='Dark Mode'),
        ),
    ]
