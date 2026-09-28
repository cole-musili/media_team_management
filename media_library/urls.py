from django.urls import path

from .views import (
    album_create,
    album_detail,
    album_edit,
    media_delete,
    media_detail,
    media_library,
    media_upload,
)

urlpatterns = [

    path(
        "",
        media_library,
        name="media_library",
    ),

    path(
        "albums/add/",
        album_create,
        name="album_create",
    ),

    path(
        "albums/<int:pk>/",
        album_detail,
        name="album_detail",
    ),

    path(
        "albums/<int:pk>/edit/",
        album_edit,
        name="album_edit",
    ),

    path(
        "albums/<int:album_id>/upload/",
        media_upload,
        name="media_upload",
    ),

    path(
        "media/<int:pk>/",
        media_detail,
        name="media_detail",
    ),

    path(
        "media/<int:pk>/delete/",
        media_delete,
        name="media_delete",
    ),
]