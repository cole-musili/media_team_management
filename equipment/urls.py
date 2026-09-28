from django.urls import path

from .views import (
    category_create,
    category_list,
    equipment_checkout,
    equipment_create,
    equipment_detail,
    equipment_edit,
    equipment_list,
    equipment_return,
    maintenance_create,
)


urlpatterns = [

    path(
        "",
        equipment_list,
        name="equipment_list",
    ),

    path(
        "add/",
        equipment_create,
        name="equipment_create",
    ),

    path(
        "categories/",
        category_list,
        name="equipment_categories",
    ),

    path(
        "categories/add/",
        category_create,
        name="equipment_category_create",
    ),

    path(
        "<int:pk>/",
        equipment_detail,
        name="equipment_detail",
    ),

    path(
        "<int:pk>/edit/",
        equipment_edit,
        name="equipment_edit",
    ),

    path(
        "<int:pk>/checkout/",
        equipment_checkout,
        name="equipment_checkout",
    ),

    path(
        "checkout/<int:checkout_id>/return/",
        equipment_return,
        name="equipment_return",
    ),

    path(
        "<int:pk>/maintenance/add/",
        maintenance_create,
        name="maintenance_create",
    ),
]