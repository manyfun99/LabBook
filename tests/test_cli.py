import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from labbook import cli, db
from tests.test_collect import CONFIG, FakeGitHub

CONNECT = db.connect  # 패치 전 원본


class CollectCommandTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.topic_dir = self.root / "topics" / "t"
        self.topic_dir.mkdir(parents=True)
        (self.topic_dir / "config.json").write_text(json.dumps(CONFIG))

    def run_main(self, gh, *argv):
        def connect(path):  # cli.main 은 연결을 닫지 않는다 — 테스트에서 닫는다
            conn = CONNECT(path)
            self.addCleanup(conn.close)
            return conn

        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(cli, "ROOT", self.root), mock.patch.object(cli, "DATA", self.root / "data"), \
                mock.patch.object(cli, "CACHE", self.root / ".cache"), mock.patch.object(cli, "GitHub", lambda **kw: gh), \
                mock.patch.object(cli.db, "connect", connect), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            cli.main(["--db", str(self.root / "x.db"), *argv])
        return out.getvalue(), err.getvalue()

    def test_collect는_잘린_검색을_stderr에_경고하고_log에_남긴다(self):
        gh = FakeGitHub()
        gh.truncated = [("kw stars:100..199 created:2026-01-01..2026-12-31", 1400)]
        _, err = self.run_main(gh, "collect", "t")
        self.assertIn("경고: 검색이 1000건에서 잘림 — kw stars:100..199 created:2026-01-01..2026-12-31 (전체 1400)", err)
        self.assertIn("collect | 엔티티 0 · 잘린 검색 1", (self.topic_dir / "log.md").read_text())

    def test_잘린_검색이_없으면_경고하지_않는다(self):
        _, err = self.run_main(FakeGitHub(), "collect", "t")
        self.assertEqual(err, "")
        self.assertNotIn("잘린 검색", (self.topic_dir / "log.md").read_text())


if __name__ == "__main__":
    unittest.main()
