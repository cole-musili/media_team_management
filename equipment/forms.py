from django import forms
from django.utils import timezone

from events.models import Event
from members.models import Member

from .models import (
    Checkout,
    Equipment,
    EquipmentCategory,
    EquipmentPhoto,
    MaintenanceRecord,
)


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = Equipment

        fields = [
            "equipment_id",
            "name",
            "category",
            "brand",
            "model",
            "serial_number",
            "purchase_date",
            "purchase_price",
            "condition",
            "status",
            "location",
            "description",
            "photo",
        ]

        widgets = {
            "equipment_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. CAM-001",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Sony PXW-Z90",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "brand": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "model": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "purchase_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "purchase_price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "condition": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Media Store",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),
            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }


class EquipmentCategoryForm(forms.ModelForm):

    class Meta:
        model = EquipmentCategory

        fields = [
            "name",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Cameras",
                }
            ),
        }


class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Checkout

        fields = [
            "member",
            "event",
            "purpose",
            "expected_return",
            "condition_before",
            "photo_before",
            "notes",
        ]

        widgets = {
            "member": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "event": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "purpose": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Explain why the equipment is "
                        "being checked out..."
                    ),
                }
            ),
            "expected_return": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "condition_before": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "photo_before": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, equipment=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["member"].queryset = (
            Member.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["event"].queryset = (
            Event.objects
            .filter(
                status__in=[
                    "draft",
                    "scheduled",
                ]
            )
            .order_by(
                "date",
                "start_time",
            )
        )

        if equipment:
            self.equipment = equipment

    def clean(self):

        cleaned_data = super().clean()

        if not hasattr(self, "equipment"):
            return cleaned_data

        equipment = self.equipment

        active_checkout = (
            equipment.checkouts
            .filter(
                status__in=[
                    "out",
                    "overdue",
                ]
            )
            .exists()
        )

        if active_checkout:
            raise forms.ValidationError(
                "This equipment is already checked out."
            )

        if equipment.status in [
            "maintenance",
            "damaged",
            "missing",
        ]:
            raise forms.ValidationError(
                "This equipment cannot be checked out while "
                "it is marked as maintenance, damaged or missing."
            )

        return cleaned_data


class ReturnEquipmentForm(forms.ModelForm):

    class Meta:
        model = Checkout

        fields = [
            "return_time",
            "condition_after",
            "photo_after",
            "notes",
        ]

        widgets = {
            "return_time": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "condition_after": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "photo_after": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Describe any issues noticed "
                        "during return..."
                    ),
                }
            ),
        }


class MaintenanceForm(forms.ModelForm):

    class Meta:
        model = MaintenanceRecord

        fields = [
            "reported_by",
            "problem",
            "reported_date",
            "provider",
            "cost",
            "completed_date",
            "status",
            "notes",
        ]

        widgets = {
            "reported_by": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "problem": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Describe the problem..."
                    ),
                }
            ),
            "reported_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "provider": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Repair provider",
                }
            ),
            "cost": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),
            "completed_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["reported_by"].queryset = (
            Member.objects
            .filter(is_active=True)
            .order_by("name")
        )

        if not self.instance.pk:
            self.fields["reported_date"].initial = (
                timezone.localdate()
            )