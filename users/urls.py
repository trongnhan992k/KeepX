from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("social-login/", views.social_login, name="social-login"), # Đường dẫn mới
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    
    # Bảo mật
    path("verify-security/<str:action_type>/", views.verify_security, name="verify_security"),
    path("change-email/", views.change_email_view, name="change_email"),
    path("change-phone/", views.change_phone_view, name="change_phone"),
    path("change-password/", views.change_password_view, name="change_password"),
    
    # Quên mật khẩu
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password-confirm/", views.reset_password_confirm, name="reset_password_confirm"),
]