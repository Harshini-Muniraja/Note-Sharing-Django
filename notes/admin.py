from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_shared", "updated_at")
    list_filter = ("is_shared",)
    search_fields = ("title", "description", "owner__username")
