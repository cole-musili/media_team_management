from django.db import models
from django.contrib.auth.models import User



class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="media_member")
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=100, help_text="e.g. Camera Operator, Sound, Streaming")
    skills = models.ManyToManyField(Skill, blank=True)
    profile_photo = models.ImageField(upload_to="members/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self): return self.name

class Availability(models.Model):
    STATUS_CHOICES = [("available","Available"),("unavailable","Not available"),("maybe","Maybe")]
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="availability")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    class Meta:
        unique_together = ("member","date")
    def __str__(self): return f"{self.member} - {self.date} - {self.status}"


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("coordinator", "Media Coordinator"),
        ("team_member", "Team Member"),
        ("viewer", "Viewer"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    member = models.OneToOneField(
        "Member",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profile",
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="team_member",
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"