# Generated by Django 5.1.7 on 2025-03-19 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0002_habit_habit_best_streak"),
    ]

    operations = [
        migrations.AddField(
            model_name="habit",
            name="habit_last_streak",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="habit",
            name="habit_status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("paused", "Paused"),
                    ("inactive", "Inactive"),
                ],
                default="active",
                max_length=10,
            ),
        ),
    ]
