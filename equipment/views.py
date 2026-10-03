from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import role_required

from .forms import (
    CheckoutForm,
    EquipmentCategoryForm,
    EquipmentForm,
    MaintenanceForm,
    ReturnEquipmentForm,
)
from .models import (
    Checkout,
    Equipment,
    EquipmentCategory,
    MaintenanceRecord,
)


@role_required("admin", "coordinator", "team_member", "viewer")
def equipment_list(request):

    equipment = (
        Equipment.objects
        .select_related("category")
        .order_by("name")
    )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    category = request.GET.get(
        "category",
        "",
    ).strip()

    status = request.GET.get(
        "status",
        "",
    ).strip()

    if search:

        equipment = equipment.filter(
            Q(equipment_id__icontains=search)
            | Q(name__icontains=search)
            | Q(brand__icontains=search)
            | Q(model__icontains=search)
            | Q(serial_number__icontains=search)
        )

    if category:
        equipment = equipment.filter(
            category_id=category
        )

    if status:
        equipment = equipment.filter(
            status=status
        )

    context = {
        "equipment": equipment,
        "categories": EquipmentCategory.objects.order_by(
            "name"
        ),
        "statuses": Equipment.STATUS,

        "search": search,
        "selected_category": category,
        "selected_status": status,

        "total_equipment": Equipment.objects.count(),

        "available_count": Equipment.objects.filter(
            status="available"
        ).count(),

        "in_use_count": Equipment.objects.filter(
            status="in_use"
        ).count(),

        "maintenance_count": Equipment.objects.filter(
            status="maintenance"
        ).count(),

        "damaged_count": Equipment.objects.filter(
            status="damaged"
        ).count(),

        "missing_count": Equipment.objects.filter(
            status="missing"
        ).count(),
    }

    return render(
        request,
        "equipment/list.html",
        context,
    )


@role_required("admin", "coordinator", "team_member", "viewer")
def equipment_detail(request, pk):

    item = get_object_or_404(
        Equipment.objects
        .select_related("category")
        .prefetch_related(
            "photos",
            "checkouts__member",
            "checkouts__event",
            "maintenance__reported_by",
        ),
        pk=pk,
    )

    active_checkout = (
        item.checkouts
        .filter(
            status__in=[
                "out",
                "overdue",
            ]
        )
        .select_related(
            "member",
            "event",
        )
        .first()
    )

    context = {
        "item": item,
        "active_checkout": active_checkout,

        "checkout_history": item.checkouts.all(),

        "maintenance_records": item.maintenance.all(),

        "photo_count": item.photos.count(),

        "checkout_count": item.checkouts.count(),

        "maintenance_count": item.maintenance.count(),
    }

    return render(
        request,
        "equipment/detail.html",
        context,
    )


@role_required("admin", "coordinator")
def equipment_create(request):

    if request.method == "POST":

        form = EquipmentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            item = form.save()

            messages.success(
                request,
                (
                    f"{item.name} "
                    f"({item.equipment_id}) was added."
                ),
            )

            return redirect(
                "equipment_detail",
                pk=item.pk,
            )

    else:

        form = EquipmentForm()

    return render(
        request,
        "equipment/form.html",
        {
            "form": form,
            "editing": False,
        },
    )


@role_required("admin", "coordinator")
def equipment_edit(request, pk):

    item = get_object_or_404(
        Equipment,
        pk=pk,
    )

    if request.method == "POST":

        form = EquipmentForm(
            request.POST,
            request.FILES,
            instance=item,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Equipment details were updated.",
            )

            return redirect(
                "equipment_detail",
                pk=item.pk,
            )

    else:

        form = EquipmentForm(
            instance=item,
        )

    return render(
        request,
        "equipment/form.html",
        {
            "form": form,
            "item": item,
            "editing": True,
        },
    )


