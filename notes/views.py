from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from firebase_admin import firestore, storage, auth
from google.cloud.firestore import FieldFilter, Query
from urllib.parse import unquote, urlparse
import uuid
import json

# --- CẤU HÌNH ---
db = firestore.client()


# ==========================================
# HÀM PHỤ TRỢ (HELPER FUNCTIONS)
# ==========================================
def _get_user_info(uid):
    try:
        user_doc = db.collection("users").document(uid).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}

        email = user_data.get("email", "User")
        username = user_data.get("username", email)
        avatar = user_data.get("avatar_url")
        if not avatar:
            avatar = (
                f"https://ui-avatars.com/api/?name={username}&background=random&color=fff"
            )
        return username, email, avatar
    except Exception:
        return "User", "", "https://ui-avatars.com/api/?name=User&background=random&color=fff"


def _get_uid_from_email(email):
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except:
        return None


def handle_uploaded_file(f, uid):
    try:
        ext = f.name.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        bucket = storage.bucket()
        blob = bucket.blob(f"note_images/{uid}/{filename}")
        blob.upload_from_file(f, content_type=f.content_type)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"Lỗi upload ảnh note: {e}")
        return None


def _delete_image_from_storage(image_url):
    if not image_url: return
    try:
        bucket = storage.bucket()
        parsed_url = urlparse(unquote(image_url))
        path = parsed_url.path
        if path.startswith("/"): path = path[1:]
        bucket_name = bucket.name
        if path.startswith(bucket_name):
            blob_name = path[len(bucket_name)+1:]
        elif "note_images/" in path:
            blob_name = path[path.find("note_images/"):]
        else: return 
        blob = bucket.blob(blob_name)
        if blob.exists(): blob.delete()
    except Exception as e:
        print(f"Lỗi khi xóa ảnh khỏi Storage: {e}")


# ==========================================
# 1. TRANG CHỦ & DANH SÁCH
# ==========================================
def index_page(request):
    if request.session.get("uid"): return redirect("note-list")
    return render(request, "index.html")


def note_list(request):
    uid = request.session.get("uid")
    if not uid: return redirect("login")
    
    username, user_email, avatar = _get_user_info(uid)
    all_notes = []

    notes_ref = db.collection("users").document(uid).collection("notes")
    try:
        docs_generator = (
            notes_ref
            .where(filter=FieldFilter("is_trashed", "==", False))
            .order_by("is_pinned", direction=Query.DESCENDING)
            .order_by("created_at", direction=Query.DESCENDING)
            .stream()
        )
        my_docs = list(docs_generator)
    except Exception as e:
        print(f"⚠️ Warning: Fallback query: {e}")
        fallback_query = notes_ref.where(filter=FieldFilter("is_trashed", "==", False)).stream()
        my_docs = list(fallback_query)

    for doc in my_docs:
        note = doc.to_dict()
        note["id"] = doc.id
        note["is_owner"] = True
        if "labels" not in note: note["labels"] = []
        all_notes.append(note)

    try:
        shared_docs = db.collection_group("notes").where(
            filter=FieldFilter("shared_with", "array_contains", uid)
        ).stream()
        shared_list = list(shared_docs)
        for doc in shared_list:
            note = doc.to_dict()
            if not note.get("is_trashed", False):
                note["id"] = doc.id
                note["is_owner"] = False
                note["shared_label"] = "Được chia sẻ"
                all_notes.append(note)
    except Exception as e:
        print(f"Lỗi lấy shared notes: {e}")

    all_notes = sorted(
        all_notes,
        key=lambda x: (x.get("is_pinned", False), x.get("created_at", "")),
        reverse=True,
    )

    return render(
        request,
        "notes/note_list.html",
        {
            "notes": all_notes,
            "avatar_url": avatar,
            "user_email": user_email,
            "username": username,
            "view_mode": "list"
        },
    )


def label_filter(request, label_name):
    uid = request.session.get("uid")
    if not uid: return redirect("login")
    
    username, _, avatar = _get_user_info(uid)
    notes_ref = db.collection("users").document(uid).collection("notes")
    
    try:
        docs = notes_ref.where(
            filter=FieldFilter("labels", "array_contains", label_name)
        ).where(
            filter=FieldFilter("is_trashed", "==", False)
        ).stream()
        docs_list = list(docs)
    except Exception:
        docs_list = []

    filtered_notes = []
    for doc in docs_list:
        note = doc.to_dict()
        note["id"] = doc.id
        note["is_owner"] = True
        filtered_notes.append(note)

    return render(request, "notes/note_list.html", {
        "notes": filtered_notes,
        "avatar_url": avatar,
        "username": username,
        "current_label": label_name,
    })


