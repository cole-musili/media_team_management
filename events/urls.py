from django.urls import path

from .views import (
    event_create,
    event_detail,
    event_edit,
    event_list,
    event_status_update,
)


urlpatterns = [
    path("", event_list, name="event_list"),
    path("add/", event_create, name="event_create"),
    path("<int:pk>/", event_detail, name="event_detail"),
    path("<int:pk>/edit/", event_edit, name="event_edit"),
    path(
        "<int:pk>/status/",
        event_status_update,
        name="event_status_update",
    ),
]