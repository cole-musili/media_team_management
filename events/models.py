from django.conf import settings
from django.db import models


class Event(models.Model):

    TYPES = [
        ("service", "Sunday/Church Service"),
        ("wedding", "Wedding"),
        ("conference", "Conference"),
        ("youth", "Youth Event"),
        ("special", "Special Event"),
        ("other", "Other"),
    ]

    STATUS = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=200)

    event_type = models.CharField(
        max_length=30,
        choices=TYPES,
        default="service",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="scheduled",
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField(
        null=True,
        blank=True,
    )

    call_time = models.TimeField(
        null=True,
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_media_events",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.name} - {self.date}"