@role_required("admin", "coordinator", "team_member")
def equipment_checkout(request, pk):

    item = get_object_or_404(
        Equipment,
        pk=pk,
    )

    if request.method == "POST":

        form = CheckoutForm(
            request.POST,
            request.FILES,
            equipment=item,
        )

        # Set equipment before form validation
        form.instance.equipment = item

        if form.is_valid():

            checkout = form.save(
                commit=False
            )

            checkout.equipment = item
            checkout.checkout_time = timezone.now()
            checkout.status = "out"

            checkout.save()

            item.status = "in_use"
            item.save(
                update_fields=["status"]
            )

            messages.success(
                request,
                f"{item.name} was checked out successfully.",
            )

            return redirect(
                "equipment_detail",
                pk=item.pk,
            )

    else:

        form = CheckoutForm(
            equipment=item,
            initial={
                "condition_before": item.condition,
            },
        )

    return render(
        request,
        "equipment/checkout_form.html",
        {
            "form": form,
            "item": item,
        },
    )


@role_required("admin", "coordinator")
def equipment_return(request, checkout_id):

    checkout = get_object_or_404(
        Checkout.objects.select_related(
            "equipment",
            "member",
            "event",
        ),
        pk=checkout_id,
    )

    if checkout.status == "returned":

        messages.info(
            request,
            "This equipment has already been returned.",
        )

        return redirect(
            "equipment_detail",
            pk=checkout.equipment.pk,
        )

    if request.method == "POST":

        form = ReturnEquipmentForm(
            request.POST,
            request.FILES,
            instance=checkout,
        )

        if form.is_valid():

            returned = form.save(
                commit=False
            )

            returned.status = "returned"

            if not returned.return_time:
                returned.return_time = timezone.now()

            returned.save()

            equipment = checkout.equipment

            if returned.condition_after:
                equipment.condition = (
                    returned.condition_after
                )

            # If returned in poor condition, flag it.
            if returned.condition_after == "poor":
                equipment.status = "damaged"
            else:
                equipment.status = "available"

            equipment.save(
                update_fields=[
                    "condition",
                    "status",
                ]
            )

            messages.success(
                request,
                (
                    f"{equipment.name} was returned "
                    "successfully."
                ),
            )

            return redirect(
                "equipment_detail",
                pk=equipment.pk,
            )

    else:

        form = ReturnEquipmentForm(
            instance=checkout,
            initial={
                "return_time": timezone.now(),
                "condition_after": (
                    checkout.condition_before
                ),
            },
        )

    return render(
        request,
        "equipment/return_form.html",
        {
            "form": form,
            "checkout": checkout,
        },
    )


@role_required("admin", "coordinator")
def maintenance_create(request, pk):

    item = get_object_or_404(
        Equipment,
        pk=pk,
    )

    if request.method == "POST":

        form = MaintenanceForm(
            request.POST
        )

        if form.is_valid():

            record = form.save(
                commit=False
            )

            record.equipment = item
            record.save()

            if record.status != "completed":
                item.status = "maintenance"

                item.save(
                    update_fields=["status"]
                )

            messages.success(
                request,
                "Maintenance record was created.",
            )

            return redirect(
                "equipment_detail",
                pk=item.pk,
            )

    else:

        form = MaintenanceForm()

    return render(
        request,
        "equipment/maintenance_form.html",
        {
            "form": form,
            "item": item,
        },
    )


@role_required("admin", "coordinator", "team_member", "viewer")
def category_list(request):

    categories = (
        EquipmentCategory.objects
        .prefetch_related("equipment")
        .order_by("name")
    )

    return render(
        request,
        "equipment/categories.html",
        {
            "categories": categories,
        },
    )


@role_required("admin", "coordinator")
def category_create(request):

    if request.method == "POST":

        form = EquipmentCategoryForm(
            request.POST
        )

        if form.is_valid():

            category = form.save()

            messages.success(
                request,
                f"{category.name} was created.",
            )

            return redirect(
                "equipment_categories"
            )

    else:

        form = EquipmentCategoryForm()

    return render(
        request,
        "equipment/category_form.html",
        {
            "form": form,
        },
    )