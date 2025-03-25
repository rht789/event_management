# Generated by Django 5.1.6 on 2025-03-25 16:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=30)),
                ("description", models.TextField()),
                ("color", models.CharField(default="#000000", max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name="Event",
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
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                ("location", models.CharField(blank=True, null=True)),
                (
                    "assets",
                    models.ImageField(
                        blank=True,
                        default="events_asset/default.jpg",
                        null=True,
                        upload_to="events_asset",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="events.category",
                    ),
                ),
            ],
        ),
    ]
