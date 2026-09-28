from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required

from .models import Availability, Member, Skill


# ============================================================
# MEMBERS
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def member_list(request):
    members = Member.objects.prefetch_related("skills").all()

    search = request.GET.get("search", "").strip()
    role = request.GET.get("role", "").strip()
    status = request.GET.get("status", "active").strip()

    if search:
        members = members.filter(
            Q(name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
            | Q(role__icontains=search)
        )

    if role:
        members = members.filter(role=role)

    if status == "active":
        members = members.filter(is_active=True)
    elif status == "inactive":
        members = members.filter(is_active=False)

    roles = (
        Member.objects.exclude(role="")
        .values_list("role", flat=True)
        .distinct()
        .order_by("role")
    )

    context = {
        "members": members,
        "roles": roles,
        "search": search,
        "selected_role": role,
        "selected_status": status,
        "total_members": Member.objects.count(),
        "active_members": Member.objects.filter(is_active=True).count(),
        "inactive_members": Member.objects.filter(is_active=False).count(),
    }

    return render(request, "members/list.html", context)


@role_required("admin", "coordinator", "team_member", "viewer")
def member_detail(request, pk):
    member = get_object_or_404(
        Member.objects.prefetch_related("skills", "availability"),
        pk=pk,
    )

    availability = member.availability.order_by("-date")[:10]

    return render(
        request,
        "members/detail.html",
        {
            "member": member,
            "availability": availability,
        },
    )


@role_required("admin", "coordinator")
def member_create(request):
    skills = Skill.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        role = request.POST.get("role", "").strip()
        joined_date = request.POST.get("joined_date") or None
        notes = request.POST.get("notes", "").strip()
        selected_skills = request.POST.getlist("skills")

        if not name:
            messages.error(request, "Member name is required.")

            return render(
                request,
                "members/form.html",
                {
                    "skills": skills,
                    "form_data": request.POST,
                },
            )

        member = Member.objects.create(
            name=name,
            phone=phone,
            email=email,
            role=role,
            joined_date=joined_date,
            notes=notes,
            is_active=True,
        )

        if request.FILES.get("profile_photo"):
            member.profile_photo = request.FILES["profile_photo"]
            member.save()

        if selected_skills:
            member.skills.set(selected_skills)

        messages.success(
            request,
            f"{member.name} was added successfully.",
        )

        return redirect("member_detail", pk=member.pk)

    return render(
        request,
        "members/form.html",
        {"skills": skills},
    )


@role_required("admin", "coordinator")
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    skills = Skill.objects.all().order_by("name")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Member name is required.")

            return render(
                request,
                "members/form.html",
                {
                    "member": member,
                    "skills": skills,
                    "editing": True,
                },
            )

        member.name = name
        member.phone = request.POST.get("phone", "").strip()
        member.email = request.POST.get("email", "").strip()
        member.role = request.POST.get("role", "").strip()
        member.joined_date = request.POST.get("joined_date") or None
        member.notes = request.POST.get("notes", "").strip()

        if request.FILES.get("profile_photo"):
            member.profile_photo = request.FILES["profile_photo"]

        member.save()

        selected_skills = request.POST.getlist("skills")
        member.skills.set(selected_skills)

        messages.success(
            request,
            f"{member.name}'s profile was updated.",
        )

        return redirect("member_detail", pk=member.pk)

    return render(
        request,
        "members/form.html",
        {
            "member": member,
            "skills": skills,
            "editing": True,
        },
    )


@role_required("admin", "coordinator")
def member_toggle_status(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        member.is_active = not member.is_active
        member.save(update_fields=["is_active"])

        if member.is_active:
            messages.success(
                request,
                f"{member.name} is now active.",
            )
        else:
            messages.warning(
                request,
                f"{member.name} has been deactivated.",
            )

    return redirect("member_detail", pk=member.pk)


@role_required("admin", "coordinator")
def availability_update(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == "POST":
        date = request.POST.get("date")
        status = request.POST.get("status")
        note = request.POST.get("note", "").strip()

        if date and status:
            Availability.objects.update_or_create(
                member=member,
                date=date,
                defaults={
                    "status": status,
                    "note": note,
                },
            )

            messages.success(
                request,
                f"Availability updated for {member.name}.",
            )

    return redirect("member_detail", pk=member.pk)


# ============================================================
# SKILLS
# ============================================================

@role_required("admin", "coordinator", "team_member", "viewer")
def skill_list(request):
    skills = Skill.objects.all().order_by("name")

    return render(
        request,
        "members/skills.html",
        {
            "skills": skills,
        },
    )


@role_required("admin", "coordinator")
def skill_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Skill name is required.")

            return render(
                request,
                "members/skill_form.html",
                {
                    "form_data": request.POST,
                },
            )

        if Skill.objects.filter(name__iexact=name).exists():
            messages.error(
                request,
                "A skill with this name already exists.",
            )

            return render(
                request,
                "members/skill_form.html",
                {
                    "form_data": request.POST,
                },
            )

        skill = Skill.objects.create(
            name=name,
            description=description,
        )

        messages.success(
            request,
            f"{skill.name} was created successfully.",
        )

        return redirect("skill_list")

    return render(
        request,
        "members/skill_form.html",
    )


@role_required("admin", "coordinator")
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Skill name is required.")

            return render(
                request,
                "members/skill_form.html",
                {
                    "skill": skill,
                    "editing": True,
                },
            )

        duplicate = Skill.objects.filter(
            name__iexact=name
        ).exclude(pk=skill.pk)

        if duplicate.exists():
            messages.error(
                request,
                "A skill with this name already exists.",
            )

            return render(
                request,
                "members/skill_form.html",
                {
                    "skill": skill,
                    "editing": True,
                },
            )

        skill.name = name
        skill.description = description
        skill.save()

        messages.success(
            request,
            f"{skill.name} was updated successfully.",
        )

        return redirect("skill_list")

    return render(
        request,
        "members/skill_form.html",
        {
            "skill": skill,
            "editing": True,
        },
    )


@role_required("admin", "coordinator")
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk)

    if request.method == "POST":
        name = skill.name
        skill.delete()

        messages.success(
            request,
            f"{name} was deleted.",
        )

    return redirect("skill_list")
