from django.urls import path

from .views import (
    attendance_add_member,
    attendance_check_out,
    attendance_list,
    attendance_update,
    attendance_session_end,
    attendance_session_start,
    attendance_scanner,
    attendance_scan,
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
        "event/<int:event_id>/start/",
        attendance_session_start,
        name="attendance_session_start",
    ),

    path(
        "scanner/<int:session_id>/",
        attendance_scanner,
        name="attendance_scanner",
    ),

    path(
        "scanner/<int:session_id>/end/",
        attendance_session_end,
        name="attendance_session_end",
    ),

    path(
        "scan/<uuid:token>/",
        attendance_scan,
        name="attendance_scan",
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