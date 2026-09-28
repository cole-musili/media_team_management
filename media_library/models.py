from django.db import models

from events.models import Event
from members.models import Member


class Album(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="albums",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover = models.ImageField(
        upload_to="albums/covers/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class MediaItem(models.Model):

    TYPES = [
        ("photo", "Photo"),
        ("video", "Video"),
        ("document", "Document"),
    ]

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="items",
    )

    media_type = models.CharField(
        max_length=20,
        choices=TYPES,
        default="photo",
    )

    file = models.FileField(
        upload_to="media_library/"
    )

    title = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        blank=True
    )

    uploaded_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_media",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title or self.file.name