from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path(
        "security/verify/<str:action_type>/",
        views.verify_security,
        name="verify_security",
    ),
    path("security/change-email/", views.change_email_view, name="change_email"),
    path("security/change-phone/", views.change_phone_view, name="change_phone"),
    path(
        "security/change-password/", views.change_password_view, name="change_password"
    ),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path(
        "reset-password-confirm/",
        views.reset_password_confirm,
        name="reset_password_confirm",
    ),
]
