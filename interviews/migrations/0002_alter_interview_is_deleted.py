# Generated by Django 4.2.9 on 2024-01-08 13:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("interviews", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="interview",
            name="is_deleted",
            field=models.BooleanField(),
        ),
    ]