def trash_list(request):
    uid = request.session.get("uid")
    if not uid: return redirect("login")

    notes_ref = db.collection("users").document(uid).collection("notes")
    try:
        docs = (
            notes_ref
            .where(filter=FieldFilter("is_trashed", "==", True))
            .order_by("created_at", direction=Query.DESCENDING)
            .stream()
        )
        trash_docs = list(docs)
    except Exception:
        docs = notes_ref.where(filter=FieldFilter("is_trashed", "==", True)).stream()
        trash_docs = list(docs)

    trash_notes = []
    for doc in trash_docs:
        note = doc.to_dict()
        note["id"] = doc.id
        if "labels" not in note: note["labels"] = []
        trash_notes.append(note)
    
    trash_notes = sorted(trash_notes, key=lambda x: x.get("created_at", ""), reverse=True)
    username, _, avatar = _get_user_info(uid)

    return render(
        request,
        "notes/trash.html",
        {"notes": trash_notes, "username": username, "avatar_url": avatar},
    )


# ==========================================
# 2. CÁC API XỬ LÝ (CREATE/UPDATE/DELETE)
# ==========================================

def create_note(request):
    if request.method == "POST":
        uid = request.session.get("uid")
        if not uid: return JsonResponse({"error": "Unauthorized"}, status=401)

        title = request.POST.get("title", "")
        content = request.POST.get("content", "")
        color = request.POST.get("color", "")
        is_pinned = request.POST.get("is_pinned") == "true"
        reminder = request.POST.get("reminder", "")
        
        try: labels = json.loads(request.POST.get("labels", "[]"))
        except: labels = []

        shared_emails = request.POST.get("shared_emails", "")
        shared_with = []
        if shared_emails:
            for email in shared_emails.split(","):
                email = email.strip()
                if email:
                    friend_uid = _get_uid_from_email(email)
                    if friend_uid and friend_uid != uid:
                        shared_with.append(friend_uid)

        image_url = ""
        if "image" in request.FILES:
            image_url = handle_uploaded_file(request.FILES["image"], uid)

        try:
            note_data = {
                "title": title,
                "content": content,
                "color": color,
                "image_url": image_url if image_url else "",
                "is_pinned": is_pinned,
                "is_trashed": False,
                "labels": labels,
                "shared_with": shared_with,
                "reminder_time": reminder,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
            }
            _, note_ref = db.collection("users").document(uid).collection("notes").add(note_data)
            return JsonResponse({"status": "success", "id": note_ref.id, "image_url": image_url if image_url else ""})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def note_update(request, note_id):
    if request.method == "POST":
        uid = request.session.get("uid")
        if not uid: return JsonResponse({"error": "Unauthorized"}, status=401)

        note_ref = db.collection("users").document(uid).collection("notes").document(note_id)

        try:
            update_data = {"updated_at": firestore.SERVER_TIMESTAMP}
            if "title" in request.POST: update_data["title"] = request.POST.get("title")
            if "content" in request.POST: update_data["content"] = request.POST.get("content")
            if "color" in request.POST: update_data["color"] = request.POST.get("color")
            if "is_pinned" in request.POST: update_data["is_pinned"] = request.POST.get("is_pinned") == "true"
            if "reminder" in request.POST: update_data["reminder_time"] = request.POST.get("reminder")

            if "labels" in request.POST:
                try: update_data["labels"] = json.loads(request.POST.get("labels"))
                except: pass

            if "shared_emails" in request.POST:
                shared_emails = request.POST.get("shared_emails", "")
                shared_with = []
                for email in shared_emails.split(","):
                    email = email.strip()
                    if email:
                        friend_uid = _get_uid_from_email(email)
                        if friend_uid and friend_uid != uid:
                            shared_with.append(friend_uid)
                update_data["shared_with"] = shared_with

            if "image" in request.FILES:
                new_image_url = handle_uploaded_file(request.FILES["image"], uid)
                if new_image_url: update_data["image_url"] = new_image_url

            note_ref.update(update_data)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def note_delete(request, note_id):
    uid = request.session.get("uid")
    if not uid: return redirect("login")
    try:
        db.collection("users").document(uid).collection("notes").document(note_id).update(
            {"is_trashed": True, "is_pinned": False, "updated_at": firestore.SERVER_TIMESTAMP}
        )
        messages.success(request, "Đã chuyển vào thùng rác.")
    except Exception as e: messages.error(request, f"Lỗi: {e}")
    return redirect("note-list")


def note_restore(request, note_id):
    uid = request.session.get("uid")
    if not uid: return redirect("login")
    try:
        db.collection("users").document(uid).collection("notes").document(note_id).update(
            {"is_trashed": False, "updated_at": firestore.SERVER_TIMESTAMP}
        )
        messages.success(request, "Đã khôi phục ghi chú.")
    except Exception: messages.error(request, "Lỗi khôi phục.")
    return redirect("trash-list")


def note_permanent_delete(request, note_id):
    uid = request.session.get("uid")
    if not uid: return redirect("login")
    try:
        note_ref = db.collection("users").document(uid).collection("notes").document(note_id)
        note_doc = note_ref.get()
        if note_doc.exists:
            note_data = note_doc.to_dict()
            image_url = note_data.get("image_url")
            if image_url: _delete_image_from_storage(image_url)
            note_ref.delete()
            messages.success(request, "Đã xóa vĩnh viễn.")
        else: messages.warning(request, "Ghi chú không tồn tại.")
    except Exception: messages.error(request, "Lỗi xóa.")
    return redirect("trash-list")