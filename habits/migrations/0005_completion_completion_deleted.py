# Generated by Django 5.1.7 on 2025-03-20 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "habits",
            "0004_rename_completion_habit_completion_completion_habit_id_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="completion",
            name="completion_deleted",
            field=models.BooleanField(default=False),
        ),
    ]
