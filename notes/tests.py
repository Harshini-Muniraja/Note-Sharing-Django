import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Note

TEMP_MEDIA = tempfile.mkdtemp()
PASSWORD = "S3cure-Pass-9876"


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class NoteAccessTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.alice = User.objects.create_user("alice", "alice@example.com", PASSWORD)
        self.bob = User.objects.create_user("bob", "bob@example.com", PASSWORD)

    def make_note(self, owner, shared=False, title="Lecture notes"):
        return Note.objects.create(
            owner=owner,
            title=title,
            is_shared=shared,
            original_name="notes.txt",
            file=SimpleUploadedFile("notes.txt", b"hello"),
        )

    def test_anonymous_users_are_sent_to_login(self):
        response = self.client.get(reverse("notes:my_notes"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_private_note_cannot_be_downloaded_by_another_user(self):
        note = self.make_note(self.alice)
        self.client.login(username="bob", password=PASSWORD)
        response = self.client.get(reverse("notes:download", args=[note.pk]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_download_private_note(self):
        note = self.make_note(self.alice)
        self.client.login(username="alice", password=PASSWORD)
        response = self.client.get(reverse("notes:download", args=[note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"hello")

    def test_shared_note_can_be_downloaded_by_another_user(self):
        note = self.make_note(self.alice, shared=True)
        self.client.login(username="bob", password=PASSWORD)
        response = self.client.get(reverse("notes:download", args=[note.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_edit_or_delete(self):
        note = self.make_note(self.alice)
        self.client.login(username="bob", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("notes:update", args=[note.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("notes:delete", args=[note.pk])).status_code, 404)
        self.assertTrue(Note.objects.filter(pk=note.pk).exists())

    def test_delete_requires_post_and_removes_note(self):
        note = self.make_note(self.alice)
        self.client.login(username="alice", password=PASSWORD)
        self.client.get(reverse("notes:delete", args=[note.pk]))
        self.assertTrue(Note.objects.filter(pk=note.pk).exists())
        self.client.post(reverse("notes:delete", args=[note.pk]))
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())

    def test_my_notes_lists_only_own_notes_and_supports_search(self):
        self.make_note(self.alice, title="Networking basics")
        self.make_note(self.alice, title="Cryptography")
        self.make_note(self.bob, title="Bob private")
        self.client.login(username="alice", password=PASSWORD)
        response = self.client.get(reverse("notes:my_notes"))
        self.assertContains(response, "Networking basics")
        self.assertNotContains(response, "Bob private")
        response = self.client.get(reverse("notes:my_notes"), {"q": "crypto"})
        self.assertContains(response, "Cryptography")
        self.assertNotContains(response, "Networking basics")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class UploadValidationTests(TestCase):
    def setUp(self):
        User.objects.create_user("alice", "alice@example.com", PASSWORD)
        self.client.login(username="alice", password=PASSWORD)

    def test_valid_upload_is_saved_for_the_logged_in_user(self):
        response = self.client.post(
            reverse("notes:create"),
            {"title": "Week 1", "description": "", "file": SimpleUploadedFile("week1.pdf", b"%PDF-1.4")},
        )
        self.assertRedirects(response, reverse("notes:my_notes"))
        note = Note.objects.get()
        self.assertEqual(note.owner.username, "alice")
        self.assertEqual(note.original_name, "week1.pdf")

    def test_disallowed_file_type_is_rejected(self):
        response = self.client.post(
            reverse("notes:create"),
            {"title": "Bad", "description": "", "file": SimpleUploadedFile("run.exe", b"MZ")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 0)
