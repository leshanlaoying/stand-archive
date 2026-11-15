from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PlayerRatingForm, RegisterForm
from .models import Match, Player, PlayerRating


def home(request):
    matches = Match.objects.annotate(
        player_count=Count("players", distinct=True),
        rating_count=Count("players__ratings", distinct=True),
    )
    query = request.GET.get("q", "").strip()[:100]
    if query:
        matches = matches.filter(Q(home_team__icontains=query) | Q(away_team__icontains=query))
    featured = Match.objects.first()
    return render(request, "archive/home.html", {
        "matches": matches[:30], "featured": featured, "query": query,
        "total_matches": Match.objects.count(),
        "total_players": Player.objects.count(),
        "total_ratings": PlayerRating.objects.count(),
    })


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    ratings = PlayerRating.objects.select_related("author").order_by("-updated_at", "-id")
    players = list(match.players.annotate(
        average_score=Avg("ratings__score"), rating_count=Count("ratings"),
    ).prefetch_related(Prefetch("ratings", queryset=ratings)))
    for player in players:
        player.my_rating = next(
            (rating for rating in player.ratings.all() if rating.author_id == request.user.pk), None
        ) if request.user.is_authenticated else None
        player.rating_form = PlayerRatingForm(instance=player.my_rating)
    return render(request, "archive/match_detail.html", {
        "match": match, "players": players,
        "total_ratings": sum(player.rating_count for player in players),
    })


@login_required
@require_POST
def save_player_rating(request, pk, player_pk):
    player = get_object_or_404(Player, pk=player_pk, match_id=pk)
    form = PlayerRatingForm(request.POST)
    if form.is_valid():
        PlayerRating.objects.update_or_create(
            player=player, author=request.user,
            defaults={"score": form.cleaned_data["score"], "comment": form.cleaned_data["comment"]},
        )
        messages.success(request, f"已保存你给 {player.name} 的评分。")
    else:
        messages.error(request, "评分未保存。请选 1–10 分，留言不超过 600 字。")
    return redirect(f"{player.match.get_absolute_url()}#player-{player.pk}")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "欢迎加入档案馆！")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


@login_required
def my_page(request):
    ratings = PlayerRating.objects.filter(author=request.user).select_related("player__match")
    return render(request, "archive/my_page.html", {"ratings": ratings})
