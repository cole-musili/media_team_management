from django.contrib import admin

from .models import Availability, Member, Skill, UserProfile


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "role",
        "phone",
        "email",
        "is_active",
        "joined_date",
    )

    list_filter = (
        "is_active",
        "role",
        "skills",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "role",
    )

    filter_horizontal = ("skills",)

    readonly_fields = ("user",)

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "name",
                    "profile_photo",
                    "phone",
                    "email",
                )
            },
        ),
        (
            "Media Team",
            {
                "fields": (
                    "role",
                    "skills",
                    "is_active",
                    "joined_date",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": (
                    "notes",
                    "user",
                )
            },
        ),
    )


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "member",
        "date",
        "status",
        "note",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "member__name",
        "note",
    )

    date_hierarchy = "date"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "member",
        "role",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "member__name",
    )