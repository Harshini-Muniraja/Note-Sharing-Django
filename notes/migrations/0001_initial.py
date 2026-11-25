import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import notes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("file", models.FileField(upload_to=notes.models.note_upload_path)),
                ("original_name", models.CharField(blank=True, editable=False, max_length=255)),
                (
                    "is_shared",
                    models.BooleanField(
                        default=False,
                        help_text="If ticked, other logged-in users can see and download this note.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
            },
        ),
    ]
