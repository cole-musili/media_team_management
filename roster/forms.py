from django import forms
from django.core.exceptions import ValidationError

from events.models import Event
from members.models import Member

from .models import DutyAssignment, DutyPosition


class DutyPositionForm(forms.ModelForm):
    class Meta:
        model = DutyPosition
        fields = [
            "name",
            "description",
            "required_skills",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Camera Operator",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe this duty position...",
                }
            ),
            "required_skills": forms.CheckboxSelectMultiple(),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class DutyAssignmentForm(forms.ModelForm):

    class Meta:
        model = DutyAssignment

        fields = [
            "event",
            "position",
            "slot",
            "member",
            "status",
            "notes",
        ]

        widgets = {
            "event": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "position": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "slot": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Camera 1",
                }
            ),
            "member": forms.Select(
                attrs={
                    "class": "form-select",
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
                    "placeholder": "Additional assignment notes...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["event"].queryset = (
            Event.objects
            .filter(status__in=["draft", "scheduled"])
            .order_by("date", "start_time")
        )

        self.fields["position"].queryset = (
            DutyPosition.objects
            .filter(is_active=True)
            .prefetch_related("required_skills")
            .order_by("name")
        )

        self.fields["member"].queryset = (
            Member.objects
            .filter(is_active=True)
            .prefetch_related("skills")
            .order_by("name")
        )

        if not self.instance.pk:
            self.fields["status"].initial = "pending"

    def clean(self):

        cleaned_data = super().clean()

        event = cleaned_data.get("event")
        position = cleaned_data.get("position")
        slot = cleaned_data.get("slot")
        member = cleaned_data.get("member")

        if not event or not position or not member:
            return cleaned_data

        # ----------------------------------------------------
        # Prevent duplicate slot
        # ----------------------------------------------------

        duplicate_slot = DutyAssignment.objects.filter(
            event=event,
            position=position,
            slot=slot,
        ).exclude(
            pk=self.instance.pk
        )

        if duplicate_slot.exists():
            raise ValidationError(
                "This duty slot is already assigned for this event."
            )

        # ----------------------------------------------------
        # Prevent assigning same member twice
        # ----------------------------------------------------

        duplicate_member = DutyAssignment.objects.filter(
            event=event,
            member=member,
        ).exclude(
            pk=self.instance.pk
        )

        if duplicate_member.exists():
            raise ValidationError(
                f"{member.name} is already assigned to another "
                "duty for this event."
            )

        # ----------------------------------------------------
        # Check availability
        # ----------------------------------------------------

        availability = member.availability.filter(
            date=event.date
        ).first()

        if availability and availability.status == "unavailable":
            raise ValidationError(
                f"{member.name} is marked as unavailable on "
                f"{event.date:%d %B %Y}."
            )

        # ----------------------------------------------------
        # Check required skills
        # ----------------------------------------------------

        required_skills = set(
            position.required_skills.values_list(
                "id",
                flat=True,
            )
        )

        member_skills = set(
            member.skills.values_list(
                "id",
                flat=True,
            )
        )

        missing_skills = required_skills - member_skills

        if missing_skills:
            missing_names = list(
                position.required_skills.filter(
                    id__in=missing_skills
                ).values_list(
                    "name",
                    flat=True,
                )
            )

            raise ValidationError(
                f"{member.name} does not have the required skill(s): "
                f"{', '.join(missing_names)}."
            )

        return cleaned_data