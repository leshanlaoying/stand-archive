from django.core.management.base import BaseCommand

from archive.models import Match, Player


class Command(BaseCommand):
    help = "仅供独立预览环境使用：添加一场虚构示例比赛和球员。"

    def handle(self, *args, **options):
        match, _ = Match.objects.get_or_create(
            home_team="蓝队（示例）", away_team="红队（示例）",
            defaults={"home_score": 3, "away_score": 2},
        )
        for name, note in [
            ("前锋甲", "两次破门，持续冲击防线"),
            ("中场乙", "送出关键助攻"),
            ("门将丙", "终场前完成一次精彩扑救"),
        ]:
            Player.objects.get_or_create(match=match, name=name, defaults={"note": note})
        self.stdout.write(self.style.SUCCESS("预览示例比赛已就绪。"))
