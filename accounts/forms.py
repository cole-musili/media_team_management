from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from members.models import Member, Skill, UserProfile


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
            }
        ),
    )

    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }
        ),
    )

    profile_photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, member=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.member = member

        if member:
            self.fields["phone"].initial = member.phone
            self.fields["profile_photo"].initial = member.profile_photo

    def save(self, commit=True):
        user = super().save(commit=commit)

        if self.member:
            self.member.phone = self.cleaned_data["phone"]
            self.member.email = self.cleaned_data["email"]

            if self.cleaned_data.get("profile_photo"):
                self.member.profile_photo = self.cleaned_data[
                    "profile_photo"
                ]

            if commit:
                self.member.save()

        return user


class UserCreateForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
            }
        ),
    )

    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Phone number",
            }
        ),
    )

    member_role = forms.CharField(
        max_length=100,
        required=True,
        label="Media Team Position",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. Camera Operator",
            }
        ),
    )

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    system_role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="System Role",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    profile_photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Username",
                    "autocomplete": "off",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Create a password",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        )

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            member = Member.objects.create(
                user=user,
                name=(
                    f"{self.cleaned_data['first_name']} "
                    f"{self.cleaned_data['last_name']}"
                ).strip(),
                phone=self.cleaned_data["phone"],
                email=self.cleaned_data["email"],
                role=self.cleaned_data["member_role"],
                profile_photo=self.cleaned_data.get("profile_photo"),
                is_active=True,
            )

            member.skills.set(self.cleaned_data["skills"])

            UserProfile.objects.create(
                user=user,
                member=member,
                role=self.cleaned_data["system_role"],
            )

        return user


class UserEditForm(forms.ModelForm):

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    member_role = forms.CharField(
        max_length=100,
        required=True,
        label="Media Team Position",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    system_role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="System Role",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    profile_photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
    )

    is_active = forms.BooleanField(
        required=False,
        label="Account active",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": True,
                }
            ),
        }

    def __init__(
        self,
        *args,
        member=None,
        profile=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.member = member
        self.profile = profile

        if member:
            self.fields["phone"].initial = member.phone
            self.fields["member_role"].initial = member.role
            self.fields["skills"].initial = member.skills.all()
            self.fields["profile_photo"].initial = member.profile_photo

        if profile:
            self.fields["system_role"].initial = profile.role

    def save(self, commit=True):
        user = super().save(commit=commit)

        if self.member:
            self.member.name = (
                f"{self.cleaned_data['first_name']} "
                f"{self.cleaned_data['last_name']}"
            ).strip()

            self.member.phone = self.cleaned_data["phone"]
            self.member.email = self.cleaned_data["email"]
            self.member.role = self.cleaned_data["member_role"]
            self.member.is_active = self.cleaned_data["is_active"]

            if self.cleaned_data.get("profile_photo"):
                self.member.profile_photo = self.cleaned_data[
                    "profile_photo"
                ]

            if commit:
                self.member.save()

            self.member.skills.set(
                self.cleaned_data["skills"]
            )

        if self.profile:
            self.profile.role = self.cleaned_data["system_role"]

            if commit:
                self.profile.save()

        return user