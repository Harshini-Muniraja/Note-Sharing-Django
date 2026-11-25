import os

from django import forms

from notesite.utils import apply_bootstrap

from .models import Note
from .validators import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, validate_upload


class NoteForm(forms.ModelForm):
    file = forms.FileField(
        validators=[validate_upload],
        help_text=f"Up to {MAX_UPLOAD_MB} MB. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
    )

    class Meta:
        model = Note
        fields = ["title", "description", "file", "is_shared"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap(self)

    def save(self, commit=True):
        note = super().save(commit=False)
        new_file = self.files.get("file")
        old_file = None
        if new_file:
            note.original_name = os.path.basename(new_file.name)
            if note.pk:
                # Keep a handle on the previous file so it can be removed after saving.
                old_file = Note.objects.get(pk=note.pk).file
        if commit:
            note.save()
            if old_file:
                old_file.delete(save=False)
        return note
