import base64
from io import BytesIO

import qrcode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.permissions import role_required
from members.models import Member
from roster.models import DutyAssignment

from .models import Attendance, AttendanceSession
from events.models import Event


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

@login_required
@role_required("admin", "coordinator")
def attendance_session_start(request, event_id):

    event = get_object_or_404(
        Event,
        pk=event_id,
    )

    if request.method != "POST":
        return redirect("event_attendance", event_id=event.id)

    with transaction.atomic():

        AttendanceSession.objects.filter(
            event=event,
            is_active=True,
        ).update(
            is_active=False,
            ended_at=timezone.now(),
        )

        session = AttendanceSession.objects.create(
            event=event,
        )

    messages.success(
        request,
        f"QR attendance has been started for {event.name}.",
    )

    return redirect(
        "attendance_scanner",
        session_id=session.id,
    )



@login_required
@role_required("admin", "coordinator")
def attendance_scanner(request, session_id):

    session = get_object_or_404(
        AttendanceSession.objects.select_related("event"),
        pk=session_id,
    )

    event = session.event

    scan_url = request.build_absolute_uri(
        reverse(
            "attendance_scan",
            kwargs={"token": session.token},
        )
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )

    qr.add_data(scan_url)
    qr.make(fit=True)

    image = qr.make_image()

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    qr_code = base64.b64encode(
        buffer.getvalue()
    ).decode()

    assignments = DutyAssignment.objects.filter(
        event=event,
    ).select_related(
        "member",
        "position",
    )

    attendance = Attendance.objects.filter(
        event=event,
    ).select_related(
        "member",
    )

    present_count = attendance.filter(
        status__in=["present", "late"],
    ).count()

    total_count = assignments.exclude(
        status__in=["declined", "replaced"],
    ).values(
        "member_id"
    ).distinct().count()

    return render(
        request,
        "attendance/scanner.html",
        {
            "session": session,
            "event": event,
            "qr_code": qr_code,
            "attendance": attendance,
            "assignments": assignments,
            "present_count": present_count,
            "total_count": total_count,
        },
    )


@login_required
def attendance_scan(request, token):

    session = get_object_or_404(
        AttendanceSession.objects.select_related("event"),
        token=token,
    )

    if not session.is_active:
        return render(
            request,
            "attendance/scan_result.html",
            {
                "success": False,
                "title": "Attendance Closed",
                "message": "This attendance session is no longer active.",
            },
        )

    event = session.event

    member = getattr(
        request.user,
        "media_member",
        None,
    )

    if member is None:
        return render(
            request,
            "attendance/scan_result.html",
            {
                "success": False,
                "title": "Member Profile Required",
                "message": (
                    "Your account is not linked to a media team member."
                ),
            },
        )

    if not member.is_active:
        return render(
            request,
            "attendance/scan_result.html",
            {
                "success": False,
                "title": "Account Inactive",
                "message": (
                    "Your media team membership is currently inactive."
                ),
            },
        )

    # Make sure the member is assigned to this event.
    assignment_exists = DutyAssignment.objects.filter(
        event=event,
        member=member,
    ).exclude(
        status__in=["declined", "replaced"],
    ).exists()

    if not assignment_exists:
        return render(
            request,
            "attendance/scan_result.html",
            {
                "success": False,
                "title": "Not Assigned",
                "message": (
                    "You are not assigned to this event. "
                    "Please contact the Media Coordinator."
                ),
            },
        )

    # Find existing attendance record or create one.
    attendance, created = Attendance.objects.get_or_create(
        event=event,
        member=member,
        defaults={
            "status": "present",
            "check_in": timezone.now(),
        },
    )

    # =========================================================
    # FIRST SCAN = CHECK IN
    # =========================================================

    if not attendance.check_in:

        attendance.status = "present"
        attendance.check_in = timezone.now()

        attendance.save(
            update_fields=[
                "status",
                "check_in",
            ]
        )

        return render(
            request,
            "attendance/scan_result.html",
            {
                "success": True,
                "action": "check_in",
                "member": member,
                "attendance": attendance,
                "event": event,
            },
        )

    # =========================================================
    # SECOND SCAN = CHECK OUT
    # =========================================================

    if not attendance.check_out:

        attendance.check_out = timezone.now()

        attendance.save(
            update_fields=[
                "check_out",
            ]
        )

        return render(
            request,
            "attendance/scan_result.html",
            {
                "success": True,
                "action": "check_out",
                "member": member,
                "attendance": attendance,
                "event": event,
            },
        )

    # =========================================================
    # THIRD OR MORE SCANS = ALREADY CHECKED OUT
    # =========================================================

    return render(
        request,
        "attendance/scan_result.html",
        {
            "success": True,
            "action": "already_checked_out",
            "member": member,
            "attendance": attendance,
            "event": event,
        },
    )


@login_required
@role_required("admin", "coordinator")
def attendance_session_end(request, session_id):

    session = get_object_or_404(
        AttendanceSession,
        pk=session_id,
    )

    if request.method == "POST":

        session.is_active = False
        session.ended_at = timezone.now()
        session.save(
            update_fields=[
                "is_active",
                "ended_at",
            ]
        )

        messages.success(
            request,
            "Attendance session has been closed.",
        )

    return redirect(
        "event_attendance",
        event_id=session.event_id,
    )