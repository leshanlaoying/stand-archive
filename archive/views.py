from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import MomentForm, RegisterForm, ReviewForm
from .models import Match, Moment, Review, ReviewLike


def home(request):
    matches = Match.objects.annotate(review_count=Count("reviews", distinct=True), average_rating=Avg("reviews__rating"))
    query = request.GET.get("q", "").strip()[:100]
    competition = request.GET.get("competition", "").strip()[:100]
    if query:
        matches = matches.filter(Q(home_team__icontains=query) | Q(away_team__icontains=query) | Q(competition__icontains=query))
    if competition:
        matches = matches.filter(competition=competition)
    competitions = Match.objects.order_by("competition").values_list("competition", flat=True).distinct()
    featured = Match.objects.filter(featured=True).order_by("-kickoff_at").first() or Match.objects.first()
    return render(request, "archive/home.html", {
        "matches": matches[:30], "featured": featured, "competitions": competitions,
        "query": query, "selected_competition": competition,
        "total_matches": Match.objects.count(), "total_reviews": Review.objects.count(),
        "total_moments": Moment.objects.count(),
    })


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    reviews = match.reviews.select_related("author").annotate(like_count=Count("likes"))
    moments = match.moments.select_related("author")
    my_review = match.reviews.filter(author=request.user).first() if request.user.is_authenticated else None
    liked_ids = set(ReviewLike.objects.filter(user=request.user, review__match=match).values_list("review_id", flat=True)) if request.user.is_authenticated else set()
    average = reviews.aggregate(value=Avg("rating"))["value"]
    return render(request, "archive/match_detail.html", {
        "match": match, "reviews": reviews, "moments": moments,
        "my_review": my_review, "review_form": ReviewForm(instance=my_review),
        "moment_form": MomentForm(), "average": average, "liked_ids": liked_ids,
    })


@login_required
@require_POST
def save_review(request, pk):
    match = get_object_or_404(Match, pk=pk)
    existing = Review.objects.filter(match=match, author=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.match = match
        review.author = request.user
        review.save()
        messages.success(request, "你的复盘已保存。")
    else:
        messages.error(request, "复盘未保存，请检查评分和必填内容。")
    return redirect(match)


@login_required
@require_POST
def add_moment(request, pk):
    match = get_object_or_404(Match, pk=pk)
    form = MomentForm(request.POST)
    if form.is_valid():
        moment = form.save(commit=False)
        moment.match = match
        moment.author = request.user
        moment.save()
        messages.success(request, "关键时刻已加入时间线。")
    else:
        messages.error(request, "关键时刻未保存，请检查分钟和标题。")
    return redirect(match)


@login_required
@require_POST
def toggle_like(request, pk):
    review = get_object_or_404(Review, pk=pk)
    like, created = ReviewLike.objects.get_or_create(review=review, user=request.user)
    if not created:
        like.delete()
    return redirect(review.match)


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
    reviews = Review.objects.filter(author=request.user).select_related("match")
    moments = Moment.objects.filter(author=request.user).select_related("match").order_by("-created_at")[:12]
    return render(request, "archive/my_page.html", {"reviews": reviews, "moments": moments})
