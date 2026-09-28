from django.core.exceptions import ValidationError
from django.db import models

from members.models import Member, Skill
from events.models import Event


class DutyPosition(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    required_skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="duty_positions",
    )

    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name


class DutyAssignment(models.Model):

    STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("declined", "Declined"),
        ("replaced", "Replaced"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    position = models.ForeignKey(
        DutyPosition,
        on_delete=models.PROTECT,
        related_name="assignments",
    )

    slot = models.CharField(
        max_length=100,
        default="Main",
        help_text=(
            "Specific duty slot, e.g. Camera 1, "
            "Camera 2, Main or Backup."
        ),
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="duty_assignments",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )

    decline_reason = models.TextField(
        blank=True,
    )

    replacement_for = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replacement",
    )

    notes = models.TextField(
        blank=True,
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "position", "slot"],
                name="one_member_per_event_position_slot",
            ),
        ]

        ordering = [
            "event__date",
            "position__name",
            "slot",
        ]

    def clean(self):

        errors = {}

        if not self.member.is_active:
            errors["member"] = (
                "An inactive member cannot be assigned "
                "to a duty."
            )

        duplicate = DutyAssignment.objects.filter(
            event=self.event,
            member=self.member,
        ).exclude(
            pk=self.pk
        )

        if duplicate.exists():
            errors["member"] = (
                "This member is already assigned to "
                "another duty for this event."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):

        return (
            f"{self.event} - "
            f"{self.position} ({self.slot}) - "
            f"{self.member}"
        )