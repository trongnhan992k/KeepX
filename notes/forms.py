# notes/forms.py
from django import forms

COLOR_CHOICES = [
    ("#ffffff", "Trắng"),
    ("#ffcccb", "Đỏ nhạt"),
    ("#90ee90", "Xanh lá"),
    ("#add8e6", "Xanh dương"),
]


class NoteForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        label="Tiêu đề",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Tiêu đề ghi chú..."}
        ),
    )
    content = forms.CharField(
        label="Nội dung",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Nội dung viết ở đây...",
            }
        ),
    )
    color = forms.ChoiceField(
        choices=COLOR_CHOICES,
        label="Màu nền",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    is_pinned = forms.BooleanField(
        required=False,
        label="Ghim lên đầu",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    is_archived = forms.BooleanField(
        required=False,
        label="Lưu trữ",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
