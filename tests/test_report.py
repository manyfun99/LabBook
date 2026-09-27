import json
import tempfile
import unittest
from pathlib import Path

from labbook import db, report


class Seed:
    def __init__(self, conn):
        self.conn = conn

    def repo(self, gh_id, *, sources=("search:x",), scoped=("include", "famous"), triaged=None, scores=None,
             market="us", category="llm-agent", stars=1000, d30=0, flags=(), injection=False):
        c = self.conn
        eid = c.execute("INSERT INTO entity (kind, key, gh_id, first_seen_at) VALUES ('github_repo', ?, ?, 't')",
                        (f"github:o/r{gh_id}", gh_id)).lastrowid
        c.execute("INSERT INTO screening (topic, entity_id, stage, decision, sources, decided_at) "
                  "VALUES ('t', ?, 'identified', 'include', ?, 't')", (eid, json.dumps(list(sources))))
        c.execute("INSERT INTO screening (topic, entity_id, stage, decision, reason, decided_at) VALUES ('t', ?, 'scoped', ?, ?, 't')",
                  (eid, *scoped))
        c.execute("INSERT INTO snapshot (entity_id, taken_at, stars, d30, flags) VALUES (?, '2026-09-26', ?, ?, ?)",
                  (eid, stars, d30, json.dumps(list(flags))))
        if triaged:
            c.execute("INSERT INTO screening (topic, entity_id, stage, decision, reason, decided_at) VALUES ('t', ?, 'triaged', ?, ?, 't')",
                      (eid, *triaged))
        if scores:
            c.execute("INSERT INTO screening (topic, entity_id, stage, decision, decided_at) VALUES ('t', ?, 'judged', 'include', 't')",
                      (eid,))
            c.execute("INSERT INTO judgment (topic, entity_id, stage, rubric_version, model, category, market, summary_ko, "
                      "scores, evidence, judged_at) VALUES ('t', ?, 'full', 'v1', 'm', ?, ?, ?, ?, ?, 't')",
                      (eid, category, market, f"요약 {gh_id}", json.dumps(dict(zip("PINT", scores))),
                       json.dumps({"injection_suspect": injection})))
        c.commit()
        return eid


class Base(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)
        db.migrate(self.conn)
        self.seed = Seed(self.conn)


class TopTest(Base):
    def test_P순_동점은_T_다음_스타(self):
        self.seed.repo(1, scores=(5, 1, 1, 2), stars=100)
        self.seed.repo(2, scores=(5, 1, 1, 3), stars=100)
        self.seed.repo(3, scores=(5, 1, 1, 3), stars=900)
        self.seed.repo(4, scores=(4, 5, 5, 5), stars=99999)
        self.assertEqual([r["key"] for r in report.top(self.conn, "t", "P")],
                         ["github:o/r3", "github:o/r2", "github:o/r1", "github:o/r4"])

    def test_momentum은_d30순(self):
        self.seed.repo(1, scores=(1, 1, 1, 1), d30=10)
        self.seed.repo(2, scores=(1, 1, 1, 1), d30=500)
        self.assertEqual([r["key"] for r in report.top(self.conn, "t", "momentum")], ["github:o/r2", "github:o/r1"])

    def test_판정되지_않은_레포는_빠진다(self):
        self.seed.repo(1)
        self.assertEqual(report.top(self.conn, "t", "P"), [])


