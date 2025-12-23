from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_page, name="index-page"),
    path("notes/", views.note_list, name="note-list"),
    path("label/<str:label_name>/", views.label_filter, name="label-filter"), 
    path("trash/", views.trash_list, name="trash-list"),
    path("api/create-note/", views.create_note, name="create-note"),
    path("api/bulk-action/", views.bulk_action, name="bulk-action"), # [MỚI]
    path("notes/<str:note_id>/edit/", views.note_update, name="note-update"),
    path("notes/<str:note_id>/delete/", views.note_delete, name="note-delete"),
    path("notes/<str:note_id>/restore/", views.note_restore, name="note-restore"),
    path(
        "notes/<str:note_id>/destroy/",
        views.note_permanent_delete,
        name="note-permanent-delete",
    ),
]