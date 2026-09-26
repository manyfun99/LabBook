import datetime
import json
import unittest
from pathlib import Path

from labbook import db, metrics
from labbook.github import GitHubError, NotFound

FIX = Path(__file__).parent / "fixtures"
HISTORY = json.loads((FIX / "history_prism_insight.json").read_text())

SCOPE = {"famous_stars": 1000, "rising_d30": 300, "rising_ratio": 0.2, "rising_min_stars": 100, "kr_min_stars": 50}
CONFIG = {"topic": "t", "scope": SCOPE}


def week(start, days):
    ts = int(datetime.datetime.fromisoformat(start).replace(tzinfo=datetime.UTC).timestamp())
    return {"week": ts, "total": sum(days), "days": days}


class DailyTest(unittest.TestCase):
    def test_최신일부터_나열하고_오늘_이후는_뺀다(self):
        hist = [week("2026-09-20", [1, 2, 3, 4, 5, 6, 7]), week("2026-09-13", [10, 20, 30, 40, 50, 60, 70])]
        days = metrics.daily_counts(hist, datetime.date(2026, 9, 23))  # 수요일
        self.assertEqual(days[:6], [4, 3, 2, 1, 70, 60])
        self.assertEqual(len(days), 4 + 7)

    def test_토요일이면_이번주_7일을_모두_쓴다(self):
        days = metrics.daily_counts(HISTORY, datetime.date(2026, 9, 26))
        self.assertEqual(len(days), 30 * 7)
        self.assertEqual(sum(days), sum(w["total"] for w in HISTORY))

    def test_momentum은_7_30_90일_합(self):
        days = list(range(1, 101))
        self.assertEqual(metrics.momentum(days), (sum(range(1, 8)), sum(range(1, 31)), sum(range(1, 91))))

    def test_기록이_짧으면_있는_만큼만_더한다(self):
        self.assertEqual(metrics.momentum([5, 5]), (10, 10, 10))


class FlagTest(unittest.TestCase):
    def test_3일에_30일_증가분의_70퍼센트_이상이_몰리면_급등(self):
        days30 = [0] * 10 + [30, 30, 20] + [1] * 17
        self.assertIn("spike", metrics.flags({"stars": 1000, "watchers": 50, "forks": 100}, days30))

    def test_고르게_늘면_급등이_아니다(self):
        self.assertNotIn("spike", metrics.flags({"stars": 1000, "watchers": 50, "forks": 100}, [10] * 30))

    def test_30일_증가가_30_미만이면_급등을_보지_않는다(self):
        self.assertNotIn("spike", metrics.flags({"stars": 1000, "watchers": 50, "forks": 100}, [20, 5] + [0] * 28))

    def test_watchers와_forks_비율이_낮으면_표시한다(self):
        f = metrics.flags({"stars": 1000, "watchers": 14, "forks": 9}, [0] * 30)
        self.assertEqual(f, ["low_watchers", "low_forks"])

    def test_비율이_정상이면_플래그_없음(self):
        self.assertEqual(metrics.flags({"stars": 1000, "watchers": 15, "forks": 10}, [0] * 30), [])


