import os
import uuid

from django.conf import settings
from django.db import models


def note_upload_path(instance, filename):
    """Store files under a random name so uploaded names cannot collide or be guessed."""
    extension = os.path.splitext(filename)[1].lower()
    return f"notes/user_{instance.owner_id}/{uuid.uuid4().hex}{extension}"


class Note(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes"
    )
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=note_upload_path)
    original_name = models.CharField(max_length=255, editable=False, blank=True)
    is_shared = models.BooleanField(
        default=False,
        help_text="If ticked, other logged-in users can see and download this note.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title

    def can_view(self, user):
        return self.is_shared or (user.is_authenticated and user.pk == self.owner_id)
