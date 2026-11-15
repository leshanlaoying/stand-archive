from django.contrib import admin
from django import forms
from .models import Match, Moment, Player, PlayerRating, Review, ReviewLike


class PlayerInline(admin.TabularInline):
    model = Player
    fields = ("name", "note")
    extra = 3
    verbose_name = "球员"
    verbose_name_plural = "球员（可继续添加）"


class MatchAdminForm(forms.ModelForm):
    home_score = forms.IntegerField(label="主队进球", min_value=0)
    away_score = forms.IntegerField(label="客队进球", min_value=0)

    class Meta:
        model = Match
        fields = ("home_team", "away_team", "home_score", "away_score")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    form = MatchAdminForm
    fields = ("home_team", "away_team", "home_score", "away_score")
    inlines = (PlayerInline,)
    list_display = ("home_team", "away_team", "score", "player_count", "created_at")
    search_fields = ("home_team", "away_team")

    @admin.display(description="比分")
    def score(self, obj):
        return f"{obj.home_score} : {obj.away_score}" if obj.has_score else "未填写"

    @admin.display(description="球员数")
    def player_count(self, obj):
        return obj.players.count()


@admin.register(PlayerRating)
class PlayerRatingAdmin(admin.ModelAdmin):
    list_display = ("player", "author", "score", "updated_at")
    search_fields = ("player__name", "author__username", "comment")
    list_filter = ("score",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "match", "rating", "headline", "updated_at")
    list_filter = ("rating", "match__competition")
    search_fields = ("headline", "body", "author__username")


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ("match", "minute", "kind", "title", "author")
    list_filter = ("kind", "match__competition")
    search_fields = ("title", "body")


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "created_at")