class ScopeTest(unittest.TestCase):
    def snap(self, **kw):
        base = {"stars": 500, "d30": 0, "archived": 0}
        return base | kw

    def test_아카이브는_제외(self):
        self.assertEqual(metrics.scope(self.snap(stars=5000, archived=1), ["star"], SCOPE), ("exclude", "archived"))

    def test_사용자_스타는_항상_포함(self):
        self.assertEqual(metrics.scope(self.snap(stars=3), ["star"], SCOPE), ("include", "starred"))

    def test_유명(self):
        self.assertEqual(metrics.scope(self.snap(stars=1000), ["search:x"], SCOPE), ("include", "famous"))

    def test_라이징_절대량(self):
        self.assertEqual(metrics.scope(self.snap(stars=500, d30=300), ["search:x"], SCOPE), ("include", "rising"))

    def test_라이징_비율(self):
        self.assertEqual(metrics.scope(self.snap(stars=100, d30=20), ["search:x"], SCOPE), ("include", "rising"))

    def test_비율은_100스타_미만이면_보지_않는다(self):
        self.assertEqual(metrics.scope(self.snap(stars=99, d30=99), ["search:x"], SCOPE), ("exclude", "below_threshold"))

    def test_한국_출처는_50스타부터(self):
        self.assertEqual(metrics.scope(self.snap(stars=50), ["kr:pykrx"], SCOPE), ("include", "kr"))
        self.assertEqual(metrics.scope(self.snap(stars=49), ["kr:pykrx"], SCOPE), ("exclude", "below_threshold"))

    def test_기준_미달(self):
        self.assertEqual(metrics.scope(self.snap(stars=999, d30=10), ["search:x"], SCOPE), ("exclude", "below_threshold"))


class FakeGH:
    def __init__(self, repos, histories):
        self.repos, self.histories, self.calls = repos, histories, []

    def get(self, path):
        self.calls.append(path)
        parts = path.split("/")
        gh_id = int(parts[1])
        if path.endswith("/stargazers/history"):
            h = self.histories[gh_id]
            if isinstance(h, Exception):
                raise h
            return h
        if gh_id not in self.repos:
            raise NotFound(path)
        return self.repos[gh_id]


def raw_repo(gh_id, full_name, stars, watchers=100, forks=100, archived=False):
    return {"id": gh_id, "full_name": full_name, "html_url": f"https://github.com/{full_name}",
            "stargazers_count": stars, "subscribers_count": watchers, "forks_count": forks,
            "open_issues_count": 1, "pushed_at": "p", "created_at": "c", "archived": archived}


class RefreshTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)
        db.migrate(self.conn)
        for gh_id, key, sources in [(1, "github:a/b", ["search:x"]), (2, "github:c/d", ["search:x"])]:
            cur = self.conn.execute("INSERT INTO entity (kind, key, gh_id, first_seen_at) VALUES ('github_repo', ?, ?, 't')",
                                    (key, gh_id))
            self.conn.execute("INSERT INTO screening (topic, entity_id, stage, decision, sources, decided_at) "
                              "VALUES ('t', ?, 'identified', 'include', ?, 't')", (cur.lastrowid, json.dumps(sources)))
        self.conn.commit()
        self.today = datetime.date(2026, 9, 26)

    def scoped(self):
        return {r["key"]: (r["decision"], r["reason"]) for r in self.conn.execute(
            "SELECT e.key, s.decision, s.reason FROM screening s JOIN entity e ON e.id = s.entity_id WHERE s.stage = 'scoped'")}

    def test_스냅샷과_범위_컷을_기록한다(self):
        gh = FakeGH({1: raw_repo(1, "a/b", 5000), 2: raw_repo(2, "c/d", 200)}, {1: HISTORY, 2: HISTORY})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        snap = self.conn.execute("SELECT * FROM snapshot WHERE entity_id = 1").fetchone()
        self.assertEqual(snap["taken_at"], "2026-09-26")
        self.assertEqual(snap["stars"], 5000)
        days = metrics.daily_counts(HISTORY, self.today)
        self.assertEqual((snap["d7"], snap["d30"], snap["d90"]), metrics.momentum(days))
        self.assertEqual(self.scoped()["github:a/b"], ("include", "famous"))

    def test_같은_날_재실행하면_API를_부르지_않고_범위_컷만_다시_계산한다(self):
        gh = FakeGH({1: raw_repo(1, "a/b", 5000), 2: raw_repo(2, "c/d", 200)}, {1: HISTORY, 2: HISTORY})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        n = len(gh.calls)
        stricter = {"topic": "t", "scope": SCOPE | {"famous_stars": 10000}}
        metrics.refresh(self.conn, gh, stricter, self.today)
        self.assertEqual(len(gh.calls), n)
        self.assertEqual(self.scoped()["github:a/b"][0], "exclude")

    def test_제외였던_레포가_라이징에_들어오면_포함으로_바뀐다(self):
        quiet = [week("2026-09-20", [0] * 7)] * 30
        gh = FakeGH({1: raw_repo(1, "a/b", 500), 2: raw_repo(2, "c/d", 500)}, {1: quiet, 2: quiet})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        self.assertEqual(self.scoped()["github:a/b"], ("exclude", "below_threshold"))
        hot = [week("2026-09-27", [0, 0, 0, 0, 0, 0, 0]), week("2026-09-20", [0, 0, 0, 0, 0, 0, 150]),
               week("2026-09-13", [0, 0, 0, 0, 0, 0, 150])]
        gh.histories[1] = hot
        metrics.refresh(self.conn, gh, CONFIG, datetime.date(2026, 10, 3))
        self.assertEqual(self.scoped()["github:a/b"], ("include", "rising"))

    def test_404면_gone으로_제외한다(self):
        gh = FakeGH({2: raw_repo(2, "c/d", 5000)}, {2: HISTORY})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        self.assertEqual(self.scoped()["github:a/b"], ("exclude", "gone"))

    def test_이름이_바뀌었으면_key를_갱신한다(self):
        gh = FakeGH({1: raw_repo(1, "new/name", 5000), 2: raw_repo(2, "c/d", 200)}, {1: HISTORY, 2: HISTORY})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        self.assertIn("github:new/name", self.scoped())

    def test_gh_id로_조회한다(self):
        gh = FakeGH({1: raw_repo(1, "a/b", 5000), 2: raw_repo(2, "c/d", 200)}, {1: HISTORY, 2: HISTORY})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        self.assertIn("repositories/1", gh.calls)
        self.assertIn("repositories/1/stargazers/history", gh.calls)

    def test_history가_실패하면_이전_스냅샷과의_스타_차이로_대신한다(self):
        gh = FakeGH({1: raw_repo(1, "a/b", 500), 2: raw_repo(2, "c/d", 200)}, {1: HISTORY, 2: HISTORY})
        metrics.refresh(self.conn, gh, CONFIG, datetime.date(2026, 8, 20))   # 37일 전
        gh.repos[1] = raw_repo(1, "a/b", 520)
        metrics.refresh(self.conn, gh, CONFIG, datetime.date(2026, 9, 20))   # 6일 전
        gh.repos[1] = raw_repo(1, "a/b", 900)
        gh.histories[1] = GitHubError("history 제한")
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        snap = self.conn.execute("SELECT d7, d30, d90 FROM snapshot WHERE entity_id = 1 AND taken_at = '2026-09-26'").fetchone()
        # d7: 7일 이상 지난 가장 가까운 스냅샷 없음(6일 전뿐) → 37일 전 기준은 d30·d90 에만 쓴다
        self.assertEqual((snap["d7"], snap["d30"], snap["d90"]), (None, 400, None))
        self.assertEqual(self.scoped()["github:a/b"], ("include", "rising"))

    def test_history도_이전_스냅샷도_없으면_스타_기준만_적용한다(self):
        gh = FakeGH({1: raw_repo(1, "a/b", 5000), 2: raw_repo(2, "c/d", 500)},
                    {1: NotFound("x"), 2: GitHubError("x")})
        metrics.refresh(self.conn, gh, CONFIG, self.today)
        snap = self.conn.execute("SELECT d30 FROM snapshot WHERE entity_id = 2").fetchone()
        self.assertIsNone(snap["d30"])
        self.assertEqual(self.scoped(), {"github:a/b": ("include", "famous"), "github:c/d": ("exclude", "below_threshold")})


if __name__ == "__main__":
    unittest.main()
