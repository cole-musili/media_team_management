from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from attendance.models import Attendance
from equipment.models import Equipment
from events.models import Event
from media_library.models import Album, MediaItem
from members.models import Member
from roster.models import DutyAssignment

from accounts.permissions import get_user_role


@login_required
def dashboard(request):
    today = timezone.localdate()
    role = get_user_role(request.user)

    # ---------------------------------------------------------
    # Common data
    # ---------------------------------------------------------
    upcoming_events = (
        Event.objects
        .filter(date__gte=today)
        .order_by("date", "start_time")[:5]
    )

    recent_events = (
        Event.objects
        .order_by("-date", "-start_time")[:5]
    )

    media_count = MediaItem.objects.count()
    album_count = Album.objects.count()

    # ---------------------------------------------------------
    # Admin / Coordinator dashboard
    # ---------------------------------------------------------
    if role in ("admin", "coordinator"):
        member_count = Member.objects.filter(is_active=True).count()

        event_count = Event.objects.filter(date__gte=today).count()

        equipment_count = Equipment.objects.count()

        available_equipment = Equipment.objects.filter(
            status="available"
        ).count()

        equipment_in_use = Equipment.objects.filter(
            status="in_use"
        ).count()

        equipment_maintenance = Equipment.objects.filter(
            status="maintenance"
        ).count()

        equipment_damaged = Equipment.objects.filter(
            status="damaged"
        ).count()

        todays_duties = (
            DutyAssignment.objects
            .filter(event__date=today)
            .select_related("event", "position", "member")
            .order_by("event__start_time", "position__name")
        )

        todays_attendance = Attendance.objects.filter(
            event__date=today
        )

        attendance_present = todays_attendance.filter(
            status="present"
        ).count()

        attendance_late = todays_attendance.filter(
            status="late"
        ).count()

        attendance_absent = todays_attendance.filter(
            status="absent"
        ).count()

        context = {
            "today": today,

            "member_count": member_count,
            "event_count": event_count,
            "equipment_count": equipment_count,
            "media_count": media_count,
            "album_count": album_count,

            "available_equipment": available_equipment,
            "equipment_in_use": equipment_in_use,
            "equipment_maintenance": equipment_maintenance,
            "equipment_damaged": equipment_damaged,

            "upcoming_events": upcoming_events,
            "recent_events": recent_events,
            "todays_duties": todays_duties,

            "attendance_present": attendance_present,
            "attendance_late": attendance_late,
            "attendance_absent": attendance_absent,

            "dashboard_role": role,
        }

        return render(request, "core/dashboard.html", context)

    # ---------------------------------------------------------
    # Team Member dashboard
    # ---------------------------------------------------------
    if role == "team_member":
        member = getattr(request.user, "media_member", None)

        if member:
            todays_duties = (
                DutyAssignment.objects
                .filter(
                    event__date=today,
                    member=member,
                )
                .select_related("event", "position", "member")
                .order_by("event__start_time", "position__name")
            )

            my_attendance = Attendance.objects.filter(
                event__date=today,
                member=member,
            )

            attendance_present = my_attendance.filter(
                status="present"
            ).count()

            attendance_late = my_attendance.filter(
                status="late"
            ).count()

            attendance_absent = my_attendance.filter(
                status="absent"
            ).count()
        else:
            todays_duties = DutyAssignment.objects.none()
            attendance_present = 0
            attendance_late = 0
            attendance_absent = 0

        context = {
            "today": today,

            # Keep the same template keys available.
            "member_count": None,
            "event_count": Event.objects.filter(date__gte=today).count(),
            "equipment_count": None,
            "media_count": media_count,
            "album_count": album_count,

            "available_equipment": None,
            "equipment_in_use": None,
            "equipment_maintenance": None,
            "equipment_damaged": None,

            "upcoming_events": upcoming_events,
            "recent_events": recent_events,
            "todays_duties": todays_duties,

            "attendance_present": attendance_present,
            "attendance_late": attendance_late,
            "attendance_absent": attendance_absent,

            "dashboard_role": role,
        }

        return render(request, "core/dashboard.html", context)

    # ---------------------------------------------------------
    # Viewer dashboard
    # ---------------------------------------------------------
    if role == "viewer":
        context = {
            "today": today,

            "member_count": Member.objects.filter(is_active=True).count(),
            "event_count": Event.objects.filter(date__gte=today).count(),
            "equipment_count": Equipment.objects.count(),
            "media_count": media_count,
            "album_count": album_count,

            "available_equipment": Equipment.objects.filter(
                status="available"
            ).count(),
            "equipment_in_use": Equipment.objects.filter(
                status="in_use"
            ).count(),
            "equipment_maintenance": Equipment.objects.filter(
                status="maintenance"
            ).count(),
            "equipment_damaged": Equipment.objects.filter(
                status="damaged"
            ).count(),

            "upcoming_events": upcoming_events,
            "recent_events": recent_events,

            "todays_duties": DutyAssignment.objects.filter(
                event__date=today
            ).select_related(
                "event", "position", "member"
            ).order_by(
                "event__start_time", "position__name"
            ),

            "attendance_present": Attendance.objects.filter(
                event__date=today,
                status="present",
            ).count(),

            "attendance_late": Attendance.objects.filter(
                event__date=today,
                status="late",
            ).count(),

            "attendance_absent": Attendance.objects.filter(
                event__date=today,
                status="absent",
            ).count(),

            "dashboard_role": role,
        }

        return render(request, "core/dashboard.html", context)

    # ---------------------------------------------------------
    # Users without a configured application role
    # ---------------------------------------------------------
    context = {
        "today": today,
        "member_count": None,
        "event_count": Event.objects.filter(date__gte=today).count(),
        "equipment_count": None,
        "media_count": media_count,
        "album_count": album_count,
        "available_equipment": None,
        "equipment_in_use": None,
        "equipment_maintenance": None,
        "equipment_damaged": None,
        "upcoming_events": upcoming_events,
        "recent_events": recent_events,
        "todays_duties": DutyAssignment.objects.none(),
        "attendance_present": 0,
        "attendance_late": 0,
        "attendance_absent": 0,
        "dashboard_role": None,
    }

    return render(request, "core/dashboard.html", context)
