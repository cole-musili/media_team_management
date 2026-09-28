from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

from accounts.permissions import role_required
from attendance.models import Attendance
from equipment.models import Checkout, Equipment, MaintenanceRecord
from events.models import Event
from media_library.models import Album, MediaItem
from members.models import Member
from roster.models import DutyAssignment


# ============================================================
# REPORTS
# ============================================================

@role_required("admin", "coordinator", "viewer")
def reports_dashboard(request):
    today = timezone.localdate()

    context = {
        "member_count": Member.objects.filter(
            is_active=True
        ).count(),

        "event_count": Event.objects.count(),

        "completed_events": Event.objects.filter(
            date__lt=today
        ).count(),

        "upcoming_events": Event.objects.filter(
            date__gte=today
        ).count(),

        "equipment_count": Equipment.objects.count(),

        "equipment_available": Equipment.objects.filter(
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

        "album_count": Album.objects.count(),

        "media_count": MediaItem.objects.count(),

        "photo_count": MediaItem.objects.filter(
            media_type="photo"
        ).count(),

        "video_count": MediaItem.objects.filter(
            media_type="video"
        ).count(),

        "attendance_count": Attendance.objects.count(),

        "present_count": Attendance.objects.filter(
            status="present"
        ).count(),

        "late_count": Attendance.objects.filter(
            status="late"
        ).count(),

        "absent_count": Attendance.objects.filter(
            status="absent"
        ).count(),

        "assignment_count": DutyAssignment.objects.count(),

        "confirmed_assignments": DutyAssignment.objects.filter(
            status="confirmed"
        ).count(),

        "pending_assignments": DutyAssignment.objects.filter(
            status="pending"
        ).count(),

        "maintenance_count": MaintenanceRecord.objects.count(),

        "recent_events": Event.objects.order_by(
            "-date",
            "-start_time"
        )[:8],
    }

    return render(
        request,
        "reports/dashboard.html",
        context,
    )


@role_required("admin", "coordinator", "viewer")
def attendance_report(request):
    members = Member.objects.filter(
        is_active=True
    ).annotate(
        total_attendance=Count(
            "attendance",
            distinct=True,
        ),
        present_count=Count(
            "attendance",
            filter=Q(
                attendance__status="present"
            ),
            distinct=True,
        ),
        late_count=Count(
            "attendance",
            filter=Q(
                attendance__status="late"
            ),
            distinct=True,
        ),
        absent_count=Count(
            "attendance",
            filter=Q(
                attendance__status="absent"
            ),
            distinct=True,
        ),
    ).order_by("-present_count", "name")

    context = {
        "members": members,
        "total_records": Attendance.objects.count(),
        "present_count": Attendance.objects.filter(
            status="present"
        ).count(),
        "late_count": Attendance.objects.filter(
            status="late"
        ).count(),
        "absent_count": Attendance.objects.filter(
            status="absent"
        ).count(),
        "excused_count": Attendance.objects.filter(
            status="excused"
        ).count(),
    }

    return render(
        request,
        "reports/attendance.html",
        context,
    )


@role_required("admin", "coordinator", "viewer")
def equipment_report(request):
    equipment = Equipment.objects.select_related(
        "category"
    ).annotate(
        checkout_count=Count(
            "checkouts",
            distinct=True,
        ),
        maintenance_count=Count(
            "maintenance",
            distinct=True,
        ),
    ).order_by(
        "name"
    )

    context = {
        "equipment": equipment,

        "total": equipment.count(),

        "available": Equipment.objects.filter(
            status="available"
        ).count(),

        "in_use": Equipment.objects.filter(
            status="in_use"
        ).count(),

        "maintenance": Equipment.objects.filter(
            status="maintenance"
        ).count(),

        "damaged": Equipment.objects.filter(
            status="damaged"
        ).count(),

        "missing": Equipment.objects.filter(
            status="missing"
        ).count(),

        "checkout_count": Checkout.objects.count(),

        "maintenance_records": MaintenanceRecord.objects.count(),
    }

    return render(
        request,
        "reports/equipment.html",
        context,
    )


@role_required("admin", "coordinator", "viewer")
def event_report(request):
    events = Event.objects.annotate(
        assignment_count=Count(
            "assignments",
            distinct=True,
        ),
        attendance_count=Count(
            "attendance",
            distinct=True,
        ),
        equipment_count=Count(
            "equipment_checkouts",
            distinct=True,
        ),
        album_count=Count(
            "albums",
            distinct=True,
        ),
    ).order_by(
        "-date",
        "-start_time",
    )

    context = {
        "events": events,
        "total_events": events.count(),
    }

    return render(
        request,
        "reports/events.html",
        context,
    )


@role_required("admin", "coordinator", "viewer")
def member_report(request):
    members = Member.objects.filter(
        is_active=True
    ).annotate(
        duty_count=Count(
            "duty_assignments",
            distinct=True,
        ),
        attendance_count=Count(
            "attendance",
            distinct=True,
        ),
        equipment_checkout_count=Count(
            "equipment_checkouts",
            distinct=True,
        ),
        media_upload_count=Count(
            "uploaded_media",
            distinct=True,
        ),
    ).order_by(
        "name"
    )

    context = {
        "members": members,
    }

    return render(
        request,
        "reports/members.html",
        context,
    )


@role_required("admin", "coordinator", "viewer")
def media_report(request):
    albums = Album.objects.select_related(
        "event"
    ).annotate(
        media_count=Count(
            "items",
            distinct=True,
        ),
        photo_count=Count(
            "items",
            filter=Q(
                items__media_type="photo"
            ),
            distinct=True,
        ),
        video_count=Count(
            "items",
            filter=Q(
                items__media_type="video"
            ),
            distinct=True,
        ),
    ).order_by(
        "-created_at"
    )

    context = {
        "albums": albums,

        "album_count": Album.objects.count(),

        "media_count": MediaItem.objects.count(),

        "photo_count": MediaItem.objects.filter(
            media_type="photo"
        ).count(),

        "video_count": MediaItem.objects.filter(
            media_type="video"
        ).count(),

        "document_count": MediaItem.objects.filter(
            media_type="document"
        ).count(),
    }

    return render(
        request,
        "reports/media.html",
        context,
    )
