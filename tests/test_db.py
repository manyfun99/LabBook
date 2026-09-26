import sqlite3
import unittest

from labbook import db


class MigrateTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)

    def test_빈_DB에_마이그레이션을_적용하면_테이블과_뷰가_생긴다(self):
        applied = db.migrate(self.conn)
        self.assertEqual(applied, [1])
        names = {r["name"] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        for t in ("entity", "screening", "snapshot", "judgment", "signal", "idea", "v_repo_latest", "schema_version"):
            self.assertIn(t, names)

    def test_두번_적용하면_아무것도_적용하지_않는다(self):
        db.migrate(self.conn)
        self.assertEqual(db.migrate(self.conn), [])
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0], 1)

    def test_같은_단계의_판정은_두번_쓸_수_없다(self):
        db.migrate(self.conn)
        self.conn.execute("INSERT INTO entity (kind, key, gh_id, first_seen_at) VALUES ('github_repo', 'github:a/b', 1, 't')")
        row = ("stock-oss", 1, "full", "v1", "opus", "t")
        sql = "INSERT INTO judgment (topic, entity_id, stage, rubric_version, model, judged_at) VALUES (?,?,?,?,?,?)"
        self.conn.execute(sql, row)
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(sql, row)

    def test_같은_신호는_중복_저장되지_않는다(self):
        db.migrate(self.conn)
        sql = "INSERT OR IGNORE INTO signal (topic, kind, quote, source_url, found_at) VALUES ('t', 'demand', 'q', 'u', 'x')"
        self.conn.execute(sql)
        self.conn.execute(sql)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM signal").fetchone()[0], 1)

    def test_외래키가_켜져_있다(self):
        db.migrate(self.conn)
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO snapshot (entity_id, taken_at) VALUES (999, '2026-09-26')")

    def test_마이그레이션이_실패하면_일부만_적용되지_않는다(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            Path(d, "001_bad.sql").write_text("CREATE TABLE a (x INTEGER);\nCREATE TABLE a (x INTEGER);\n")
            with mock.patch.object(db, "MIGRATIONS", Path(d)):
                with self.assertRaises(sqlite3.OperationalError):
                    db.migrate(self.conn)
        names = {r["name"] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertNotIn("a", names)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0], 0)



class SetScreeningTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)
        db.migrate(self.conn)
        self.conn.execute("INSERT INTO entity (kind, key, gh_id, first_seen_at) VALUES ('github_repo', 'github:a/b', 1, 't')")

    def row(self, stage):
        return self.conn.execute("SELECT * FROM screening WHERE topic = 't' AND entity_id = 1 AND stage = ?",
                                 (stage,)).fetchone()

    def test_없으면_넣는다(self):
        db.set_screening(self.conn, "t", 1, "triaged", "error", "missing_in_response")
        r = self.row("triaged")
        self.assertEqual((r["decision"], r["reason"]), ("error", "missing_in_response"))
        self.assertIsNotNone(r["decided_at"])

    def test_있으면_판정_사유_시각을_덮어쓰고_sources는_보존한다(self):
        self.conn.execute("INSERT INTO screening (topic, entity_id, stage, decision, reason, sources, decided_at) "
                          "VALUES ('t', 1, 'scoped', 'exclude', 'below_threshold', '[\"star\"]', 'old')")
        db.set_screening(self.conn, "t", 1, "scoped", "include", None)
        r = self.row("scoped")
        self.assertEqual((r["decision"], r["reason"], r["sources"]), ("include", None, '["star"]'))
        self.assertNotEqual(r["decided_at"], "old")
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM screening").fetchone()[0], 1)

    def test_다른_단계는_건드리지_않는다(self):
        db.set_screening(self.conn, "t", 1, "scoped", "include", "famous")
        db.set_screening(self.conn, "t", 1, "triaged", "exclude", "unrelated")
        self.assertEqual(self.row("scoped")["reason"], "famous")


if __name__ == "__main__":
    unittest.main()
