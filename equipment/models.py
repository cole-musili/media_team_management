from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from members.models import Member
from events.models import Event


class EquipmentCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    def __str__(self):
        return self.name


class Equipment(models.Model):

    STATUS = [
        ("available", "Available"),
        ("in_use", "In Use"),
        ("reserved", "Reserved"),
        ("maintenance", "Under Maintenance"),
        ("damaged", "Damaged"),
        ("missing", "Missing"),
    ]

    CONDITION = [
        ("excellent", "Excellent"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
    ]

    equipment_id = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
    )

    category = models.ForeignKey(
        EquipmentCategory,
        on_delete=models.PROTECT,
        related_name="equipment",
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
    )

    model = models.CharField(
        max_length=100,
        blank=True,
    )

    serial_number = models.CharField(
        max_length=150,
        blank=True,
    )

    purchase_date = models.DateField(
        null=True,
        blank=True,
    )

    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    condition = models.CharField(
        max_length=20,
        choices=CONDITION,
        default="good",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="available",
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    photo = models.ImageField(
        upload_to="equipment/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.equipment_id} - {self.name}"


class EquipmentPhoto(models.Model):

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(
        upload_to="equipment/photos/",
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.equipment.equipment_id} photo"


class Checkout(models.Model):

    STATUS = [
        ("out", "Checked Out"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name="checkouts",
    )

    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="equipment_checkouts",
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipment_checkouts",
    )

    purpose = models.TextField()

    checkout_time = models.DateTimeField()

    expected_return = models.DateTimeField(
        null=True,
        blank=True,
    )

    return_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    condition_before = models.CharField(
        max_length=20,
        choices=Equipment.CONDITION,
        default="good",
    )

    condition_after = models.CharField(
        max_length=20,
        choices=Equipment.CONDITION,
        null=True,
        blank=True,
    )

    photo_before = models.ImageField(
        upload_to="checkouts/before/",
        blank=True,
        null=True,
    )

    photo_after = models.ImageField(
        upload_to="checkouts/after/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="out",
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["equipment"],
                condition=Q(
                    status__in=["out", "overdue"]
                ),
                name="one_active_checkout_per_equipment",
            ),
        ]

        ordering = [
            "-checkout_time",
        ]

    def clean(self):

        errors = {}

        if not self.member.is_active:
            errors["member"] = (
                "An inactive member cannot check out equipment."
            )

        if (
            self.status == "returned"
            and not self.return_time
        ):
            errors["return_time"] = (
                "A returned item must have a return time."
            )

        if self.status in ["out", "overdue"]:

            existing = (
                Checkout.objects
                .filter(
                    equipment=self.equipment,
                    status__in=["out", "overdue"],
                )
                .exclude(pk=self.pk)
            )

            if existing.exists():

                errors["equipment"] = (
                    "This equipment is already checked out."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):

        return (
            f"{self.equipment} - "
            f"{self.member} - "
            f"{self.status}"
        )


class MaintenanceRecord(models.Model):

    STATUS = [
        ("reported", "Reported"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="maintenance",
    )

    reported_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    problem = models.TextField()

    reported_date = models.DateField()

    provider = models.CharField(
        max_length=150,
        blank=True,
    )

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    completed_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="reported",
    )

    notes = models.TextField(
        blank=True,
    )

    def __str__(self):

        return (
            f"{self.equipment} - "
            f"{self.problem[:30]}"
        )