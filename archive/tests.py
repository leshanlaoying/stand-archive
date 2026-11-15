from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Match, Player, PlayerRating, Review


class PlayerRatingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fan", password="strong-password-123")
        self.other = User.objects.create_user(username="other", password="strong-password-123")
        self.admin = User.objects.create_superuser(username="owner", password="strong-password-123")
        self.match = Match.objects.create(home_team="主队", away_team="客队", home_score=2, away_score=1)
        self.player = Player.objects.create(match=self.match, name="前锋", note="梅开二度")
        self.url = reverse("save_player_rating", args=[self.match.pk, self.player.pk])

    def test_admin_can_publish_match_with_multiple_players(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:archive_match_add"), {
            "home_team": "蓝队", "away_team": "红队", "home_score": 3, "away_score": 2,
            "players-TOTAL_FORMS": "3", "players-INITIAL_FORMS": "0",
            "players-MIN_NUM_FORMS": "0", "players-MAX_NUM_FORMS": "1000",
            "players-0-name": "甲", "players-0-note": "制胜球",
            "players-1-name": "乙", "players-1-note": "",
            "players-2-name": "", "players-2-note": "",
            "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        match = Match.objects.get(home_team="蓝队")
        self.assertEqual(match.players.count(), 2)
        self.assertEqual(match.players.get(name="甲").note, "制胜球")
        self.assertContains(self.client.get(match.get_absolute_url()), "制胜球")

    def test_login_and_valid_range_required(self):
        self.assertEqual(self.client.post(self.url, {"score": 8}).status_code, 302)
        self.assertEqual(PlayerRating.objects.count(), 0)
        self.client.force_login(self.user)
        self.client.post(self.url, {"score": 0, "comment": "太低"})
        self.client.post(self.url, {"score": 11, "comment": "太高"})
        self.assertEqual(PlayerRating.objects.count(), 0)
        self.client.post(self.url, {"score": 8, "comment": "跑动很积极"})
        self.assertEqual(PlayerRating.objects.get().score, 8)

    def test_users_see_each_others_ratings_and_can_update_their_own(self):
        self.client.force_login(self.user)
        self.client.post(self.url, {"score": 7, "comment": "第一印象"})
        self.client.force_login(self.other)
        self.client.post(self.url, {"score": 9, "comment": "我觉得更好"})
        response = self.client.get(self.match.get_absolute_url())
        self.assertContains(response, "第一印象")
        self.assertContains(response, "我觉得更好")
        self.assertContains(response, "8.0")
        self.client.force_login(self.user)
        self.client.post(self.url, {"score": 10, "comment": "看完回放改分"})
        self.assertEqual(PlayerRating.objects.count(), 2)
        self.assertEqual(PlayerRating.objects.get(author=self.user).score, 10)
        self.assertEqual(PlayerRating.objects.get(author=self.other).score, 9)
        self.assertContains(self.client.get(reverse("my_page")), "看完回放改分")

    def test_rating_cannot_be_posted_to_another_match(self):
        other_match = Match.objects.create(home_team="另一队", away_team="对手", home_score=0, away_score=0)
        self.client.force_login(self.user)
        response = self.client.post(reverse("save_player_rating", args=[other_match.pk, self.player.pk]), {"score": 8})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(PlayerRating.objects.count(), 0)

    def test_old_review_data_survives_without_old_public_sections(self):
        Review.objects.create(match=self.match, author=self.user, rating=8, headline="旧复盘", body="旧内容")
        response = self.client.get(self.match.get_absolute_url())
        self.assertNotContains(response, "旧复盘")
        self.assertNotContains(response, "我们的比赛时间线")
        self.assertEqual(Review.objects.count(), 1)

    def test_admin_bootstrap_does_not_reset_existing_password(self):
        with patch.dict("os.environ", {"INITIAL_ADMIN_USERNAME": "bootstrap", "INITIAL_ADMIN_PASSWORD": "first-secret"}):
            call_command("bootstrap_admin", verbosity=0)
        with patch.dict("os.environ", {"INITIAL_ADMIN_USERNAME": "bootstrap", "INITIAL_ADMIN_PASSWORD": "second-secret"}):
            call_command("bootstrap_admin", verbosity=0)
        owner = User.objects.get(username="bootstrap")
        self.assertTrue(owner.check_password("first-secret"))
        self.assertFalse(owner.check_password("second-secret"))
