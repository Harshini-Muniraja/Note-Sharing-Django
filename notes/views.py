import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NoteForm
from .models import Note


def _search(queryset, request):
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return queryset, query


@login_required
def my_notes(request):
    notes, query = _search(Note.objects.filter(owner=request.user), request)
    return render(request, "notes/my_notes.html", {"notes": notes, "q": query})


@login_required
def shared_notes(request):
    notes, query = _search(Note.objects.filter(is_shared=True).select_related("owner"), request)
    return render(request, "notes/shared_notes.html", {"notes": notes, "q": query})


@login_required
def note_create(request):
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.owner = request.user
            note.save()
            messages.success(request, "Note uploaded.")
            return redirect("notes:my_notes")
    else:
        form = NoteForm()
    return render(request, "notes/note_form.html", {"form": form, "heading": "Upload a note"})


@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated.")
            return redirect("notes:my_notes")
    else:
        form = NoteForm(instance=note)
    return render(request, "notes/note_form.html", {"form": form, "heading": "Edit note"})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == "POST":
        note.file.delete(save=False)
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("notes:my_notes")
    return render(request, "notes/note_confirm_delete.html", {"note": note})


@login_required
def note_download(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if not note.can_view(request.user):
        raise Http404("Note not found.")
    try:
        handle = note.file.open("rb")
    except FileNotFoundError:
        raise Http404("The file for this note is missing.")
    filename = note.original_name or os.path.basename(note.file.name)
    return FileResponse(handle, as_attachment=True, filename=filename)
