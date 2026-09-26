"""`gh api` subprocess 래퍼 — 인증은 gh auth 를 재사용한다 (새 환경변수·시크릿 없음).

실패 시 거동 (계획 §6-3):
- 403/429 레이트리밋: Retry-After 또는 리셋 시각까지 기다린 뒤 재시도
- 5xx·타임아웃·gh 실행 실패: 1·2·4초 지수 백오프로 3회 재시도
- 404: NotFound
"""
import base64
import datetime
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

SEARCH_CAP = 1000  # 검색 API 가 한 쿼리에 돌려주는 최대 건수
BACKOFFS = (1, 2, 4)
STAR_BOUNDS = (50, 100, 200, 500, 1000, 5000)
NOT_REPO_OWNERS = {"topics", "sponsors", "orgs", "features", "marketplace", "apps", "settings",
                   "about", "collections", "trending", "site", "login", "join", "explore", "search"}
LINK_RE = re.compile(r"github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)")


class GitHubError(Exception):
    pass


class NotFound(GitHubError):
    pass


def star_slices(min_stars):
    """min_stars 이상을 1000건 한도 아래로 나누는 stars: 구간 목록."""
    bounds = [b for b in STAR_BOUNDS if b > min_stars]
    edges = [min_stars] + bounds
    slices = [f"{lo}..{hi - 1}" for lo, hi in zip(edges, edges[1:])]
    return slices + [f">={edges[-1]}"]


def parse_response(stdout):
    head, _, body = stdout.replace("\r\n", "\n").partition("\n\n")
    lines = head.split("\n")
    status = int(lines[0].split()[1])
    headers = {}
    for line in lines[1:]:
        k, _, v = line.partition(":")
        headers[k.strip().lower()] = v.strip()
    return status, headers, (json.loads(body) if body.strip() else None)


def normalize_repo(r):
    return {
        "gh_id": r["id"],
        "full_name": r["full_name"],
        "url": r.get("html_url"),
        "description": r.get("description"),
        "topics": r.get("topics") or [],
        "language": r.get("language"),
        "stars": r.get("stargazers_count"),
        "forks": r.get("forks_count"),
        "watchers": r.get("subscribers_count"),  # 검색 결과에는 없다 — repo API 에서만 채워진다
        "open_issues": r.get("open_issues_count"),
        "pushed_at": r.get("pushed_at"),
        "created_at": r.get("created_at"),
        "archived": r.get("archived"),
        "fork": r.get("fork"),
    }


class GitHub:
    def __init__(self, runner=subprocess.run, sleep=time.sleep, clock=time.time, cache_dir=None,
                 timeout=30, this_year=None):
        self.runner = runner
        self.sleep = sleep
        self.clock = clock
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.this_year = this_year or datetime.date.today().year

    def get(self, path):
        failures = 0
        while True:
            try:
                proc = self.runner(["gh", "api", "-i", path], capture_output=True, text=True, timeout=self.timeout)
                status, headers, body = parse_response(proc.stdout) if proc.stdout else (0, {}, None)
            except subprocess.TimeoutExpired:
                status, headers, body = 0, {}, None
            if status == 200:
                self._wait_if_exhausted(headers)
                return body
            if status == 404:
                raise NotFound(path)
            wait = self._rate_limit_wait(status, headers)
            if wait is not None:
                self.sleep(wait)
                continue
            if status == 0 or status >= 500:
                if failures == len(BACKOFFS):
                    raise GitHubError(f"{path}: 재시도 {failures}회 후에도 실패 (HTTP {status})")
                self.sleep(BACKOFFS[failures])
                failures += 1
                continue
            raise GitHubError(f"{path}: HTTP {status} {body}")

    def _rate_limit_wait(self, status, headers):
        if status not in (403, 429):
            return None
        if "retry-after" in headers:
            return int(headers["retry-after"])
        if headers.get("x-ratelimit-remaining") == "0" and "x-ratelimit-reset" in headers:
            return max(1, int(headers["x-ratelimit-reset"]) - int(self.clock()) + 1)
        return None

    def _wait_if_exhausted(self, headers):
        if headers.get("x-ratelimit-remaining") == "0" and "x-ratelimit-reset" in headers:
            self.sleep(max(1, int(headers["x-ratelimit-reset"]) - int(self.clock()) + 1))

    def repo(self, full_name):
        return normalize_repo(self.get(f"repos/{full_name}"))

    def history(self, full_name):
        """stargazers/history page 1 — 최신 주 먼저, 주는 일요일 시작, 30주."""
        return self.get(f"repos/{full_name}/stargazers/history")

    def readme(self, full_name):
        cache = self.cache_dir / "readme" / (full_name.replace("/", "__") + ".json") if self.cache_dir else None
        if cache and cache.exists():
            hit = json.loads(cache.read_text())
            return hit["text"], hit["sha"]
        try:
            r = self.get(f"repos/{full_name}/readme")
            text, sha = base64.b64decode(r["content"]).decode("utf-8", errors="replace"), r["sha"]
        except NotFound:
            text, sha = "", None
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps({"text": text, "sha": sha}, ensure_ascii=False))
        return text, sha

    def top_issues(self, full_name, limit=30):
        rows = self.get(f"repos/{full_name}/issues?state=all&sort=comments&direction=desc&per_page=100")
        issues = [{"title": i["title"], "comments": i["comments"], "url": i["html_url"]}
                  for i in rows if "pull_request" not in i]
        return issues[:limit]

    def starred(self, user):
        out, page = [], 1
        while True:
            rows = self.get(f"users/{user}/starred?per_page=100&page={page}")
            out += [normalize_repo(r) for r in rows]
            if len(rows) < 100:
                return out
            page += 1

    def awesome_links(self, full_name):
        text, _ = self.readme(full_name)
        seen, out = set(), []
        for owner, name in LINK_RE.findall(text):
            name = name.removesuffix(".git").rstrip(".")
            ref = f"{owner}/{name}"
            if owner.lower() in NOT_REPO_OWNERS or ref.lower() == full_name.lower() or ref.lower() in seen:
                continue
            seen.add(ref.lower())
            out.append(ref)
        return out

    def search_repos(self, query, min_stars):
        """query 에 stars:>=min_stars 를 붙여 모두 가져온다. 1000건을 넘으면 스타 구간 → 생성 연도로 나눈다."""
        found = {}
        for item in self._search_split(query, min_stars):
            found[item["id"]] = normalize_repo(item)
        return list(found.values())

    def _search_split(self, query, min_stars):
        base = f"{query} stars:>={min_stars}"
        first = self._search_page(base, 1)
        if first["total_count"] <= SEARCH_CAP:
            yield from self._search_all(base, first)
            return
        for s in star_slices(min_stars):
            q = f"{query} stars:{s}"
            first = self._search_page(q, 1)
            if first["total_count"] <= SEARCH_CAP:
                yield from self._search_all(q, first)
                continue
            for year in range(2008, self.this_year + 1):
                yq = f"{q} created:{year}-01-01..{year}-12-31"
                yield from self._search_all(yq, self._search_page(yq, 1))

    def _search_page(self, q, page):
        return self.get(f"search/repositories?q={quote(q)}&per_page=100&page={page}")

    def _search_all(self, q, first):
        r, page = first, 1
        while True:
            yield from r["items"]
            if page * 100 >= min(r["total_count"], SEARCH_CAP):
                return
            page += 1
            r = self._search_page(q, page)
