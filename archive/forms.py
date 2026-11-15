from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Moment, Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="邮箱", required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "球迷昵称"}


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "headline", "body", "player_of_match", "turning_point")
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} 分") for i in range(1, 11)]),
            "headline": forms.TextInput(attrs={"placeholder": "一句话说出这场比赛留给你的印象"}),
            "body": forms.Textarea(attrs={"rows": 5, "placeholder": "战术、球员、情绪、争议……写下你想保存的观点"}),
            "player_of_match": forms.TextInput(attrs={"placeholder": "可选"}),
            "turning_point": forms.TextInput(attrs={"placeholder": "可选：哪一刻改变了比赛？"}),
        }


class MomentForm(forms.ModelForm):
    class Meta:
        model = Moment
        fields = ("minute", "kind", "title", "body")
        widgets = {
            "minute": forms.NumberInput(attrs={"min": 0, "max": 130, "placeholder": "分钟"}),
            "title": forms.TextInput(attrs={"placeholder": "这一刻发生了什么？"}),
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "补充你的看法（可选）"}),
        }
