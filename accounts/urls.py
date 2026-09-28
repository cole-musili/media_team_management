from django.urls import path

from .views import (
    login_view,
    logout_view,
    password_change_view,
    profile_edit,
    profile_view,
    user_create,
    user_edit,
    user_list,
    user_toggle_status,
)


urlpatterns = [
    path(
        "login/",
        login_view,
        name="login",
    ),

    path(
        "logout/",
        logout_view,
        name="logout",
    ),

    path(
        "profile/",
        profile_view,
        name="profile",
    ),

    path(
        "profile/edit/",
        profile_edit,
        name="profile_edit",
    ),

    path(
        "profile/password/",
        password_change_view,
        name="password_change",
    ),

    path(
        "administration/users/",
        user_list,
        name="user_list",
    ),

    path(
        "administration/users/add/",
        user_create,
        name="user_create",
    ),

    path(
        "administration/users/<int:pk>/edit/",
        user_edit,
        name="user_edit",
    ),

    path(
        "administration/users/<int:pk>/toggle-status/",
        user_toggle_status,
        name="user_toggle_status",
    ),
]