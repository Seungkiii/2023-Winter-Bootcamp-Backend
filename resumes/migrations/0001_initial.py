# Generated by Django 4.2.9 on 2024-01-12 05:34

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Resume",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("user_id", models.CharField(max_length=500)),
                ("image_url", models.URLField(max_length=500)),
                ("text_contents", models.TextField()),
            ],
            options={
                "db_table": "resumes",
            },
        ),
    ]
