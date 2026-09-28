from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required

from .forms import AlbumForm, MediaItemForm
from .models import Album, MediaItem


# ============================================================
# MEDIA LIBRARY
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def media_library(request):
    query = request.GET.get("q", "").strip()
    media_type = request.GET.get("type", "").strip()

    albums = (
        Album.objects
        .select_related("event")
        .prefetch_related("items")
    )

    if query:
        albums = albums.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(event__name__icontains=query)
        )

    if media_type:
        albums = albums.filter(
            items__media_type=media_type
        ).distinct()

    context = {
        "albums": albums,
        "query": query,
        "media_type": media_type,
        "total_albums": Album.objects.count(),
        "total_media": MediaItem.objects.count(),
        "total_photos": MediaItem.objects.filter(
            media_type="photo"
        ).count(),
        "total_videos": MediaItem.objects.filter(
            media_type="video"
        ).count(),
    }

    return render(
        request,
        "media_library/index.html",
        context,
    )


@role_required("admin", "coordinator", "team_member", "viewer")
def album_detail(request, pk):
    album = get_object_or_404(
        Album.objects
        .select_related("event")
        .prefetch_related("items__uploaded_by"),
        pk=pk,
    )

    media_type = request.GET.get("type", "").strip()

    items = album.items.all()

    if media_type:
        items = items.filter(
            media_type=media_type
        )

    context = {
        "album": album,
        "items": items,
        "media_type": media_type,
    }

    return render(
        request,
        "media_library/album_detail.html",
        context,
    )


@role_required("admin", "coordinator")
def album_create(request):
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES)

        if form.is_valid():
            album = form.save()

            messages.success(
                request,
                "Album created successfully.",
            )

            return redirect(
                "album_detail",
                pk=album.pk,
            )

    else:
        form = AlbumForm()

    return render(
        request,
        "media_library/album_form.html",
        {
            "form": form,
            "page_title": "Create Album",
        },
    )


@role_required("admin", "coordinator")
def album_edit(request, pk):
    album = get_object_or_404(
        Album,
        pk=pk,
    )

    if request.method == "POST":
        form = AlbumForm(
            request.POST,
            request.FILES,
            instance=album,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Album updated successfully.",
            )

            return redirect(
                "album_detail",
                pk=album.pk,
            )

    else:
        form = AlbumForm(
            instance=album
        )

    return render(
        request,
        "media_library/album_form.html",
        {
            "form": form,
            "album": album,
            "page_title": "Edit Album",
        },
    )


@role_required("admin", "coordinator", "team_member")
def media_upload(request, album_id):
    album = get_object_or_404(
        Album,
        pk=album_id,
    )

    if request.method == "POST":
        form = MediaItemForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            media = form.save(
                commit=False
            )

            media.album = album

            # Record the linked Member as the uploader.
            if request.user.is_authenticated:
                member = getattr(
                    request.user,
                    "media_member",
                    None,
                )

                if member:
                    media.uploaded_by = member

            media.save()

            messages.success(
                request,
                "Media uploaded successfully.",
            )

            return redirect(
                "album_detail",
                pk=album.pk,
            )

    else:
        form = MediaItemForm()

    return render(
        request,
        "media_library/media_form.html",
        {
            "form": form,
            "album": album,
        },
    )


@role_required("admin", "coordinator", "team_member", "viewer")
def media_detail(request, pk):
    media = get_object_or_404(
        MediaItem.objects
        .select_related(
            "album",
            "album__event",
            "uploaded_by",
        ),
        pk=pk,
    )

    return render(
        request,
        "media_library/media_detail.html",
        {
            "media": media,
        },
    )


@role_required("admin", "coordinator")
def media_delete(request, pk):
    media = get_object_or_404(
        MediaItem,
        pk=pk,
    )

    album_id = media.album_id

    if request.method == "POST":
        media.delete()

        messages.success(
            request,
            "Media deleted successfully.",
        )

        return redirect(
            "album_detail",
            pk=album_id,
        )

    return render(
        request,
        "media_library/media_confirm_delete.html",
        {
            "media": media,
        },
    )
