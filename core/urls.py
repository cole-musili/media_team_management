from django.urls import path
from .views import dashboard, service_worker

urlpatterns = [
    path("", dashboard, name="dashboard"),

    path(
        "service-worker.js",
        service_worker,
        name="service_worker",
    ),
]
