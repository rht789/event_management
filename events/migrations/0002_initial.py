# Generated by Django 5.1.6 on 2025-03-25 16:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("events", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="organizer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="events_organized",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="participant",
            field=models.ManyToManyField(
                blank=True, related_name="rsvp_events", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
