from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required

from .models import Event


# ============================================================
# EVENTS
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def event_list(request):
    events = Event.objects.all()

    search = request.GET.get("search", "").strip()
    event_type = request.GET.get("event_type", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        events = events.filter(
            Q(name__icontains=search)
            | Q(location__icontains=search)
            | Q(description__icontains=search)
        )

    if event_type:
        events = events.filter(event_type=event_type)

    if status:
        events = events.filter(status=status)

    context = {
        "events": events,
        "search": search,
        "selected_type": event_type,
        "selected_status": status,
        "event_types": Event.TYPES,
        "event_statuses": Event.STATUS,
        "total_events": Event.objects.count(),
        "scheduled_events": Event.objects.filter(
            status="scheduled"
        ).count(),
        "completed_events": Event.objects.filter(
            status="completed"
        ).count(),
        "cancelled_events": Event.objects.filter(
            status="cancelled"
        ).count(),
    }

    return render(request, "events/list.html", context)


@role_required("admin", "coordinator", "team_member", "viewer")
def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.prefetch_related(
            "assignments__member",
            "assignments__position",
            "attendance__member",
            "equipment_checkouts__equipment",
        ),
        pk=pk,
    )

    assignments = event.assignments.all()
    attendance = event.attendance.all()
    checkouts = event.equipment_checkouts.all()

    context = {
        "event": event,
        "assignments": assignments,
        "attendance": attendance,
        "checkouts": checkouts,
        "assignment_count": assignments.count(),
        "attendance_count": attendance.count(),
        "equipment_count": checkouts.count(),
    }

    return render(
        request,
        "events/detail.html",
        context,
    )


@role_required("admin", "coordinator")
def event_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        event_type = request.POST.get("event_type", "service")
        status = request.POST.get("status", "scheduled")
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time") or None
        call_time = request.POST.get("call_time") or None
        location = request.POST.get("location", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Event name is required.")

            return render(
                request,
                "events/form.html",
                {
                    "form_data": request.POST,
                    "event_types": Event.TYPES,
                    "event_statuses": Event.STATUS,
                },
            )

        if not date:
            messages.error(request, "Event date is required.")

            return render(
                request,
                "events/form.html",
                {
                    "form_data": request.POST,
                    "event_types": Event.TYPES,
                    "event_statuses": Event.STATUS,
                },
            )

        if not start_time:
            messages.error(request, "Event start time is required.")

            return render(
                request,
                "events/form.html",
                {
                    "form_data": request.POST,
                    "event_types": Event.TYPES,
                    "event_statuses": Event.STATUS,
                },
            )

        event = Event.objects.create(
            name=name,
            event_type=event_type,
            status=status,
            date=date,
            start_time=start_time,
            end_time=end_time,
            call_time=call_time,
            location=location,
            description=description,
            created_by=(
                request.user
                if request.user.is_authenticated
                else None
            ),
        )

        messages.success(
            request,
            f"{event.name} was created successfully.",
        )

        return redirect("event_detail", pk=event.pk)

    return render(
        request,
        "events/form.html",
        {
            "event_types": Event.TYPES,
            "event_statuses": Event.STATUS,
        },
    )


@role_required("admin", "coordinator")
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Event name is required.")

            return render(
                request,
                "events/form.html",
                {
                    "event": event,
                    "editing": True,
                    "event_types": Event.TYPES,
                    "event_statuses": Event.STATUS,
                },
            )

        event.name = name
        event.event_type = request.POST.get(
            "event_type",
            event.event_type,
        )
        event.status = request.POST.get(
            "status",
            event.status,
        )
        event.date = request.POST.get(
            "date",
            event.date,
        )
        event.start_time = request.POST.get(
            "start_time",
            event.start_time,
        )
        event.end_time = request.POST.get("end_time") or None
        event.call_time = request.POST.get("call_time") or None
        event.location = request.POST.get("location", "").strip()
        event.description = request.POST.get(
            "description",
            "",
        ).strip()

        event.save()

        messages.success(
            request,
            f"{event.name} was updated successfully.",
        )

        return redirect("event_detail", pk=event.pk)

    return render(
        request,
        "events/form.html",
        {
            "event": event,
            "editing": True,
            "event_types": Event.TYPES,
            "event_statuses": Event.STATUS,
        },
    )


@role_required("admin", "coordinator")
def event_status_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        status = request.POST.get("status")

        valid_statuses = dict(Event.STATUS)

        if status not in valid_statuses:
            messages.error(request, "Invalid event status.")
            return redirect("event_detail", pk=event.pk)

        event.status = status
        event.save(update_fields=["status"])

        messages.success(
            request,
            f"Event status changed to {event.get_status_display()}.",
        )

    return redirect("event_detail", pk=event.pk)
