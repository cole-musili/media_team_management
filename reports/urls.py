from django.urls import path

from .views import (
    attendance_report,
    equipment_report,
    event_report,
    media_report,
    member_report,
    reports_dashboard,
)


urlpatterns = [

    path(
        "",
        reports_dashboard,
        name="reports_dashboard",
    ),

    path(
        "attendance/",
        attendance_report,
        name="attendance_report",
    ),

    path(
        "equipment/",
        equipment_report,
        name="equipment_report",
    ),

    path(
        "events/",
        event_report,
        name="event_report",
    ),

    path(
        "members/",
        member_report,
        name="member_report",
    ),

    path(
        "media/",
        media_report,
        name="media_report",
    ),

]