from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
import requests
import urllib.parse  # <--- THÊM IMPORT NÀY
from .forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordConfirmForm,
    UpdateProfileForm,
    VerifyPasswordForm,
    ChangeEmailForm,
    ChangePhoneForm,
    ChangePasswordFinalForm,
)
from firebase_admin import auth, firestore, storage
from google.cloud.firestore import FieldFilter

# --- CẤU HÌNH ---
db = firestore.client()
FIREBASE_WEB_API_KEY = settings.FIREBASE_WEB_API_KEY


# ==========================================
# HÀM PHỤ TRỢ (HELPER)
# ==========================================
def _get_user_display_info(uid):
    """Lấy thông tin user và avatar an toàn"""
    try:
        user_ref = db.collection("users").document(uid)
        doc = user_ref.get()
        if doc.exists:
            data = doc.to_dict()
            username = data.get("username") or data.get("email", "User")
            avatar = data.get("avatar_url")
            
            # Tạo avatar mặc định nếu không có ảnh
            if not avatar:
                # Mã hóa tên tiếng Việt sang dạng URL an toàn (Ví dụ: Nguyễn -> Nguy%E1%BB%85n)
                safe_username = urllib.parse.quote(username)
                avatar = f"https://ui-avatars.com/api/?name={safe_username}&background=random&color=fff&size=256"
                
            return username, avatar
    except Exception as e:
        print(f"Lỗi lấy info user: {e}")
    
    # Fallback mặc định
    return "User", "https://ui-avatars.com/api/?name=User&background=random&color=fff"


