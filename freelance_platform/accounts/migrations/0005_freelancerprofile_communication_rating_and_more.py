# Generated by Django 5.1.8 on 2025-05-21 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_dark_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='freelancerprofile',
            name='communication_rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Communication Rating'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='cost_rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Value for Money Rating'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='deadline_rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Deadline Adherence Rating'),
        ),
        migrations.AddField(
            model_name='freelancerprofile',
            name='quality_rating',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Quality Rating'),
        ),
        migrations.CreateModel(
            name='ReviewDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality_rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Quality Rating')),
                ('communication_rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Communication Rating')),
                ('deadline_rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Deadline Adherence Rating')),
                ('cost_rating', models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='Value for Money Rating')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='accounts.review')),
            ],
        ),
    ]
