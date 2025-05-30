# Generated by Django 5.1.7 on 2025-04-25 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_project_is_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='name_en',
            field=models.CharField(blank=True, max_length=100, verbose_name='Name (English)'),
        ),
        migrations.AddField(
            model_name='category',
            name='name_kk',
            field=models.CharField(blank=True, max_length=100, verbose_name='Name (Kazakh)'),
        ),
        migrations.AddField(
            model_name='category',
            name='name_ru',
            field=models.CharField(blank=True, max_length=100, verbose_name='Name (Russian)'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name_en',
            field=models.CharField(blank=True, max_length=50, verbose_name='Name (English)'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name_kk',
            field=models.CharField(blank=True, max_length=50, verbose_name='Name (Kazakh)'),
        ),
        migrations.AddField(
            model_name='tag',
            name='name_ru',
            field=models.CharField(blank=True, max_length=50, verbose_name='Name (Russian)'),
        ),
    ]
