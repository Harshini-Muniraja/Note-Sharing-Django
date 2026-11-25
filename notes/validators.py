import os

from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".txt", ".md", ".png", ".jpg", ".jpeg",
}
MAX_UPLOAD_MB = 10
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def validate_upload(uploaded):
    """Allow only known document/image types up to MAX_UPLOAD_MB."""
    extension = os.path.splitext(uploaded.name)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValidationError(f"File type not allowed. Allowed types: {allowed}.")
    if uploaded.size > MAX_UPLOAD_BYTES:
        raise ValidationError(f"File is too large. The limit is {MAX_UPLOAD_MB} MB.")
