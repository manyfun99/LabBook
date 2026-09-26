import base64
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from labbook import github

FIX = Path(__file__).parent / "fixtures"


def fixture(name):
    return json.loads((FIX / f"{name}.json").read_text())


def http(status, body=None, headers=None):
    """gh api -i 출력 형태의 CompletedProcess 를 만든다."""
    lines = [f"HTTP/2.0 {status} X"] + [f"{k}: {v}" for k, v in (headers or {}).items()]
    text = "\n".join(lines) + "\n\n" + (json.dumps(body) if body is not None else "")
    return subprocess.CompletedProcess([], 0 if status == 200 else 1, stdout=text, stderr="")


class FakeRunner:
    """경로별 응답 목록(순서대로 소비) 또는 경로를 받아 응답을 돌려주는 함수."""

    def __init__(self, routes=None, handler=None):
        self.routes = {k: list(v) for k, v in (routes or {}).items()}
        self.handler = handler
        self.calls = []

    def __call__(self, args, **kwargs):
        path = args[-1]
        self.calls.append(path)
        if self.handler:
            return self.handler(path)
        resp = self.routes[path].pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


def make(runner, **kw):
    sleeps = []
    gh = github.GitHub(runner=runner, sleep=sleeps.append, clock=lambda: 1000.0, **kw)
    return gh, sleeps


class RequestTest(unittest.TestCase):
    def test_200이면_본문을_돌려준다(self):
        gh, _ = make(FakeRunner({"repos/a/b": [http(200, {"id": 1})]}))
        self.assertEqual(gh.get("repos/a/b"), {"id": 1})

    def test_404면_NotFound(self):
        gh, _ = make(FakeRunner({"repos/a/b": [http(404, {"message": "Not Found"})]}))
        with self.assertRaises(github.NotFound):
            gh.get("repos/a/b")

    def test_레이트리밋이면_리셋_시각까지_기다렸다가_재시도한다(self):
        limited = http(403, {"message": "rate limit"}, {"X-Ratelimit-Remaining": "0", "X-Ratelimit-Reset": "1010"})
        gh, sleeps = make(FakeRunner({"p": [limited, http(200, {"ok": 1})]}))
        self.assertEqual(gh.get("p"), {"ok": 1})
        self.assertEqual(sleeps, [11])

    def test_Retry_After_가_있으면_그만큼_기다린다(self):
        gh, sleeps = make(FakeRunner({"p": [http(429, {}, {"Retry-After": "7"}), http(200, {"ok": 1})]}))
        gh.get("p")
        self.assertEqual(sleeps, [7])

    def test_레이트리밋이_계속되면_10번_기다린_뒤_실패한다(self):
        limited = http(429, {}, {"Retry-After": "1"})
        gh, sleeps = make(FakeRunner({"p": [limited] * 11}))
        with self.assertRaises(github.GitHubError):
            gh.get("p")
        self.assertEqual(len(sleeps), 10)

    def test_권한_403은_재시도하지_않고_실패한다(self):
        gh, sleeps = make(FakeRunner({"p": [http(403, {"message": "Forbidden"}, {"X-Ratelimit-Remaining": "4000"})]}))
        with self.assertRaises(github.GitHubError):
            gh.get("p")
        self.assertEqual(sleeps, [])

    def test_5xx는_지수_백오프로_3회까지_재시도한다(self):
        gh, sleeps = make(FakeRunner({"p": [http(502), http(502), http(502), http(200, {"ok": 1})]}))
        self.assertEqual(gh.get("p"), {"ok": 1})
        self.assertEqual(sleeps, [1, 2, 4])

    def test_5xx가_4번_연속이면_실패한다(self):
        gh, _ = make(FakeRunner({"p": [http(502)] * 4}))
        with self.assertRaises(github.GitHubError):
            gh.get("p")

    def test_타임아웃도_5xx처럼_재시도한다(self):
        gh, sleeps = make(FakeRunner({"p": [subprocess.TimeoutExpired("gh", 30), http(200, {"ok": 1})]}))
        self.assertEqual(gh.get("p"), {"ok": 1})
        self.assertEqual(sleeps, [1])

    def test_남은_한도가_0이면_다음_호출_전에_리셋까지_기다린다(self):
        ok = http(200, {"ok": 1}, {"X-Ratelimit-Remaining": "0", "X-Ratelimit-Reset": "1005"})
        gh, sleeps = make(FakeRunner({"p": [ok]}))
        gh.get("p")
        self.assertEqual(sleeps, [6])


