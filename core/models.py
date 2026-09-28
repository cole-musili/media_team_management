from django.db import models
class Announcement(models.Model):
    PRIORITY = [("normal","Normal"),("important","Important"),("urgent","Urgent")]
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY, default="normal")
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title
