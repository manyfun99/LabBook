import json
import tempfile
import unittest
from pathlib import Path

from labbook import archive, db


def seed(conn):
    conn.execute("INSERT INTO entity (id, kind, key, gh_id, url, first_seen_at) VALUES (5, 'github_repo', 'github:a/b', 1, 'u', 't')")
    conn.execute("INSERT INTO entity (id, kind, key, gh_id, url, first_seen_at) VALUES (9, 'github_repo', 'github:c/d', 2, 'u', 't')")
    conn.execute("INSERT INTO screening VALUES ('t', 5, 'identified', 'include', NULL, '[\"star\"]', 't')")
    conn.execute("INSERT INTO snapshot (entity_id, taken_at, stars, flags) VALUES (9, '2026-09-26', 10, '[]')")
    conn.execute("INSERT INTO snapshot (entity_id, taken_at, stars, flags) VALUES (5, '2026-10-03', 30, '[]')")
    conn.execute("INSERT INTO snapshot (entity_id, taken_at, stars, flags) VALUES (5, '2026-09-26', 20, '[]')")
    conn.execute("INSERT INTO judgment (id, topic, entity_id, stage, rubric_version, model, scores, evidence, judged_at) "
                 "VALUES (3, 't', 5, 'full', 'v1', 'm', '{\"P\":4}', '{\"P\":\"한글 인용\"}', 't')")
    conn.execute("INSERT INTO signal (id, topic, entity_id, kind, quote, source_url, found_at) VALUES (7, 't', 5, 'demand', 'q', 'u', 't')")
    conn.execute("INSERT INTO signal (id, topic, entity_id, kind, quote, source_url, found_at) VALUES (8, 't', 9, 'pain', 'q2', 'u2', 't')")
    conn.execute("INSERT INTO idea (id, topic, title, signal_ids, status, created_at) VALUES (1, 't', '아이디어', '[7, 8]', 'draft', 't')")
    conn.commit()


def dump(conn):
    return {t: [dict(r) for r in conn.execute(f"SELECT * FROM {t} ORDER BY 1, 2")] for t in archive.TABLES}


class ArchiveTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)
        db.migrate(self.conn)
        seed(self.conn)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name)

    def test_export_후_import하면_같은_내용으로_복원된다(self):
        archive.export(self.conn, self.data)
        fresh = db.connect(":memory:")
        self.addCleanup(fresh.close)
        archive.import_(fresh, self.data)
        self.assertEqual(dump(fresh), dump(self.conn))

    def test_id가_유지돼_idea의_signal_참조가_살아있다(self):
        archive.export(self.conn, self.data)
        fresh = db.connect(":memory:")
        self.addCleanup(fresh.close)
        archive.import_(fresh, self.data)
        ids = json.loads(fresh.execute("SELECT signal_ids FROM idea").fetchone()[0])
        quotes = [fresh.execute("SELECT quote FROM signal WHERE id = ?", (i,)).fetchone()[0] for i in ids]
        self.assertEqual(quotes, ["q", "q2"])

    def test_import는_뷰까지_마이그레이션을_먼저_적용한다(self):
        archive.export(self.conn, self.data)
        fresh = db.connect(":memory:")
        self.addCleanup(fresh.close)
        archive.import_(fresh, self.data)
        self.assertEqual(fresh.execute("SELECT key FROM v_repo_latest").fetchone()[0], "github:a/b")

    def test_snapshot은_날짜_엔티티_순으로_쓴다(self):
        archive.export(self.conn, self.data)
        rows = [json.loads(line) for line in (self.data / "snapshot.jsonl").read_text().splitlines()]
        self.assertEqual([(r["taken_at"], r["entity_id"]) for r in rows],
                         [("2026-09-26", 5), ("2026-09-26", 9), ("2026-10-03", 5)])

    def test_한글을_이스케이프하지_않고_schema_version은_내보내지_않는다(self):
        archive.export(self.conn, self.data)
        self.assertIn("한글 인용", (self.data / "judgment.jsonl").read_text())
        self.assertFalse((self.data / "schema_version.jsonl").exists())

    def test_같은_내용이면_두번_export해도_파일이_같다(self):
        archive.export(self.conn, self.data)
        first = {p.name: p.read_text() for p in self.data.glob("*.jsonl")}
        archive.export(self.conn, self.data)
        self.assertEqual({p.name: p.read_text() for p in self.data.glob("*.jsonl")}, first)

    def test_비어있지_않은_DB에는_import하지_않는다(self):
        archive.export(self.conn, self.data)
        with self.assertRaises(ValueError):
            archive.import_(self.conn, self.data)


if __name__ == "__main__":
    unittest.main()
