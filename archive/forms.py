from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import PlayerRating


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="邮箱", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "球迷昵称"}


class PlayerRatingForm(forms.ModelForm):
    class Meta:
        model = PlayerRating
        fields = ("score", "comment")
        widgets = {
            "score": forms.Select(choices=[("", "请选择分数")] + [(i, f"{i} 分") for i in range(1, 11)]),
            "comment": forms.Textarea(attrs={"rows": 3, "maxlength": 600, "placeholder": "说说这位球员的表现（可选）"}),
        }
