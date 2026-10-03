from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import role_required
from events.models import Event
from members.models import Member

from .forms import DutyAssignmentForm, DutyPositionForm
from .models import DutyAssignment, DutyPosition


# ============================================================
# DUTY ROSTER
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def roster_list(request):
    today = timezone.localdate()

    assignments = (
        DutyAssignment.objects
        .filter(event__date__gte=today)
        .select_related(
            "event",
            "member",
            "position",
        )
        .prefetch_related(
            "position__required_skills",
            "member__skills",
        )
    )

    # Team members should only see their own assignments.
    if request.user.profile.role == "team_member":
        member = getattr(request.user, "media_member", None)

        if member:
            assignments = assignments.filter(member=member)
        else:
            assignments = assignments.none()

    search = request.GET.get("search", "").strip()
    event_id = request.GET.get("event", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        assignments = assignments.filter(
            Q(event__name__icontains=search)
            | Q(member__name__icontains=search)
            | Q(position__name__icontains=search)
            | Q(slot__icontains=search)
        )

    if event_id:
        assignments = assignments.filter(event_id=event_id)

    if status:
        assignments = assignments.filter(status=status)

    events = (
        Event.objects
        .filter(
            date__gte=today,
            status__in=["draft", "scheduled"],
        )
        .order_by(
            "date",
            "start_time",
        )
    )

    context = {
        "assignments": assignments,
        "events": events,
        "search": search,
        "selected_event": event_id,
        "selected_status": status,
        "total_assignments": assignments.count(),
        "confirmed_count": assignments.filter(
            status="confirmed"
        ).count(),
        "pending_count": assignments.filter(
            status="pending"
        ).count(),
        "declined_count": assignments.filter(
            status="declined"
        ).count(),
    }

    return render(
        request,
        "roster/list.html",
        context,
    )


@role_required("admin", "coordinator")
def assignment_create(request):
    if request.method == "POST":
        form = DutyAssignmentForm(request.POST)

        if form.is_valid():
            assignment = form.save()

            messages.success(
                request,
                (
                    f"{assignment.member.name} was assigned "
                    f"to {assignment.position.name}."
                ),
            )

            return redirect("roster_list")

    else:
        initial = {}

        event_id = request.GET.get("event")

        if event_id:
            initial["event"] = event_id

        form = DutyAssignmentForm(initial=initial)

    return render(
        request,
        "roster/assignment_form.html",
        {
            "form": form,
            "editing": False,
        },
    )


@role_required("admin", "coordinator")
def assignment_edit(request, pk):
    assignment = get_object_or_404(
        DutyAssignment,
        pk=pk,
    )

    if request.method == "POST":
        form = DutyAssignmentForm(
            request.POST,
            instance=assignment,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Duty assignment was updated.",
            )

            return redirect("roster_list")

    else:
        form = DutyAssignmentForm(
            instance=assignment
        )

    return render(
        request,
        "roster/assignment_form.html",
        {
            "form": form,
            "assignment": assignment,
            "editing": True,
        },
    )


@role_required("admin", "coordinator")
def assignment_status(request, pk):
    assignment = get_object_or_404(
        DutyAssignment,
        pk=pk,
    )

    if request.method == "POST":
        status = request.POST.get("status")

        valid_statuses = dict(
            DutyAssignment.STATUS
        )

        if status not in valid_statuses:
            messages.error(
                request,
                "Invalid assignment status.",
            )

            return redirect("roster_list")

        assignment.status = status
        assignment.save(
            update_fields=["status"]
        )

        messages.success(
            request,
            (
                f"{assignment.member.name}'s assignment "
                f"is now {assignment.get_status_display()}."
            ),
        )

    return redirect("roster_list")


@role_required("team_member")
def assignment_confirm(request, pk):
    assignment = get_object_or_404(
        DutyAssignment.objects.select_related(
            "member",
            "event",
            "position",
        ),
        pk=pk,
    )

    member = getattr(request.user, "media_member", None)

    if not member or assignment.member_id != member.id:
        messages.error(
            request,
            "You are not allowed to confirm this assignment.",
        )
        return redirect("roster_list")

    if request.method == "POST":

        if assignment.status != "pending":
            messages.info(
                request,
                "This assignment is no longer pending.",
            )
            return redirect("roster_list")

        assignment.status = "confirmed"
        assignment.save(
            update_fields=["status"]
        )

        messages.success(
            request,
            (
                f"You confirmed your duty as "
                f"{assignment.position.name} "
                f"for {assignment.event.name}."
            ),
        )

    return redirect("roster_list")


@role_required("team_member")
def assignment_decline(request, pk):
    assignment = get_object_or_404(
        DutyAssignment.objects.select_related(
            "member",
            "event",
            "position",
        ),
        pk=pk,
    )

    member = getattr(request.user, "media_member", None)

    if not member or assignment.member_id != member.id:
        messages.error(
            request,
            "You are not allowed to decline this assignment.",
        )
        return redirect("roster_list")

    if request.method == "POST":

        if assignment.status != "pending":
            messages.info(
                request,
                "This assignment is no longer pending.",
            )
            return redirect("roster_list")

        assignment.status = "declined"
        assignment.save(
            update_fields=["status"]
        )

        messages.warning(
            request,
            (
                f"You declined your duty as "
                f"{assignment.position.name} "
                f"for {assignment.event.name}."
            ),
        )

    return redirect("roster_list")

@role_required("admin", "coordinator")
def assignment_delete(request, pk):
    assignment = get_object_or_404(
        DutyAssignment,
        pk=pk,
    )

    if request.method == "POST":
        member_name = assignment.member.name

        assignment.delete()

        messages.success(
            request,
            f"Assignment for {member_name} was removed.",
        )

    return redirect("roster_list")


# ============================================================
# DUTY POSITIONS
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def position_list(request):
    positions = (
        DutyPosition.objects
        .prefetch_related(
            "required_skills"
        )
        .order_by(
            "-is_active",
            "name",
        )
    )

    return render(
        request,
        "roster/positions.html",
        {
            "positions": positions,
        },
    )


@role_required("admin", "coordinator")
def position_create(request):
    if request.method == "POST":
        form = DutyPositionForm(request.POST)

        if form.is_valid():
            position = form.save()

            messages.success(
                request,
                f"{position.name} was created.",
            )

            return redirect("position_list")

    else:
        form = DutyPositionForm()

    return render(
        request,
        "roster/position_form.html",
        {
            "form": form,
            "editing": False,
        },
    )


@role_required("admin", "coordinator")
def position_edit(request, pk):
    position = get_object_or_404(
        DutyPosition,
        pk=pk,
    )

    if request.method == "POST":
        form = DutyPositionForm(
            request.POST,
            instance=position,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Duty position was updated.",
            )

            return redirect("position_list")

    else:
        form = DutyPositionForm(
            instance=position
        )

    return render(
        request,
        "roster/position_form.html",
        {
            "form": form,
            "position": position,
            "editing": True,
        },
    )


@role_required("admin", "coordinator")
def position_toggle(request, pk):
    position = get_object_or_404(
        DutyPosition,
        pk=pk,
    )

    if request.method == "POST":
        position.is_active = not position.is_active

        position.save(
            update_fields=["is_active"]
        )

        if position.is_active:
            messages.success(
                request,
                f"{position.name} is now active.",
            )
        else:
            messages.warning(
                request,
                f"{position.name} has been deactivated.",
            )

    return redirect(
        "position_list"
    )
