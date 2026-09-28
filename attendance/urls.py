from django.urls import path

from .views import (
    attendance_add_member,
    attendance_check_out,
    attendance_list,
    attendance_update,
    event_attendance,
    mark_attendance,
)


urlpatterns = [

    path(
        "",
        attendance_list,
        name="attendance_list",
    ),

    path(
        "event/<int:event_id>/",
        event_attendance,
        name="event_attendance",
    ),

    path(
        "event/<int:event_id>/add-member/",
        attendance_add_member,
        name="attendance_add_member",
    ),

    path(
        "<int:pk>/edit/",
        attendance_update,
        name="attendance_update",
    ),

    path(
        "<int:pk>/mark/",
        mark_attendance,
        name="mark_attendance",
    ),

    path(
        "<int:pk>/checkout/",
        attendance_check_out,
        name="attendance_check_out",
    ),
]