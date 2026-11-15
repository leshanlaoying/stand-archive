from datetime import datetime, timezone
from django.db import migrations


def add_classics(apps, schema_editor):
    Match = apps.get_model("archive", "Match")
    classics = [
        dict(competition="世界杯", season="2022", home_team="阿根廷", away_team="法国",
             kickoff_at=datetime(2022, 12, 18, 15, 0, tzinfo=timezone.utc), home_score=3, away_score=3,
             summary="一场在加时赛后战成 3:3、最终由阿根廷在点球大战中夺冠的世界杯决赛。哪一个瞬间最让你难忘？",
             cover_color="#d8fb49", featured=True),
        dict(competition="欧冠", season="2004/05", home_team="AC米兰", away_team="利物浦",
             kickoff_at=datetime(2005, 5, 25, 18, 45, tzinfo=timezone.utc), home_score=3, away_score=3,
             summary="伊斯坦布尔之夜：利物浦从半场落后三球到点球大战获胜。那段逆转，你会怎样复盘？",
             cover_color="#ff8c71", featured=False),
        dict(competition="世界杯", season="2014", home_team="巴西", away_team="德国",
             kickoff_at=datetime(2014, 7, 8, 20, 0, tzinfo=timezone.utc), home_score=1, away_score=7,
             summary="2014 年世界杯半决赛，一场令人难以置信的 1:7。战术、心理与比赛节奏，你认为决定性的因素是什么？",
             cover_color="#f6d363", featured=False),
    ]
    for item in classics:
        identity = {key: item[key] for key in ("competition", "season", "home_team", "away_team", "kickoff_at")}
        defaults = {key: value for key, value in item.items() if key not in identity}
        Match.objects.get_or_create(**identity, defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [("archive", "0001_initial")]
    operations = [migrations.RunPython(add_classics, migrations.RunPython.noop)]