# ==========================================
# 1. ĐĂNG KÝ
# ==========================================
def register(request):
    if request.session.get("uid"):
        return redirect("note-list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            try:
                user = auth.create_user(
                    email=email, password=password, display_name=username
                )
                default_avatar = f"https://ui-avatars.com/api/?name={username}&background=random&color=fff"

                user_data = {
                    "username": username,
                    "email": email,
                    "avatar_url": default_avatar,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "is_new_user": True,
                }
                db.collection("users").document(user.uid).set(user_data)

                messages.success(
                    request, f"Tài khoản {username} đã tạo thành công! Hãy đăng nhập."
                )
                return redirect("login")
            except Exception as e:
                messages.error(request, f"Lỗi đăng ký: {str(e)}")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


# ==========================================
# 2. ĐĂNG NHẬP
# ==========================================
def login_view(request):
    if request.session.get("uid"):
        return redirect("note-list")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            email_to_login = None
            if "@" in login_input:
                email_to_login = login_input
            else:
                try:
                    docs = (
                        db.collection("users")
                        .where(filter=FieldFilter("username", "==", login_input))
                        .stream()
                    )
                    for doc in docs:
                        email_to_login = doc.to_dict().get("email")
                        break
                except Exception as e:
                    print(f"Lỗi tìm user: {e}")

            if not email_to_login:
                messages.error(request, "Tên đăng nhập hoặc Email không tồn tại!")
                return render(request, "users/login.html", {"form": form})

            rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
            payload = {
                "email": email_to_login,
                "password": password,
                "returnSecureToken": True,
            }

            try:
                r = requests.post(rest_api_url, json=payload)
                data = r.json()

                if r.status_code == 200:
                    uid = data["localId"]
                    request.session["uid"] = uid
                    request.session["id_token"] = data["idToken"]
                    request.session["user_email"] = email_to_login

                    messages.success(request, "Đăng nhập thành công!")

                    if form.cleaned_data.get("remember_me"):
                        request.session.set_expiry(1209600)
                    else:
                        request.session.set_expiry(0)
                    try:
                        user_ref = db.collection("users").document(uid)
                        user_doc = user_ref.get()

                        if user_doc.exists:
                            user_info = user_doc.to_dict()
                            if user_info.get("is_new_user", False):
                                user_ref.update({"is_new_user": False})
                                return redirect("profile")
                    except Exception as e:
                        print(f"Lỗi kiểm tra user mới: {e}")

                    return redirect("note-list")

                else:
                    error_msg = data.get("error", {}).get("message", "")
                    error_map = {
                        "INVALID_PASSWORD": "Sai mật khẩu!",
                        "EMAIL_NOT_FOUND": "Email không tồn tại!",
                        "USER_DISABLED": "Tài khoản đã bị vô hiệu hóa.",
                        "MISSING_PASSWORD": "Vui lòng nhập mật khẩu.",
                    }
                    messages.error(
                        request, error_map.get(error_msg, f"Lỗi đăng nhập: {error_msg}")
                    )

            except Exception as e:
                messages.error(request, f"Lỗi kết nối: {str(e)}")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


# ==========================================
# 3. ĐĂNG XUẤT
# ==========================================
def logout_view(request):
    request.session.flush()
    messages.info(request, "Đã đăng xuất.")
    return redirect("login")


# ==========================================
# 4. HỒ SƠ (PROFILE)
# ==========================================
def profile(request):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    user_data = user_doc.to_dict() if user_doc.exists else {}

    if not user_data.get("email"):
        try:
            user_data["email"] = auth.get_user(uid).email
        except:
            pass

    if request.method == "POST":
        form = UpdateProfileForm(request.POST, request.FILES)
        if form.is_valid():
            update_data = {}
            if form.cleaned_data.get("username"):
                new_name = form.cleaned_data.get("username")
                update_data["username"] = new_name
                try:
                    auth.update_user(uid, display_name=new_name)
                except:
                    pass

            if form.cleaned_data.get("gender"):
                update_data["gender"] = form.cleaned_data.get("gender")
            if form.cleaned_data.get("dob"):
                update_data["dob"] = str(form.cleaned_data.get("dob"))

            image_file = request.FILES.get("image")
            if image_file:
                try:
                    bucket = storage.bucket()
                    # Lưu vào folder profile_pics
                    blob = bucket.blob(f"profile_pics/{uid}_{image_file.name}")
                    blob.upload_from_file(
                        image_file, content_type=image_file.content_type
                    )
                    blob.make_public() # Bắt buộc để tạo public link
                    
                    # Sửa lỗi cache: Thêm timestamp vào URL để trình duyệt tải ảnh mới ngay lập tức
                    import time
                    update_data["avatar_url"] = f"{blob.public_url}?t={int(time.time())}"
                    
                    try:
                        auth.update_user(uid, photo_url=update_data["avatar_url"])
                    except:
                        pass
                except Exception as e:
                    messages.error(request, f"Lỗi ảnh: {e}")

            if update_data:
                user_ref.set(update_data, merge=True)
                messages.success(request, "Cập nhật thông tin thành công!")
                
            # Reload lại trang để thấy thay đổi
            return redirect("profile")
    else:
        form = UpdateProfileForm(initial=user_data)

    username = user_data.get("username") or user_data.get("email", "User")
    
    # Logic xử lý avatar hiển thị
    avatar_url = user_data.get("avatar_url")
    if not avatar_url:
        safe_username = urllib.parse.quote(username)
        avatar_url = f"https://ui-avatars.com/api/?name={safe_username}&background=random&color=fff&size=256"
    
    user_data["avatar_url"] = avatar_url

    return render(
        request,
        "users/profile.html",
        {
            "form": form,
            "user_data": user_data,
            "username": username,
            "avatar_url": avatar_url,
        },
    )

# ==========================================
# 5. CÁC HÀM BẢO MẬT
# ==========================================


def verify_security(request, action_type):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    username, avatar_url = _get_user_display_info(uid)

    if request.method == "POST":
        form = VerifyPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            try:
                user_email = None
                try:
                    user_doc = db.collection("users").document(uid).get()
                    if user_doc.exists:
                        user_email = user_doc.to_dict().get("email")
                except:
                    pass

                if not user_email:
                    user_email = auth.get_user(uid).email

                api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
                r = requests.post(
                    api_url,
                    json={
                        "email": user_email,
                        "password": password,
                        "returnSecureToken": True,
                    },
                )

                if r.status_code == 200:
                    request.session[f"can_change_{action_type}"] = True
                    return redirect(f"change_{action_type}")
                else:
                    form.add_error("password", "Mật khẩu không đúng.")
            except Exception as e:
                messages.error(request, "Lỗi hệ thống khi xác thực.")
                print(e)
    else:
        form = VerifyPasswordForm()

    titles = {
        "email": "Đổi Email",
        "phone": "Đổi Số điện thoại",
        "password": "Đổi Mật khẩu",
    }
    return render(
        request,
        "users/verify_security.html",
        {
            "form": form,
            "page_title": titles.get(action_type, "Xác thực"),
            "username": username,
            "avatar_url": avatar_url,
        },
    )


# ==========================================
# 6. ĐỔI EMAIL
# ==========================================


def change_email_view(request):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    if not request.session.get("can_change_email"):
        return redirect("verify_security", action_type="email")

    username, avatar_url = _get_user_display_info(uid)

    if request.method == "POST":
        form = ChangeEmailForm(request.POST, current_uid=uid)
        if form.is_valid():
            new_email = form.cleaned_data.get("new_email")
            try:
                auth.update_user(uid, email=new_email)
                db.collection("users").document(uid).update({"email": new_email})
                del request.session["can_change_email"]
                messages.success(request, "Đổi Email thành công!")
                return redirect("profile")
            except Exception as e:
                messages.error(request, f"Lỗi: {e}")
    else:
        form = ChangeEmailForm(current_uid=uid)

    return render(
        request,
        "users/change_info.html",
        {
            "form": form,
            "title": "Đổi Email mới",
            "btn_text": "Lưu Email",
            "username": username,  # Truyền vào template
            "avatar_url": avatar_url,  # Truyền vào template
        },
    )


# ==========================================
# 7. ĐỔI SỐ ĐIỆN THOẠI
# ==========================================


def change_phone_view(request):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    if not request.session.get("can_change_phone"):
        return redirect("verify_security", action_type="phone")

    # [FIX] Lấy info hiển thị
    username, avatar_url = _get_user_display_info(uid)

    if request.method == "POST":
        form = ChangePhoneForm(request.POST, current_uid=uid)
        if form.is_valid():
            new_phone = form.cleaned_data.get("new_phone")
            try:
                db.collection("users").document(uid).set(
                    {"phone": new_phone}, merge=True
                )
                del request.session["can_change_phone"]
                messages.success(request, "Đổi Số điện thoại thành công!")
                return redirect("profile")
            except Exception as e:
                messages.error(request, f"Lỗi: {e}")
    else:
        form = ChangePhoneForm(current_uid=uid)

    return render(
        request,
        "users/change_info.html",
        {
            "form": form,
            "title": "Đổi Số điện thoại",
            "btn_text": "Lưu Số điện thoại",
            "username": username,  # Truyền vào template
            "avatar_url": avatar_url,  # Truyền vào template
        },
    )


# ==========================================
# 8.ĐỔI MẬT KHẨU
# ==========================================


def change_password_view(request):
    uid = request.session.get("uid")
    if not uid:
        return redirect("login")

    if not request.session.get("can_change_password"):
        return redirect("verify_security", action_type="password")

    username, avatar_url = _get_user_display_info(uid)

    if request.method == "POST":
        form = ChangePasswordFinalForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data.get("new_password")
            try:
                auth.update_user(uid, password=new_pass)
                del request.session["can_change_password"]
                messages.success(request, "Đổi mật khẩu thành công!")
                return redirect("profile")
            except Exception as e:
                messages.error(request, f"Lỗi: {e}")
    else:
        form = ChangePasswordFinalForm()

    return render(
        request,
        "users/change_password_final.html",
        {"form": form, "username": username, "avatar_url": avatar_url},
    )


# ==========================================
# 9. QUÊN MẬT KHẨU
# ==========================================
def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
            try:
                r = requests.post(
                    endpoint, json={"requestType": "PASSWORD_RESET", "email": email}
                )
                if r.status_code == 200:
                    messages.success(request, "Email đặt lại mật khẩu đã gửi!")
                    return redirect("login")
                else:
                    messages.error(request, "Email không tồn tại.")
            except Exception as e:
                messages.error(request, f"Lỗi: {str(e)}")
    else:
        form = ForgotPasswordForm()
    return render(request, "users/forgot_password.html", {"form": form})


# ==========================================
# 10. XÁC NHẬN ĐỔI MẬT KHẨU
# ==========================================
def reset_password_confirm(request):
    oob_code = request.GET.get("oobCode")
    if not oob_code and request.method == "GET":
        return redirect("login")

    if request.method == "POST":
        form = ResetPasswordConfirmForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data.get("new_password")
            code = request.POST.get("oob_code_hidden")
            endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={FIREBASE_WEB_API_KEY}"

            try:
                r = requests.post(
                    endpoint, json={"oobCode": code, "newPassword": new_pass}
                )
                if r.status_code == 200:
                    messages.success(request, "Đổi mật khẩu thành công!")
                    return redirect("login")
                else:
                    messages.error(request, "Link lỗi hoặc hết hạn.")
            except Exception as e:
                messages.error(request, f"Lỗi: {str(e)}")
    else:
        form = ResetPasswordConfirmForm()
    return render(
        request,
        "users/reset_password_confirm.html",
        {"form": form, "oob_code": oob_code},
    )
