from django import forms

from .models import Album, MediaItem


class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = [
            "event",
            "title",
            "description",
            "cover",
        ]

        widgets = {
            "event": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Album title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe this album...",
                }
            ),
            "cover": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }


class MediaItemForm(forms.ModelForm):

    class Meta:
        model = MediaItem

        fields = [
            "media_type",
            "file",
            "title",
            "description",
        ]

        widgets = {
            "media_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Media title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional description...",
                }
            ),
        }