# Generated by Django 5.1.7 on 2025-03-18 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="habit",
            name="habit_best_streak",
            field=models.IntegerField(default=0),
        ),
    ]
