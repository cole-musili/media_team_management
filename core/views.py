from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from attendance.models import Attendance
from equipment.models import Equipment
from events.models import Event
from media_library.models import Album, MediaItem
from members.models import Member
from roster.models import DutyAssignment
from core.models import Announcement

from accounts.permissions import get_user_role


@login_required
def dashboard(request):
    today = timezone.localdate()
    role = get_user_role(request.user)

    # ---------------------------------------------------------
    # Current logged-in user's media member
    # ---------------------------------------------------------

    member = getattr(
        request.user,
        "media_member",
        None,
    )

    # ---------------------------------------------------------
    # Upcoming events
    # ---------------------------------------------------------

    upcoming_events = (
        Event.objects
        .filter(
            date__gte=today
        )
        .exclude(
            status="cancelled"
        )
        .order_by(
            "date",
            "start_time"
        )[:5]
    )

    # ---------------------------------------------------------
    # Recent events
    # ---------------------------------------------------------

    recent_events = (
        Event.objects
        .order_by(
            "-date",
            "-start_time"
        )[:5]
    )

    # ---------------------------------------------------------
    # Members
    # ---------------------------------------------------------

    member_count = Member.objects.filter(
        is_active=True
    ).count()

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------

    event_count = (
        Event.objects
        .filter(
            date__gte=today
        )
        .exclude(
            status="cancelled"
        )
        .count()
    )

    # ---------------------------------------------------------
    # Equipment
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Media
    # ---------------------------------------------------------

    media_count = MediaItem.objects.count()
    album_count = Album.objects.count()

    # ---------------------------------------------------------
    # TODAY'S ATTENDANCE
    # ---------------------------------------------------------

    todays_attendance = (
        Attendance.objects
        .filter(
            event__date=today
        )
        .select_related(
            "event",
            "member",
        )
    )

    attendance_today = todays_attendance.count()

    attendance_present = todays_attendance.filter(
        status="present"
    ).count()

    attendance_late = todays_attendance.filter(
        status="late"
    ).count()

    attendance_absent = todays_attendance.filter(
        status="absent"
    ).count()

    attendance_excused = todays_attendance.filter(
        status="excused"
    ).count()

    # ---------------------------------------------------------
    # MY LATEST ATTENDANCE
    #
    # This is separate from today's attendance.
    # It allows a team member to see their latest check-in
    # even when the event is not today.
    # ---------------------------------------------------------

    my_attendance = Attendance.objects.none()

    if member:
        my_attendance = (
            Attendance.objects
            .filter(
                member=member
            )
            .select_related(
                "event",
                "member",
            )
            .order_by(
                "-event__date",
                "-check_in",
                "-id",
            )[:5]
        )

    # ---------------------------------------------------------
    # RECENT TEAM ATTENDANCE
    #
    # Used by admin/coordinator dashboard.
    # ---------------------------------------------------------

    recent_attendance = (
        Attendance.objects
        .select_related(
            "event",
            "member",
        )
        .order_by(
            "-event__date",
            "-check_in",
            "-id",
        )[:8]
    )

    # ---------------------------------------------------------
    # Pending duty confirmations
    # ---------------------------------------------------------

    pending_assignments = (
        DutyAssignment.objects
        .filter(
            status="pending",
            event__date__gte=today,
        )
        .exclude(
            event__status="cancelled"
        )
        .select_related(
            "event",
            "position",
            "member",
        )
        .order_by(
            "event__date",
            "event__start_time",
            "position__name",
        )[:5]
    )

    # ---------------------------------------------------------
    # My pending assignments
    # ---------------------------------------------------------

    my_pending_assignments = DutyAssignment.objects.none()

    if member:
        my_pending_assignments = (
            DutyAssignment.objects
            .filter(
                member=member,
                status="pending",
                event__date__gte=today,
            )
            .exclude(
                event__status="cancelled"
            )
            .select_related(
                "event",
                "position",
                "member",
            )
            .order_by(
                "event__date",
                "event__start_time",
                "position__name",
            )[:5]
        )

    # ---------------------------------------------------------
    # Today's duties
    # ---------------------------------------------------------

    todays_duties = (
        DutyAssignment.objects
        .filter(
            event__date=today
        )
        .exclude(
            event__status="cancelled"
        )
        .select_related(
            "event",
            "position",
            "member",
        )
        .order_by(
            "event__start_time",
            "position__name",
        )
    )

    # ---------------------------------------------------------
    # My today's duties
    # ---------------------------------------------------------

    my_todays_duties = DutyAssignment.objects.none()

    if member:
        my_todays_duties = (
            DutyAssignment.objects
            .filter(
                member=member,
                event__date=today,
            )
            .exclude(
                event__status="cancelled"
            )
            .select_related(
                "event",
                "position",
                "member",
            )
            .order_by(
                "event__start_time",
                "position__name",
            )
        )

    # ---------------------------------------------------------
    # Announcements
    # ---------------------------------------------------------

    announcements = (
        Announcement.objects
        .filter(
            published=True
        )
        .order_by(
            "-created_at"
        )[:5]
    )

    # ---------------------------------------------------------
    # Dashboard context
    # ---------------------------------------------------------

    context = {
        "today": today,

        # Main statistics
        "member_count": member_count,
        "event_count": event_count,
        "equipment_count": equipment_count,
        "available_equipment": available_equipment,

        # Equipment breakdown
        "equipment_in_use": equipment_in_use,
        "equipment_maintenance": equipment_maintenance,
        "equipment_damaged": equipment_damaged,

        # Media
        "media_count": media_count,
        "album_count": album_count,

        # Today's attendance
        "attendance_today": attendance_today,
        "attendance_present": attendance_present,
        "attendance_late": attendance_late,
        "attendance_absent": attendance_absent,
        "attendance_excused": attendance_excused,

        # Personal/latest attendance
        "my_attendance": my_attendance,
        "recent_attendance": recent_attendance,

        # Events
        "upcoming_events": upcoming_events,
        "recent_events": recent_events,

        # Roster
        "todays_duties": (
            my_todays_duties
            if role == "team_member"
            else todays_duties
        ),

        "pending_assignments": (
            my_pending_assignments
            if role == "team_member"
            else pending_assignments
        ),

        # Announcements
        "announcements": announcements,

        # User/member
        "dashboard_role": role,
        "dashboard_member": member,
    }

    return render(
        request,
        "core/dashboard.html",
        context,
    )


def service_worker(request):
    javascript = """
const CACHE_NAME = "church-media-v1";

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches
            .open(CACHE_NAME)
            .then(function (cache) {
                return cache.add("/");
            })
            .then(function () {
                return self.skipWaiting();
            })
    );
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches
            .keys()
            .then(function (cacheNames) {
                return Promise.all(
                    cacheNames
                        .filter(function (name) {
                            return name !== CACHE_NAME;
                        })
                        .map(function (name) {
                            return caches.delete(name);
                        })
                );
            })
            .then(function () {
                return self.clients.claim();
            })
    );
});

self.addEventListener("fetch", function (event) {
    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(function (response) {
                return response;
            })
            .catch(function () {
                return caches.match(event.request);
            })
    );
});
"""

    return HttpResponse(
        javascript,
        content_type="application/javascript",
    )