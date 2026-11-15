from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Match(models.Model):
    competition = models.CharField("赛事", max_length=100, blank=True, default="球迷档案")
    season = models.CharField("赛季", max_length=30, blank=True)
    home_team = models.CharField("主队", max_length=80)
    away_team = models.CharField("客队", max_length=80)
    kickoff_at = models.DateTimeField("开赛时间", blank=True, default=timezone.now)
    home_score = models.PositiveSmallIntegerField("主队进球", null=True, blank=True)
    away_score = models.PositiveSmallIntegerField("客队进球", null=True, blank=True)
    summary = models.TextField("赛前导语或赛后概述", blank=True)
    cover_color = models.CharField("主题色", max_length=7, default="#d8fb49", help_text="例如 #d8fb49")
    featured = models.BooleanField("首页精选", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-kickoff_at", "-id"]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} · {self.competition}"

    def get_absolute_url(self):
        return reverse("match_detail", args=[self.pk])

    @property
    def has_score(self):
        return self.home_score is not None and self.away_score is not None


class Review(models.Model):
    match = models.ForeignKey(Match, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="football_reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField("比赛评分", validators=[MinValueValidator(1), MaxValueValidator(10)])
    headline = models.CharField("一句话复盘", max_length=120)
    body = models.TextField("我的复盘", max_length=3000)
    player_of_match = models.CharField("本场最佳球员", max_length=80, blank=True)
    turning_point = models.CharField("转折点", max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [models.UniqueConstraint(fields=["match", "author"], name="one_review_per_match_per_user")]

    def __str__(self):
        return f"{self.author} · {self.match}"


class Moment(models.Model):
    KIND_CHOICES = [
        ("goal", "进球"), ("tactic", "战术"), ("turn", "转折"),
        ("controversy", "争议"), ("memory", "名场面"),
    ]
    match = models.ForeignKey(Match, related_name="moments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    minute = models.PositiveSmallIntegerField("比赛分钟", validators=[MaxValueValidator(130)])
    kind = models.CharField("类型", max_length=20, choices=KIND_CHOICES, default="memory")
    title = models.CharField("标题", max_length=100)
    body = models.TextField("补充说明", max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["minute", "created_at"]

    def __str__(self):
        return f"{self.minute}′ {self.title}"


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["review", "user"], name="one_like_per_review_per_user")]


class Player(models.Model):
    match = models.ForeignKey(Match, related_name="players", on_delete=models.CASCADE)
    name = models.CharField("球员姓名", max_length=80)
    note = models.CharField("一句话介绍", max_length=180, blank=True)
    sort_order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.name} · {self.match.home_team} vs {self.match.away_team}"


class PlayerRating(models.Model):
    player = models.ForeignKey(Player, related_name="ratings", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="player_ratings", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField("评分", validators=[MinValueValidator(1), MaxValueValidator(10)])
    comment = models.TextField("留言", max_length=600, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["player", "author"], name="one_rating_per_player_per_user"),
            models.CheckConstraint(condition=models.Q(score__gte=1, score__lte=10), name="player_rating_score_1_to_10"),
        ]

    def __str__(self):
        return f"{self.author} 给 {self.player.name} {self.score} 分"
