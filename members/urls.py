from django.urls import path

from .views import (
    availability_update,
    member_create,
    member_detail,
    member_edit,
    member_list,
    member_toggle_status,
    skill_create,
    skill_delete,
    skill_edit,
    skill_list,
)

urlpatterns = [
    # Members
    path("", member_list, name="member_list"),
    path("add/", member_create, name="member_create"),
    path("<int:pk>/", member_detail, name="member_detail"),
    path("<int:pk>/edit/", member_edit, name="member_edit"),
    path(
        "<int:pk>/toggle-status/",
        member_toggle_status,
        name="member_toggle_status",
    ),
    path(
        "<int:pk>/availability/",
        availability_update,
        name="availability_update",
    ),

    # Skills
    path("skills/", skill_list, name="skill_list"),
    path("skills/add/", skill_create, name="skill_create"),
    path("skills/<int:pk>/edit/", skill_edit, name="skill_edit"),
    path("skills/<int:pk>/delete/", skill_delete, name="skill_delete"),
]