class EndpointTest(unittest.TestCase):
    def test_repo는_필요한_필드로_정규화한다(self):
        gh, _ = make(FakeRunner({"repos/dragon1086/prism-insight": [http(200, fixture("repo_prism_insight"))]}))
        r = gh.repo("dragon1086/prism-insight")
        self.assertEqual(r["gh_id"], fixture("repo_prism_insight")["id"])
        self.assertEqual(r["full_name"], "dragon1086/prism-insight")
        self.assertEqual(r["watchers"], fixture("repo_prism_insight")["subscribers_count"])
        self.assertIn("stars", r)

    def test_repo_by_id는_gh_id_경로로_조회해_정규화한다(self):
        raw = fixture("repo_prism_insight")
        runner = FakeRunner({f"repositories/{raw['id']}": [http(200, raw)]})
        gh, _ = make(runner)
        self.assertEqual(gh.repo_by_id(raw["id"]), github.normalize_repo(raw))
        self.assertEqual(runner.calls, [f"repositories/{raw['id']}"])

    def test_repo_by_id는_없으면_NotFound(self):
        gh, _ = make(FakeRunner({"repositories/9": [http(404, {"message": "Not Found"})]}))
        with self.assertRaises(github.NotFound):
            gh.repo_by_id(9)

    def test_history는_page1을_돌려준다(self):
        gh, _ = make(FakeRunner({"repos/a/b/stargazers/history": [http(200, fixture("history_prism_insight"))]}))
        self.assertEqual(len(gh.history("a/b")), 30)

    def test_readme는_디코딩하고_blob_sha를_주며_캐시한다(self):
        with tempfile.TemporaryDirectory() as d:
            runner = FakeRunner({"repos/a/b/readme": [http(200, fixture("readme_prism_insight"))]})
            gh, _ = make(runner, cache_dir=Path(d))
            text, sha = gh.readme("a/b")
            self.assertTrue(text.startswith('<div align="center">'))
            self.assertEqual(sha, fixture("readme_prism_insight")["sha"])
            self.assertEqual(gh.readme("a/b"), (text, sha))
            self.assertEqual(runner.calls, ["repos/a/b/readme"])

    def test_readme_캐시는_7일이_지나면_다시_받는다(self):
        with tempfile.TemporaryDirectory() as d:
            now = [1000.0]
            runner = FakeRunner({"repos/a/b/readme": [http(200, fixture("readme_prism_insight"))] * 2})
            gh = github.GitHub(runner=runner, sleep=lambda s: None, clock=lambda: now[0], cache_dir=Path(d))
            gh.readme("a/b")
            now[0] += 7 * 86400
            gh.readme("a/b")
            self.assertEqual(len(runner.calls), 1)
            now[0] += 1
            gh.readme("a/b")
            self.assertEqual(len(runner.calls), 2)

    def test_awesome_목록은_캐시를_쓰지_않고_매번_새로_읽는다(self):
        with tempfile.TemporaryDirectory() as d:
            body = {"sha": "s", "encoding": "base64", "content": base64.b64encode(b"- https://github.com/x/y").decode()}
            runner = FakeRunner({"repos/o/list/readme": [http(200, body)] * 2})
            gh, _ = make(runner, cache_dir=Path(d))
            gh.awesome_links("o/list")
            gh.awesome_links("o/list")
            self.assertEqual(len(runner.calls), 2)

    def test_readme가_없으면_빈_문자열(self):
        gh, _ = make(FakeRunner({"repos/a/b/readme": [http(404, {})]}))
        self.assertEqual(gh.readme("a/b"), ("", None))

    def test_top_issues는_PR을_빼고_제목_댓글수_url을_준다(self):
        path = "repos/a/b/issues?state=all&sort=comments&direction=desc&per_page=100"
        gh, _ = make(FakeRunner({path: [http(200, fixture("issues_prism_insight"))]}))
        self.assertEqual(gh.top_issues("a/b", limit=30), [{
            "title": "[CLA] 기존 기여에 대한 소급 동의 요청 / Retroactive consent request",
            "comments": 9,
            "url": "https://github.com/dragon1086/prism-insight/issues/603",
        }])

    def test_top_issues는_limit만큼만_준다(self):
        path = "repos/a/b/issues?state=all&sort=comments&direction=desc&per_page=100"
        many = [{"title": f"t{i}", "comments": 1, "html_url": f"u{i}"} for i in range(50)]
        gh, _ = make(FakeRunner({path: [http(200, many)]}))
        self.assertEqual(len(gh.top_issues("a/b", limit=30)), 30)

    def test_awesome_링크_추출(self):
        text = (
            "- [A](https://github.com/Foo/bar-baz) x\n"
            "- [B](https://github.com/foo/bar-baz#readme) 중복\n"
            "- [C](https://github.com/topics/trading) 제외\n"
            "- [D](https://github.com/x/y.git)\n"
            "- [E](https://github.com/owner/self) 자기 자신\n"
            "- [F](https://github.com/sponsors/someone)\n"
        )
        runner = FakeRunner({"repos/owner/self/readme": [http(200, {"sha": "s", "encoding": "base64",
                                                                    "content": base64.b64encode(text.encode()).decode()})]})
        gh, _ = make(runner)
        self.assertEqual(gh.awesome_links("owner/self"), ["Foo/bar-baz", "x/y"])