class SelectTest(Base):
    def test_P5_I5_라이징3_한국2_순서로_채우고_이미_뽑힌_레포는_건너뛴다(self):
        for i in range(1, 7):      # P 상위 후보 6개 (1~5 가 뽑힘)
            self.seed.repo(i, scores=(5, 1, 1, 1), stars=1000 - i)
        self.seed.repo(7, scores=(5, 5, 1, 5), stars=10)       # P 동점이지만 T 가 높아 P 1순위
        for i in range(8, 13):     # I 상위
            self.seed.repo(i, scores=(1, 5, 1, 1), stars=1000 - i)
        self.seed.repo(13, scores=(1, 1, 1, 1), d30=900)
        self.seed.repo(14, scores=(1, 1, 1, 1), d30=800)
        self.seed.repo(15, scores=(1, 1, 1, 1), d30=700)
        self.seed.repo(16, scores=(1, 1, 1, 1), d30=600)
        self.seed.repo(17, scores=(2, 4, 1, 1), market="kr")
        self.seed.repo(18, scores=(3, 1, 1, 1), market="kr")
        self.seed.repo(19, scores=(1, 1, 1, 1), market="kr")
        picks = report.select(self.conn, "t")
        slots = {}
        for p in picks:
            slots.setdefault(p["slot"], []).append(int(p["key"].split("/r")[1]))
        self.assertEqual(slots["P"], [7, 1, 2, 3, 4])
        self.assertEqual(slots["I"], [8, 9, 10, 11, 12])   # 7 은 이미 P 에서 뽑혀 건너뜀
        self.assertEqual(slots["rising"], [13, 14, 15])
        self.assertEqual(slots["kr"], [17, 18])
        self.assertEqual(len(picks), 15)

    def test_현재_범위에서_빠진_레포는_후보와_상위_목록에서_제외한다(self):
        self.seed.repo(1, scores=(5, 5, 5, 5), scoped=("exclude", "archived"))
        self.seed.repo(2, scores=(1, 1, 1, 1))
        self.assertEqual([p["key"] for p in report.select(self.conn, "t")], ["github:o/r2"])
        self.assertEqual([r["key"] for r in report.top(self.conn, "t", "P")], ["github:o/r2"])

    def test_confirm_해야_deep_단계를_쓴다(self):
        self.seed.repo(1, scores=(5, 5, 5, 5))
        report.select(self.conn, "t")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM screening WHERE stage = 'deep'").fetchone()[0], 0)
        report.select(self.conn, "t", confirm=True)
        row = self.conn.execute("SELECT decision, reason FROM screening WHERE stage = 'deep'").fetchone()
        self.assertEqual((row["decision"], row["reason"]), ("include", "P"))

    def test_사용자_지정분을_더한다(self):
        self.seed.repo(1, scores=(5, 5, 5, 5))
        self.seed.repo(2)
        picks = report.select(self.conn, "t", add=["O/R2"], confirm=True)
        self.assertEqual(picks[-1], {"slot": "user", "key": "github:o/r2", "entity_id": 2})
        reasons = {r["reason"] for r in self.conn.execute("SELECT reason FROM screening WHERE stage = 'deep'")}
        self.assertEqual(reasons, {"P", "user"})

    def test_모르는_레포를_지정하면_오류(self):
        with self.assertRaises(ValueError):
            report.select(self.conn, "t", add=["no/such"])


class FunnelTest(Base):
    def test_단계별_건수와_제외_사유를_쓴다(self):
        self.seed.repo(1, sources=("search:a", "awesome:x"), scores=(5, 5, 5, 5), triaged=("include", None),
                       flags=("spike",))
        self.seed.repo(2, sources=("kr:k",), scoped=("exclude", "below_threshold"))
        self.seed.repo(3, sources=("star",), triaged=("exclude", "unrelated"))
        self.seed.repo(4, triaged=("unsure", None), scores=(1, 1, 1, 1), injection=True, category="data-mcp")
        report.select(self.conn, "t", confirm=True)
        with tempfile.TemporaryDirectory() as d:
            text = report.funnel(self.conn, "t", Path(d), "2026-09-26")
            self.assertEqual((Path(d) / "reports" / "funnel-2026-09-26.md").read_text(), text)
        self.assertIn("식별 4 (검색 2 · awesome 1 · 스타 1 · 한국 1, 중복 제거 전 5)", text)
        self.assertIn("범위 컷 제외 1 (below_threshold 1)", text)
        self.assertIn("범위 내 3 (의심 표시 2", text)
        self.assertIn("1단 제외 1 (unrelated 1)", text)
        self.assertIn("정밀 판정 2", text)
        self.assertIn("llm-agent 1", text)
        self.assertIn("data-mcp 1", text)
        self.assertIn("심층분석 2", text)


