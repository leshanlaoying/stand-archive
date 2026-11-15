from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Match, Moment, Review, ReviewLike


class ArchiveFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fan", password="strong-password-123")
        self.other = User.objects.create_user(username="other", password="strong-password-123")
        self.match = Match.objects.create(
            competition="测试联赛", home_team="主队", away_team="客队",
            kickoff_at=timezone.now() - timedelta(days=1), home_score=2, away_score=1,
        )

    def test_public_browse_and_login_required_for_posting(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertContains(self.client.get(self.match.get_absolute_url()), "测试联赛")
        response = self.client.post(reverse("save_review", args=[self.match.pk]), {"rating": 9, "headline": "好比赛", "body": "精彩"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_review_update_preserves_single_record_and_other_users_data(self):
        self.client.force_login(self.user)
        url = reverse("save_review", args=[self.match.pk])
        self.client.post(url, {"rating": 8, "headline": "第一版", "body": "很精彩"})
        self.client.force_login(self.other)
        self.client.post(url, {"rating": 7, "headline": "另一位球迷", "body": "我的看法"})
        self.client.force_login(self.user)
        self.client.post(url, {"rating": 9, "headline": "修改后的复盘", "body": "新的看法"})
        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(Review.objects.get(author=self.user).rating, 9)
        self.assertEqual(Review.objects.get(author=self.other).headline, "另一位球迷")

    def test_moment_and_like_flow(self):
        review = Review.objects.create(match=self.match, author=self.other, rating=8, headline="复盘", body="正文")
        self.client.force_login(self.user)
        self.client.post(reverse("add_moment", args=[self.match.pk]), {"minute": 63, "kind": "goal", "title": "逆转进球", "body": "全场沸腾"})
        self.assertEqual(Moment.objects.get(match=self.match).minute, 63)
        url = reverse("toggle_like", args=[review.pk])
        self.client.post(url)
        self.assertEqual(ReviewLike.objects.count(), 1)
        self.client.post(url)
        self.assertEqual(ReviewLike.objects.count(), 0)

    def test_admin_bootstrap_does_not_reset_existing_password(self):
        with patch.dict("os.environ", {"INITIAL_ADMIN_USERNAME": "owner", "INITIAL_ADMIN_PASSWORD": "first-secret"}):
            call_command("bootstrap_admin", verbosity=0)
        owner = User.objects.get(username="owner")
        self.assertTrue(owner.is_superuser)
        with patch.dict("os.environ", {"INITIAL_ADMIN_USERNAME": "owner", "INITIAL_ADMIN_PASSWORD": "second-secret"}):
            call_command("bootstrap_admin", verbosity=0)
        owner.refresh_from_db()
        self.assertTrue(owner.check_password("first-secret"))
        self.assertFalse(owner.check_password("second-secret"))