def search_handler(totals, shared=0):
    """q 에 포함된 구간 문자열로 total_count 를 정해 돌려준다. totals: [(부분문자열, total)] 앞에서부터 매칭.
    id 는 (q, 순번)마다 결정적으로 붙이고, 쿼리마다 앞 shared 개는 모든 쿼리가 같은 레포(id 0..shared-1)를 돌려준다."""
    ids = {}

    def handle(path):
        qs = parse_qs(urlparse(path).query)
        q, page = qs["q"][0], int(qs.get("page", ["1"])[0])
        total = next(t for key, t in totals if key in q)
        start = (page - 1) * 100
        n = max(0, min(100, min(total, 1000) - start))
        items = []
        for i in range(start, start + n):
            gid = i if i < shared else ids.setdefault((q, i), 1_000_000 + len(ids))
            items.append({"id": gid, "full_name": f"o/r{gid}", "stargazers_count": 1})
        return http(200, {"total_count": total, "incomplete_results": False, "items": items})

    return handle


class SearchTest(unittest.TestCase):
    def test_1000건_이하면_페이지만_넘긴다(self):
        runner = FakeRunner(handler=search_handler([("", 250)]))
        gh, _ = make(runner)
        items = gh.search_repos("topic:kospi", min_stars=50)
        self.assertEqual(len(items), 250)
        self.assertEqual(len(runner.calls), 3)
        self.assertIn("stars%3A%3E%3D50", runner.calls[0])

    def test_1000건_초과면_스타_구간으로_나눈다(self):
        totals = [("stars:100..199", 400), ("stars:200..499", 300), ("stars:500..999", 200),
                  ("stars:1000..4999", 100), ("stars:>=5000", 10), ("", 1500)]
        runner = FakeRunner(handler=search_handler(totals))
        gh, _ = make(runner)
        items = gh.search_repos("topic:trading", min_stars=100)
        self.assertEqual(len(items), 1010)

    def test_구간도_1000건_초과면_생성연도로_한번_더_나눈다(self):
        totals = [("stars:>=100", 1200), ("created:2025", 600), ("created:2026", 600), ("created:", 0),
                  ("stars:100..199", 1200), ("stars:", 0)]
        runner = FakeRunner(handler=search_handler(totals))
        gh, _ = make(runner, this_year=2026)
        items = gh.search_repos("topic:x", min_stars=100)
        self.assertEqual(len(items), 1200)

    def test_구간_사이에_겹친_레포는_한번만_센다(self):
        totals = [("stars:100..199", 400), ("stars:200..499", 300), ("stars:500..999", 200),
                  ("stars:1000..4999", 100), ("stars:>=5000", 10), ("", 1500)]
        gh, _ = make(FakeRunner(handler=search_handler(totals, shared=5)))
        # 구간 5개가 모두 id 0..4 를 돌려준다 → 1010 - 4*5
        self.assertEqual(len(gh.search_repos("topic:trading", min_stars=100)), 990)

    def test_연도_구간도_1000건을_넘으면_잘린_쿼리를_기록한다(self):
        totals = [("stars:>=100", 1400), ("created:2026", 1400), ("created:", 0),
                  ("stars:100..199", 1400), ("stars:", 0)]
        gh, _ = make(FakeRunner(handler=search_handler(totals)), this_year=2026)
        self.assertEqual(len(gh.search_repos("topic:x", min_stars=100)), 1000)
        self.assertEqual(gh.truncated, [("topic:x stars:100..199 created:2026-01-01..2026-12-31", 1400)])

    def test_하한_50이면_50_99_구간부터_시작한다(self):
        self.assertEqual(github.star_slices(50)[0], "50..99")
        self.assertEqual(github.star_slices(100)[0], "100..199")


if __name__ == "__main__":
    unittest.main()
