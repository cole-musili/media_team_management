from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("core.urls")),
    path("", include("accounts.urls")),
    
    path("members/", include("members.urls")),
    path("events/", include("events.urls")),
    path("roster/", include("roster.urls")),
    path("attendance/", include("attendance.urls")),
    path("equipment/", include("equipment.urls")),
    path("media-library/", include("media_library.urls")),
    path("reports/", include("reports.urls")),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
