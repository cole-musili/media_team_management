from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from members.models import UserProfile


ROLE_ADMIN = "admin"
ROLE_COORDINATOR = "coordinator"
ROLE_TEAM_MEMBER = "team_member"
ROLE_VIEWER = "viewer"


def get_user_role(user):
    """
    Return the application's system role for a user.
    """

    if not user.is_authenticated:
        return None

    if user.is_superuser:
        return ROLE_ADMIN

    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return None


def has_role(user, *roles):
    """
    Check whether a user has one of the supplied roles.
    """

    role = get_user_role(user)

    return role in roles


def role_required(*roles):
    """
    Protect a view based on system role.
    """

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("login")

            if not has_role(request.user, *roles):
                messages.error(
                    request,
                    "You do not have permission to access this page."
                )
                return redirect("dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator