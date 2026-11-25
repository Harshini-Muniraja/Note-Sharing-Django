from django.urls import path

from . import views

app_name = "notes"

urlpatterns = [
    path("", views.my_notes, name="my_notes"),
    path("shared/", views.shared_notes, name="shared_notes"),
    path("notes/new/", views.note_create, name="create"),
    path("notes/<int:pk>/edit/", views.note_update, name="update"),
    path("notes/<int:pk>/delete/", views.note_delete, name="delete"),
    path("notes/<int:pk>/download/", views.note_download, name="download"),
]
