import json
import tempfile
import unittest
from pathlib import Path

from labbook import db, idea


def seed(conn):
    conn.execute("INSERT INTO entity (id, kind, key, gh_id, url, first_seen_at) VALUES (5, 'github_repo', 'github:a/b', 1, 'u', 't')")
    conn.execute("INSERT INTO signal (id, topic, entity_id, kind, quote, source_url, found_at) VALUES (7, 't', 5, 'demand', 'q', 'u', 't')")
    conn.execute("INSERT INTO signal (id, topic, entity_id, kind, quote, source_url, found_at) VALUES (8, 't', 5, 'pain', 'q2', 'u2', 't')")
    conn.execute("INSERT INTO signal (id, topic, entity_id, kind, quote, source_url, found_at) VALUES (9, 'other', 5, 'gap', 'q3', 'u3', 't')")
    conn.commit()


DRAFT = {"title": "한국 공시 알림", "jtbd": "공시를 놓치지 않으려는 개인이 알림을 원한다", "lens": "한국화",
         "signal_ids": [7, 8], "scores": {"수요": 4, "차별성": 3}, "status": "draft"}


class IdeaLoadTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)
        db.migrate(self.conn)
        seed(self.conn)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, *rows, name="ideas.jsonl"):
        path = self.dir / name
        path.write_text("".join(
            (r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)) + "\n" for r in rows))
        return path

    def rows(self):
        return [dict(r) for r in self.conn.execute("SELECT * FROM idea ORDER BY id")]

    # 1
    def test_정상_2줄을_적재하고_created_at은_ISO_형식이다(self):
        second = {**DRAFT, "title": "곡괭이 MCP", "signal_ids": []}
        out = idea.load(self.conn, "t", self.write(DRAFT, second))
        self.assertEqual({"added": 2, "updated": 0, "total": 2}, out)
        rows = self.rows()
        self.assertEqual(["한국 공시 알림", "곡괭이 MCP"], [r["title"] for r in rows])
        self.assertEqual([7, 8], json.loads(rows[0]["signal_ids"]))
        self.assertEqual({"수요": 4, "차별성": 3}, json.loads(rows[0]["scores"]))
        self.assertTrue(rows[0]["created_at"].endswith("+00:00"), rows[0]["created_at"])

    # 2
    def test_상태만_담아_재적재하면_나머지_필드가_유지된다(self):
        idea.load(self.conn, "t", self.write(DRAFT))
        before = self.rows()[0]
        out = idea.load(self.conn, "t", self.write(
            {"title": DRAFT["title"], "status": "shortlist", "doc_path": "topics/t/ideas/dart-alert.md"}))
        self.assertEqual({"added": 0, "updated": 1, "total": 1}, out)
        after = self.rows()[0]
        self.assertEqual("shortlist", after["status"])
        self.assertEqual("topics/t/ideas/dart-alert.md", after["doc_path"])
        for col in ("jtbd", "lens", "signal_ids", "scores", "created_at"):
            self.assertEqual(before[col], after[col], col)

    # 3
    def test_status_오타는_줄_번호를_내고_DB를_바꾸지_않는다(self):
        path = self.write(DRAFT, {**DRAFT, "title": "둘째", "status": "drafts"})
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", path)
        self.assertIn(":2", str(e.exception))
        self.assertEqual([], self.rows())

    # 4
    def test_없는_signal_id는_거부한다(self):
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", self.write({**DRAFT, "signal_ids": [7, 999]}))
        self.assertIn("999", str(e.exception))
        self.assertEqual([], self.rows())

    def test_다른_주제의_signal_id는_거부한다(self):
        with self.assertRaises(ValueError):
            idea.load(self.conn, "t", self.write({**DRAFT, "signal_ids": [9]}))

    # 5
    def test_dropped는_reason이_shortlist는_doc_path가_필요하다(self):
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", self.write({**DRAFT, "status": "dropped"}))
        self.assertIn("reason", str(e.exception))
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", self.write({**DRAFT, "status": "shortlist"}))
        self.assertIn("doc_path", str(e.exception))
        self.assertEqual([], self.rows())

    def test_reason과_doc_path가_있으면_통과한다(self):
        idea.load(self.conn, "t", self.write(
            {**DRAFT, "status": "dropped", "reason": "중복: 곡괭이 MCP"},
            {**DRAFT, "title": "둘째", "status": "shortlist", "doc_path": "topics/t/ideas/x.md"}))
        self.assertEqual(["dropped", "shortlist"], [r["status"] for r in self.rows()])

    # 6
    def test_JSON이_아닌_줄과_객체가_아닌_줄은_줄_번호를_낸다(self):
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", self.write(DRAFT, "{깨진 줄"))
        self.assertIn(":2", str(e.exception))
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", self.write("[1, 2]"))
        self.assertIn(":1", str(e.exception))
        self.assertEqual([], self.rows())

    # 7
    def test_빈_파일과_빈_줄만_있는_파일은_예외_없이_0건이다(self):
        self.assertEqual({"added": 0, "updated": 0, "total": 0},
                         idea.load(self.conn, "t", self.write()))
        self.assertEqual({"added": 0, "updated": 0, "total": 0},
                         idea.load(self.conn, "t", self.write("", "   ")))

    # 8
    def test_파일이_없으면_경로를_담은_에러를_낸다(self):
        missing = self.dir / "없다.jsonl"
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", missing)
        self.assertIn(str(missing), str(e.exception))

    # 9
    def test_작은따옴표와_개행이_든_값이_그대로_들어간다(self):
        quirky = {**DRAFT, "jtbd": "'따옴표' 와\n개행이 든 문장", "status": "dropped",
                  "reason": "중복: it's a 'dup'"}
        idea.load(self.conn, "t", self.write(quirky))
        row = self.rows()[0]
        self.assertEqual(quirky["jtbd"], row["jtbd"])
        self.assertEqual(quirky["reason"], row["reason"])

    # 11
    def test_한_파일에_같은_title이_두_줄이면_거부한다(self):
        with self.assertRaises(ValueError) as e:
            idea.load(self.conn, "t", self.write(DRAFT, {**DRAFT, "lens": "언번들"}))
        self.assertIn(":2", str(e.exception))
        self.assertEqual([], self.rows())

    def test_title이_비어_있으면_거부한다(self):
        with self.assertRaises(ValueError):
            idea.load(self.conn, "t", self.write({**DRAFT, "title": "  "}))

    # 12
    def test_새_행에는_signal_ids와_status가_필요하다(self):
        for missing in ("signal_ids", "status"):
            row = {k: v for k, v in DRAFT.items() if k != missing}
            with self.assertRaises(ValueError) as e:
                idea.load(self.conn, "t", self.write(row))
            self.assertIn(missing, str(e.exception))
        self.assertEqual([], self.rows())

    def test_signal_ids가_정수_배열이_아니면_거부한다(self):
        for bad in ("7,8", [7, "8"], {"a": 1}):
            with self.assertRaises(ValueError):
                idea.load(self.conn, "t", self.write({**DRAFT, "signal_ids": bad}))

    def test_scores가_객체도_null도_아니면_거부한다(self):
        with self.assertRaises(ValueError):
            idea.load(self.conn, "t", self.write({**DRAFT, "scores": [4, 3]}))
        idea.load(self.conn, "t", self.write({**DRAFT, "scores": None}))
        self.assertIsNone(self.rows()[0]["scores"])

    def test_다른_주제의_같은_제목은_별개_행이다(self):
        conn = self.conn
        conn.execute("INSERT INTO signal (id, topic, entity_id, kind, quote, source_url, found_at) "
                     "VALUES (10, 'u', 5, 'demand', 'q', 'u4', 't')")
        idea.load(conn, "t", self.write(DRAFT))
        idea.load(conn, "u", self.write({**DRAFT, "signal_ids": [10]}))
        self.assertEqual(2, len(self.rows()))


if __name__ == "__main__":
    unittest.main()