class SuspectsTest(Base):
    def included(self):
        return {r[0] for r in self.conn.execute(
            "SELECT entity_id FROM screening WHERE topic = 't' AND stage = 'scoped' AND decision = 'include'")}

    def test_1단_판정의_바이너리_링크도_의심으로_센다(self):
        eid = self.seed.repo(1)
        self.conn.execute("INSERT INTO judgment (topic, entity_id, stage, rubric_version, model, evidence, judged_at) "
                          "VALUES ('t', ?, 'triage', 'v1', 'm', ?, 't')",
                          (eid, json.dumps({"injection_suspect": False, "binary_link": True})))
        self.seed.repo(2)
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 1)

    def test_플래그는_최신_스냅샷만_본다(self):
        eid = self.seed.repo(1)   # 최신(2026-09-26) 스냅샷 플래그 없음
        self.conn.execute("INSERT INTO snapshot (entity_id, taken_at, stars, flags) VALUES (?, '2026-09-19', 1000, ?)",
                          (eid, json.dumps(["spike"])))
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 0)

    def test_범위_밖_레포와_플래그가_NULL인_스냅샷은_세지_않는다(self):
        self.seed.repo(1, scoped=("exclude", "below_threshold"), flags=("spike",))
        eid = self.seed.repo(2)
        self.conn.execute("UPDATE snapshot SET flags = NULL WHERE entity_id = ?", (eid,))
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 0)

    def test_판정_증거가_NULL이거나_키가_없으면_세지_않는다(self):
        for gh_id, evidence in [(1, None), (2, "{}"), (3, json.dumps({"injection_suspect": False}))]:
            eid = self.seed.repo(gh_id)
            self.conn.execute("INSERT INTO judgment (topic, entity_id, stage, rubric_version, model, evidence, judged_at) "
                              "VALUES ('t', ?, 'triage', 'v1', 'm', ?, 't')", (eid, evidence))
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 0)

    def test_범위_밖_레포의_판정_증거는_세지_않는다(self):
        self.seed.repo(1, scoped=("exclude", "below_threshold"), scores=(1, 1, 1, 1), injection=True)
        self.seed.repo(2)
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 0)

    def test_플래그나_판정_증거가_빈_문자열이면_빈_값으로_본다(self):
        eid = self.seed.repo(1)
        self.conn.execute("UPDATE snapshot SET flags = '' WHERE entity_id = ?", (eid,))
        self.conn.execute("INSERT INTO judgment (topic, entity_id, stage, rubric_version, model, evidence, judged_at) "
                          "VALUES ('t', ?, 'triage', 'v1', 'm', '', 't')", (eid,))
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 0)

    def test_다른_토픽의_판정_증거는_세지_않는다(self):
        eid = self.seed.repo(1)
        self.conn.execute("INSERT INTO judgment (topic, entity_id, stage, rubric_version, model, evidence, judged_at) "
                          "VALUES ('other', ?, 'triage', 'v1', 'm', ?, 't')", (eid, json.dumps({"binary_link": True})))
        self.assertEqual(report._suspects(self.conn, "t", self.included()), 0)

    def test_쿼리_수는_레포_수와_무관하다(self):
        def statements():
            n, included = [], self.included()   # trace 를 켜기 전에 — _suspects 의 문장만 센다
            self.conn.set_trace_callback(n.append)
            try:
                count = report._suspects(self.conn, "t", included)
            finally:
                self.conn.set_trace_callback(None)
            return len(n), count

        self.seed.repo(1, scores=(1, 1, 1, 1))
        one, _ = statements()
        for i in range(2, 21):   # 3의 배수는 플래그, 5의 배수는 인젝션 — 15 는 둘 다
            self.seed.repo(i, scores=(1, 1, 1, 1), flags=("spike",) if i % 3 == 0 else (), injection=i % 5 == 0)
        self.assertEqual(statements(), (one, 9))   # 3·6·9·12·15·18 + 5·10·20


if __name__ == "__main__":
    unittest.main()
