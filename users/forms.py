from django import forms
import re
from firebase_admin import auth


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Tên hiển thị"}
        ),
        label="Tên hiển thị",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mật khẩu"}
        ),
        label="Mật khẩu",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nhập lại mật khẩu"}
        ),
        label="Nhập lại mật khẩu",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            try:
                auth.get_user_by_email(email)
                raise forms.ValidationError(
                    "Email này đã được sử dụng bởi tài khoản khác."
                )
            except auth.UserNotFoundError:
                pass
            except Exception:
                pass
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Mật khẩu nhập lại không khớp.")


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Tên đăng nhập / Email",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nhập username hoặc email"}
        ),
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nhập mật khẩu"}
        ),
    )
    remember_me = forms.BooleanField(
        label="Ghi nhớ đăng nhập",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class UpdateProfileForm(forms.Form):
    username = forms.CharField(
        required=False,
        label="Tên hiển thị",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    gender = forms.ChoiceField(
        choices=[("Nam", "Nam"), ("Nữ", "Nữ"), ("Khác", "Khác")],
        required=False,
        label="Giới tính",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    dob = forms.DateField(
        required=False,
        label="Ngày sinh",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    image = forms.ImageField(
        required=False,
        label="Ảnh đại diện",
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )


class VerifyPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nhập mật khẩu hiện tại"}
        ),
        label="Mật khẩu xác nhận",
    )


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email mới"}
        ),
        label="Email mới",
    )

    def __init__(self, *args, **kwargs):
        self.current_uid = kwargs.pop("current_uid", None)
        super().__init__(*args, **kwargs)

    def clean_new_email(self):
        email = self.cleaned_data.get("new_email")
        if email:
            try:
                user = auth.get_user_by_email(email)
                if user.uid != self.current_uid:
                    raise forms.ValidationError("Email này đã được sử dụng.")
            except auth.UserNotFoundError:
                pass
        return email


class ChangePhoneForm(forms.Form):
    new_phone = forms.CharField(
        label="Số điện thoại mới",
        max_length=15,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ví dụ: 0912345678"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.current_uid = kwargs.pop("current_uid", None)
        super().__init__(*args, **kwargs)

    def clean_new_phone(self):
        phone = self.cleaned_data.get("new_phone")
        pattern = re.compile(r"^(?:\+84|0)(?:\d){9,10}$")

        if not pattern.match(phone):
            raise forms.ValidationError(
                "Số điện thoại không hợp lệ (Phải bắt đầu bằng 0 hoặc +84 và gồm 10-11 số)."
            )

        return phone


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Nhập email đã đăng ký"}
        ),
        label="Email",
        required=True,
    )


class ResetPasswordConfirmForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mật khẩu mới"}
        ),
        label="Mật khẩu mới",
        min_length=6,
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nhập lại mật khẩu mới"}
        ),
        label="Nhập lại mật khẩu mới",
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get("new_password")
        confirm_pass = cleaned_data.get("confirm_new_password")
        if new_pass and confirm_pass and new_pass != confirm_pass:
            self.add_error("confirm_new_password", "Mật khẩu không khớp.")


class ChangePasswordFinalForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Mật khẩu mới"}
        ),
        label="Mật khẩu mới",
        min_length=6,
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Nhập lại mật khẩu"}
        ),
        label="Nhập lại mật khẩu",
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get("new_password")
        confirm_pass = cleaned_data.get("confirm_new_password")
        if new_pass and confirm_pass and new_pass != confirm_pass:
            self.add_error("confirm_new_password", "Mật khẩu không khớp.")
