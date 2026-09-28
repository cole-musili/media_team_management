import uuid

from django.db import models

from members.models import Member
from events.models import Event


class Attendance(models.Model):
    STATUS = [
        ("present", "Present"),
        ("late", "Late"),
        ("absent", "Absent"),
        ("excused", "Excused"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attendance",
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="attendance",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="present",
    )

    check_in = models.DateTimeField(
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "member"],
                name="unique_event_member_attendance",
            )
        ]

        ordering = [
            "event__date",
            "member__name",
        ]

    def __str__(self):
        return f"{self.member} - {self.event} - {self.status}"


class AttendanceSession(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attendance_sessions",
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.event} - Attendance Session"