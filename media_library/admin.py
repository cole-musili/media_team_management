from django.contrib import admin

from .models import Album, MediaItem


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "event",
        "created_at",
    )

    search_fields = (
        "title",
        "event__name",
    )

    list_filter = (
        "event",
        "created_at",
    )


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "media_type",
        "album",
        "uploaded_by",
        "uploaded_at",
    )

    search_fields = (
        "title",
        "album__title",
        "description",
    )

    list_filter = (
        "media_type",
        "uploaded_at",
    )