import json
import unittest

from labbook import collect, db
from labbook.github import NotFound


def repo(gh_id, full_name, stars=500):
    return {"gh_id": gh_id, "full_name": full_name, "url": f"https://github.com/{full_name}", "stars": stars}


class FakeGitHub:
    def __init__(self, search=None, repos=None, awesome=None, starred=None):
        self.search = search or {}
        self.repos = repos or {}
        self.awesome = awesome or {}
        self.star_list = starred or []
        self.search_calls = []
        self.truncated = []  # 실제 GitHub 처럼 항상 있다

    def search_repos(self, query, min_stars):
        self.search_calls.append((query, min_stars))
        return self.search.get(query, [])

    def repo(self, full_name):
        if full_name not in self.repos:
            raise NotFound(full_name)
        return self.repos[full_name]

    def awesome_links(self, full_name):
        return self.awesome.get(full_name, [])

    def starred(self, user):
        return self.star_list


CONFIG = {"topic": "t", "min_stars": 100, "kr_min_stars": 50,
          "topic_queries": ["topic:a"], "keyword_queries": ["kw"], "kr_queries": ["kr"],
          "awesome_lists": ["x/awesome"], "starred_user": "me"}


class CollectTest(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.addCleanup(self.conn.close)
        db.migrate(self.conn)

    def entities(self):
        return {r["gh_id"]: dict(r) for r in self.conn.execute("SELECT * FROM entity")}

    def sources(self, gh_id):
        row = self.conn.execute(
            "SELECT s.sources FROM screening s JOIN entity e ON e.id = s.entity_id "
            "WHERE e.gh_id = ? AND s.stage = 'identified'", (gh_id,)).fetchone()
        return json.loads(row["sources"])

    def test_여러_소스에서_나온_같은_레포는_엔티티_하나에_출처가_누적된다(self):
        gh = FakeGitHub(search={"topic:a": [repo(1, "A/B")], "kw": [repo(1, "A/B")], "kr": [repo(2, "k/r", 60)]},
                        repos={"a/b": repo(1, "A/B")}, awesome={"x/awesome": ["a/b"]}, starred=[repo(1, "A/B")])
        collect.collect(self.conn, gh, CONFIG)
        ents = self.entities()
        self.assertEqual(set(ents), {1, 2})
        self.assertEqual(ents[1]["key"], "github:a/b")
        self.assertEqual(self.sources(1), ["awesome:x/awesome", "search:kw", "search:topic:a", "star"])
        self.assertEqual(self.sources(2), ["kr:kr"])

    def test_검색_하한은_일반_100_한국_50(self):
        gh = FakeGitHub()
        collect.collect(self.conn, gh, CONFIG)
        self.assertEqual(sorted(gh.search_calls), [("kr", 50), ("kw", 100), ("topic:a", 100)])

    def test_이름이_바뀐_레포는_gh_id로_합치고_key를_갱신한다(self):
        collect.collect(self.conn, FakeGitHub(search={"topic:a": [repo(1, "old/name")]}), CONFIG)
        collect.collect(self.conn, FakeGitHub(search={"kw": [repo(1, "new/name")]}), CONFIG)
        ents = self.entities()
        self.assertEqual(len(ents), 1)
        self.assertEqual(ents[1]["key"], "github:new/name")
        self.assertEqual(ents[1]["url"], "https://github.com/new/name")
        self.assertEqual(self.sources(1), ["search:kw", "search:topic:a"])

    def test_awesome_링크가_404면_엔티티를_만들지_않는다(self):
        gh = FakeGitHub(awesome={"x/awesome": ["gone/repo"]})
        collect.collect(self.conn, gh, CONFIG)
        self.assertEqual(self.entities(), {})

    def test_awesome_링크는_하한_미만_스타면_뺀다(self):
        gh = FakeGitHub(repos={"s/mall": repo(3, "s/mall", 99)}, awesome={"x/awesome": ["s/mall"]})
        collect.collect(self.conn, gh, CONFIG)
        self.assertEqual(self.entities(), {})

    def test_사용자_스타는_스타_수와_무관하게_넣는다(self):
        collect.collect(self.conn, FakeGitHub(starred=[repo(4, "me/tiny", 3)]), CONFIG)
        self.assertEqual(self.sources(4), ["star"])

    def test_재실행해도_출처가_중복되지_않고_첫_발견일이_유지된다(self):
        gh = FakeGitHub(search={"topic:a": [repo(1, "A/B")]})
        collect.collect(self.conn, gh, CONFIG)
        first = self.entities()[1]["first_seen_at"]
        collect.collect(self.conn, gh, CONFIG)
        self.assertEqual(self.sources(1), ["search:topic:a"])
        self.assertEqual(self.entities()[1]["first_seen_at"], first)

    def test_삭제된_레포의_이름을_다른_레포가_쓰면_옛_엔티티_key를_비켜준다(self):
        collect.collect(self.conn, FakeGitHub(search={"topic:a": [repo(1, "a/b")]}), CONFIG)
        collect.collect(self.conn, FakeGitHub(search={"topic:a": [repo(9, "a/b")]}), CONFIG)
        ents = self.entities()
        self.assertEqual(ents[9]["key"], "github:a/b")
        self.assertEqual(ents[1]["key"], "github:a/b@1")

    def test_요약을_돌려준다(self):
        gh = FakeGitHub(search={"topic:a": [repo(1, "A/B")], "kw": [repo(2, "c/d")]})
        summary = collect.collect(self.conn, gh, CONFIG)
        self.assertEqual(summary["entities"], 2)
        self.assertEqual(summary["by_source"]["search:topic:a"], 1)

    def test_잘린_검색을_요약에_넘긴다(self):
        gh = FakeGitHub()
        gh.truncated = [("kw stars:100..199 created:2026-01-01..2026-12-31", 1400)]
        self.assertEqual(collect.collect(self.conn, gh, CONFIG)["truncated"], gh.truncated)
        self.assertEqual(collect.collect(self.conn, FakeGitHub(), CONFIG)["truncated"], [])


if __name__ == "__main__":
    unittest.main()
