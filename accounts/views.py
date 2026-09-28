from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from members.models import UserProfile

from .forms import ProfileForm, UserCreateForm, UserEditForm
from .permissions import role_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            if not user.is_active:
                messages.error(
                    request,
                    "Your account is inactive. Please contact an administrator.",
                )
                return redirect("login")

            login(request, user)
            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(request, "accounts/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")

    return redirect("login")


def get_profile_for_user(user):
    """
    Return the user's UserProfile and keep the profile/member
    relationship connected where possible.
    """

    member = getattr(user, "media_member", None)

    if user.is_superuser:
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "role": "admin",
                "member": member,
            },
        )

        if profile.role != "admin":
            profile.role = "admin"

        if profile.member is None and member is not None:
            profile.member = member

        profile.save()

        return profile

    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "member": member,
        },
    )

    if profile.member is None and member is not None:
        profile.member = member
        profile.save(update_fields=["member"])

    return profile


@login_required
def profile_view(request):
    profile = get_profile_for_user(request.user)

    member = profile.member

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": profile,
            "member": member,
        },
    )


@login_required
def profile_edit(request):
    profile = get_profile_for_user(request.user)

    member = profile.member

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
            member=member,
        )

        if form.is_valid():
            with transaction.atomic():
                form.save()

                if member:
                    member.name = (
                        f"{request.user.first_name} "
                        f"{request.user.last_name}"
                    ).strip() or member.name

                    member.save()

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )

            return redirect("profile")

    else:
        form = ProfileForm(
            instance=request.user,
            member=member,
        )

    return render(
        request,
        "accounts/profile_edit.html",
        {
            "form": form,
            "profile": profile,
            "member": member,
        },
    )


@login_required
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(
            request.user,
            request.POST,
        )

        for field in form.fields.values():
            field.widget.attrs["class"] = "form-control"

        if form.is_valid():
            user = form.save()

            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Your password has been changed successfully.",
            )

            return redirect("profile")

    else:
        form = PasswordChangeForm(request.user)

        for field in form.fields.values():
            field.widget.attrs["class"] = "form-control"

    return render(
        request,
        "accounts/password_change.html",
        {
            "form": form,
        },
    )



@role_required("admin")
def user_list(request):
    users = (
        User.objects
        .select_related("profile", "profile__member")
        .order_by("first_name", "last_name", "username")
    )

    search = request.GET.get("search", "").strip()
    role = request.GET.get("role", "")
    status = request.GET.get("status", "")

    if search:
        from django.db.models import Q

        users = users.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(username__icontains=search)
            | Q(email__icontains=search)
        )

    if role:
        users = users.filter(profile__role=role)

    if status == "active":
        users = users.filter(is_active=True)
    elif status == "inactive":
        users = users.filter(is_active=False)

    return render(
        request,
        "accounts/users/list.html",
        {
            "users": users,
            "role_choices": UserProfile.ROLE_CHOICES,
            "current_role": role,
            "current_status": status,
            "search": search,
        },
    )


@role_required("admin")
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            with transaction.atomic():
                form.save()

            messages.success(
                request,
                "User account created successfully.",
            )

            return redirect("user_list")

    else:
        form = UserCreateForm()

    return render(
        request,
        "accounts/users/form.html",
        {
            "form": form,
            "page_title": "Add User",
            "page_subtitle": "Create a new system account and media team profile.",
            "is_edit": False,
        },
    )


@role_required("admin")
def user_edit(request, pk):
    user = get_object_or_404(
        User.objects.select_related(
            "profile",
            "profile__member",
        ),
        pk=pk,
    )

    profile = getattr(user, "profile", None)
    member = (
        profile.member
        if profile
        else getattr(user, "media_member", None)
    )

    if profile is None:
        profile = UserProfile.objects.create(
            user=user,
            member=member,
            role="admin" if user.is_superuser else "team_member",
        )

    if request.method == "POST":
        form = UserEditForm(
            request.POST,
            request.FILES,
            instance=user,
            member=member,
            profile=profile,
        )

        if form.is_valid():
            with transaction.atomic():
                form.save()

            messages.success(
                request,
                f"{user.username}'s account has been updated.",
            )

            return redirect("user_list")

    else:
        form = UserEditForm(
            instance=user,
            member=member,
            profile=profile,
        )

    return render(
        request,
        "accounts/users/form.html",
        {
            "form": form,
            "user_account": user,
            "profile": profile,
            "member": member,
            "page_title": "Edit User",
            "page_subtitle": "Update account, role and media team information.",
            "is_edit": True,
        },
    )


@role_required("admin")
def user_toggle_status(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method != "POST":
        return redirect("user_list")

    if user == request.user:
        messages.error(
            request,
            "You cannot deactivate your own account.",
        )
        return redirect("user_list")

    # Never allow an administrator to remove the active status
    # from a superuser through the normal user-management screen.
    if user.is_superuser:
        messages.error(
            request,
            "A superuser account cannot be deactivated here.",
        )
        return redirect("user_list")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    member = getattr(user, "media_member", None)

    if member:
        member.is_active = user.is_active
        member.save(update_fields=["is_active"])

    status = "activated" if user.is_active else "deactivated"

    messages.success(
        request,
        f"{user.username} has been {status}.",
    )

    return redirect("user_list")
