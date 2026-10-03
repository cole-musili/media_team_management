from django.urls import path

from .views import (
    assignment_create,
    assignment_delete,
    assignment_edit,
    assignment_status,
    assignment_confirm,
    assignment_decline,
    position_create,
    position_edit,
    position_list,
    position_toggle,
    roster_list,
)


urlpatterns = [

    # Roster
    path(
        "",
        roster_list,
        name="roster_list",
    ),

    path(
        "assign/",
        assignment_create,
        name="assignment_create",
    ),

    path(
        "assignment/<int:pk>/edit/",
        assignment_edit,
        name="assignment_edit",
    ),

    path(
        "assignment/<int:pk>/status/",
        assignment_status,
        name="assignment_status",
    ),

    # Team member confirmation
    path(
        "assignment/<int:pk>/confirm/",
        assignment_confirm,
        name="assignment_confirm",
    ),

    path(
        "assignment/<int:pk>/decline/",
        assignment_decline,
        name="assignment_decline",
    ),

    path(
        "assignment/<int:pk>/delete/",
        assignment_delete,
        name="assignment_delete",
    ),

    # Positions
    path(
        "positions/",
        position_list,
        name="position_list",
    ),

    path(
        "positions/add/",
        position_create,
        name="position_create",
    ),

    path(
        "positions/<int:pk>/edit/",
        position_edit,
        name="position_edit",
    ),

    path(
        "positions/<int:pk>/toggle/",
        position_toggle,
        name="position_toggle",
    ),
]