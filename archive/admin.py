from django.contrib import admin
from .models import Match, Moment, Review, ReviewLike


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("home_team", "away_team", "competition", "kickoff_at", "featured")
    list_filter = ("competition", "featured")
    search_fields = ("home_team", "away_team", "competition")
    list_editable = ("featured",)


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
