from django import forms

from .models import Attendance


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance

        fields = [
            "status",
            "check_in",
            "check_out",
            "notes",
        ]

        widgets = {
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "check_in": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "check_out": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional attendance notes...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["check_in"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]

        self.fields["check_out"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]