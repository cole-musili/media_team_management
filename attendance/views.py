from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import role_required
from events.models import Event
from members.models import Member

from .forms import AttendanceForm
from .models import Attendance


# ============================================================
# ATTENDANCE
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def attendance_list(request):
    events = (
        Event.objects
        .order_by("-date", "-start_time")
    )

    selected_event = request.GET.get(
        "event",
        "",
    ).strip()

    search = request.GET.get(
        "search",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    rows = (
        Attendance.objects
        .select_related(
            "event",
            "member",
        )
        .order_by(
            "-event__date",
            "member__name",
        )
    )

    # Team members can only view their own attendance.
    if request.user.profile.role == "team_member":
        member = getattr(request.user, "media_member", None)

        if member:
            rows = rows.filter(member=member)
        else:
            rows = rows.none()

    if selected_event:
        rows = rows.filter(
            event_id=selected_event
        )

    if search:
        rows = rows.filter(
            Q(member__name__icontains=search)
            | Q(event__name__icontains=search)
        )

    if status:
        rows = rows.filter(
            status=status
        )

    context = {
        "events": events,
        "rows": rows,
        "selected_event": selected_event,
        "search": search,
        "selected_status": status,
        "total_records": rows.count(),
        "present_count": rows.filter(
            status="present"
        ).count(),
        "late_count": rows.filter(
            status="late"
        ).count(),
        "absent_count": rows.filter(
            status="absent"
        ).count(),
        "excused_count": rows.filter(
            status="excused"
        ).count(),
    }

    return render(
        request,
        "attendance/list.html",
        context,
    )


@role_required("admin", "coordinator", "team_member", "viewer")
def event_attendance(request, event_id):
    event = get_object_or_404(
        Event,
        pk=event_id,
    )

    assignments = (
        event.assignments
        .select_related(
            "member",
            "position",
        )
        .order_by(
            "position__name",
            "slot",
        )
    )

    # Only administrators and coordinators can manage
    # attendance for the whole event.
    if request.user.profile.role == "team_member":
        member = getattr(request.user, "media_member", None)

        if member:
            assignments = assignments.filter(member=member)
        else:
            assignments = assignments.none()

    # Do not initialize attendance records for a Team Member
    # viewing an event. Initialization changes database state.
    if request.user.profile.role in ["admin", "coordinator"]:
        for assignment in assignments:
            Attendance.objects.get_or_create(
                event=event,
                member=assignment.member,
                defaults={
                    "status": "absent",
                },
            )

    rows = (
        Attendance.objects
        .filter(event=event)
        .select_related("member")
        .order_by("member__name")
    )

    # Team members can only see their own attendance.
    if request.user.profile.role == "team_member":
        member = getattr(request.user, "media_member", None)

        if member:
            rows = rows.filter(member=member)
        else:
            rows = rows.none()

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:
        rows = rows.filter(
            member__name__icontains=search
        )

    context = {
        "event": event,
        "rows": rows,
        "assignments": assignments,
        "present_count": rows.filter(
            status="present"
        ).count(),
        "late_count": rows.filter(
            status="late"
        ).count(),
        "absent_count": rows.filter(
            status="absent"
        ).count(),
        "excused_count": rows.filter(
            status="excused"
        ).count(),
        "total_count": rows.count(),
        "search": search,
    }

    return render(
        request,
        "attendance/event.html",
        context,
    )


@role_required("admin", "coordinator")
def attendance_update(request, pk):
    attendance = get_object_or_404(
        Attendance.objects.select_related(
            "event",
            "member",
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = AttendanceForm(
            request.POST,
            instance=attendance,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                (
                    f"Attendance for {attendance.member.name} "
                    "was updated."
                ),
            )

            return redirect(
                "event_attendance",
                event_id=attendance.event.pk,
            )

    else:
        form = AttendanceForm(
            instance=attendance,
        )

    return render(
        request,
        "attendance/form.html",
        {
            "form": form,
            "attendance": attendance,
        },
    )


@role_required("admin", "coordinator")
def mark_attendance(request, pk):
    attendance = get_object_or_404(
        Attendance.objects.select_related(
            "event",
            "member",
        ),
        pk=pk,
    )

    if request.method == "POST":
        status = request.POST.get(
            "status",
        )

        valid_statuses = dict(
            Attendance.STATUS
        )

        if status not in valid_statuses:
            messages.error(
                request,
                "Invalid attendance status.",
            )

            return redirect(
                "event_attendance",
                event_id=attendance.event.pk,
            )

        attendance.status = status

        # Automatically record check-in when present/late.
        if status in ["present", "late"]:
            if not attendance.check_in:
                attendance.check_in = timezone.now()

        # Clear check-in/check-out when absent/excused.
        elif status in ["absent", "excused"]:
            attendance.check_in = None
            attendance.check_out = None

        attendance.save()

        messages.success(
            request,
            (
                f"{attendance.member.name} marked "
                f"{attendance.get_status_display().lower()}."
            ),
        )

    return redirect(
        "event_attendance",
        event_id=attendance.event.pk,
    )


@role_required("admin", "coordinator")
def attendance_check_out(request, pk):
    attendance = get_object_or_404(
        Attendance.objects.select_related(
            "event",
            "member",
        ),
        pk=pk,
    )

    if request.method == "POST":
        if attendance.status not in [
            "present",
            "late",
        ]:
            messages.error(
                request,
                "Only present or late members can be checked out.",
            )

        else:
            attendance.check_out = timezone.now()

            attendance.save(
                update_fields=[
                    "check_out",
                ]
            )

            messages.success(
                request,
                f"{attendance.member.name} has been checked out.",
            )

    return redirect(
        "event_attendance",
        event_id=attendance.event.pk,
    )


@role_required("admin", "coordinator")
def attendance_add_member(request, event_id):
    event = get_object_or_404(
        Event,
        pk=event_id,
    )

    if request.method == "POST":
        member_id = request.POST.get(
            "member",
        )

        member = get_object_or_404(
            Member,
            pk=member_id,
            is_active=True,
        )

        attendance, created = Attendance.objects.get_or_create(
            event=event,
            member=member,
            defaults={
                "status": "absent",
            },
        )

        if created:
            messages.success(
                request,
                f"{member.name} was added to attendance.",
            )
        else:
            messages.info(
                request,
                f"{member.name} is already on the attendance sheet.",
            )

    return redirect(
        "event_attendance",
        event_id=event.pk,
    )
