# # config/settings.py

# import os
# import sys
# from pathlib import Path
# import environ
# from .firebase_setup import initialize_firebase

# env = environ.Env()
# BASE_DIR = Path(__file__).resolve().parent.parent
# env_file = os.path.join(BASE_DIR, ".env")
# if os.path.exists(env_file):
#     environ.Env.read_env(env_file)

# if "runserver" not in sys.argv or os.environ.get("RUN_MAIN") == "true":
#     try:
#         FIREBASE_APP = initialize_firebase(BASE_DIR)
#     except Exception as e:
#         print(f"WARNING: Firebase chưa khởi tạo được: {e}")

# # === 1. Cấu hình Cơ bản ===
# SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")
# DEBUG = env.bool("DEBUG", default=False)

# if DEBUG:
#     ALLOWED_HOSTS = ["*"]
# else:
#     environ_hosts = os.environ.get("ALLOWED_HOSTS", "")
#     ALLOWED_HOSTS = [host.strip() for host in environ_hosts.split(",") if host.strip()]

# # Xử lý CSRF_TRUSTED_ORIGINS (Luôn chạy để nhận diện domain từ env)
# environ_csrf = os.environ.get("CSRF_TRUSTED_ORIGINS", "")

# if environ_csrf:
#     CSRF_TRUSTED_ORIGINS = [
#         origin.strip() for origin in environ_csrf.split(",") if origin.strip()
#     ]
# else:
#     CSRF_TRUSTED_ORIGINS = []

# # In ra log để kiểm tra khi deploy (xem trong Cloud Run Logs)
# print(f"=== DEBUG CSRF CONFIG ===")
# print(f"CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
# print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
# print(f"=========================")


# # ----------------------------------------------------

# # === 2. Application definition ===
# INSTALLED_APPS = [
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "users",
#     "notes",
# ]

# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "whitenoise.middleware.WhiteNoiseMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "config.urls"

# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.request",
#                 "django.contrib.messages.context_processors.messages",
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = "config.wsgi.application"

# # === 3. Database ===
# DATABASES = {}

# # === 5. Internationalization ===
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "UTC"
# USE_I18N = True
# USE_TZ = True

# # === 6. Static & Media Files ===
# STATIC_URL = "static/"
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]

# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# MEDIA_URL = "/media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # === 7. Auth Redirects ===
# LOGIN_URL = "login"
# LOGIN_REDIRECT_URL = "note-list"
# LOGOUT_REDIRECT_URL = "login"

# # === 8. Security & CSRF ===

# CSRF_TRUSTED_ORIGINS = [
#     "https://keepx-project.web.app",
#     "https://keepx-project.firebaseapp.com",
#     "https://keepx-backend-kgwtqjq3zq-as.a.run.app",
# ]

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
# USE_X_FORWARDED_HOST = False
# USE_X_FORWARDED_PORT = True
# CSRF_COOKIE_DOMAIN = None
# SESSION_COOKIE_AGE = 60 * 60 * 24 * 7
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_SAMESITE = 'None'

# # Lấy API Key từ biến môi trường
# FIREBASE_WEB_API_KEY = env("FIREBASE_WEB_API_KEY", default="API_KEY_NOT_SET")

# config/settings.py

import os
import sys
from pathlib import Path
import environ
from .firebase_setup import initialize_firebase

# --- Cấu hình môi trường ---
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# --- Khởi tạo Firebase ---
if "runserver" not in sys.argv or os.environ.get("RUN_MAIN") == "true":
    try:
        FIREBASE_APP = initialize_firebase(BASE_DIR)
    except Exception as e:
        print(f"WARNING: Firebase chưa khởi tạo được: {e}")

# === 1. Cấu hình Cơ bản ===
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = env.bool("DEBUG", default=True)

# Cho phép tất cả Host (Cloud Run đã lo bảo mật lớp ngoài)
ALLOWED_HOSTS = ["*"]

# === 2. Application definition ===
INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "notes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# === 3. Database ===
DATABASES = {}

# === 4. Quốc tế hóa ===
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# === 5. Static Files ===
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === 6. Auth Redirects ===
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "note-list"
LOGOUT_REDIRECT_URL = "login"

# === 7. Security & CSRF (Cấu hình FIX RIÊNG CHO FIREBASE HOSTING) ===

CSRF_TRUSTED_ORIGINS = [
    "https://keepx-project.web.app",
    "https://keepx-project.firebaseapp.com",
    "https://keepx-backend-kgwtqjq3zq-as.a.run.app",
]

# [QUAN TRỌNG NHẤT] Đổi tên cookie session thành __session để Firebase không xóa
SESSION_COOKIE_NAME = '__session'

# [QUAN TRỌNG NHÌ] Lưu CSRF Token vào Session luôn (vì Firebase chỉ cho 1 cookie __session tồn tại)
CSRF_USE_SESSIONS = True

# Cấu hình Session Engine
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Cấu hình bảo mật Cookie
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 tuần
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Cấu hình Proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
SECURE_SSL_REDIRECT = False

# Lấy API Key
FIREBASE_WEB_API_KEY = env("FIREBASE_WEB_API_KEY", default="API_KEY_NOT_SET")

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"