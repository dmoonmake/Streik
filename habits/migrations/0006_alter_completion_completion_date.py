# Generated by Django 5.1.7 on 2025-03-25 06:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("habits", "0005_completion_completion_deleted"),
    ]

    operations = [
        migrations.AlterField(
            model_name="completion",
            name="completion_date",
            field=models.DateTimeField(default=datetime.date.today),
        ),
    ]
