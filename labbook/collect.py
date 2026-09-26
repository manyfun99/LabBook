"""후보 수집 — 소스별로 레포를 모아 gh_id 기준으로 entity 를 upsert 하고 출처를 누적한다 (계획 §3.1 B·B-2)."""
import json
from collections import Counter

from labbook.db import utc_now
from labbook.github import NotFound


def collect(conn, gh, config):
    topic = config["topic"]
    found = []  # (repo, source)
    for q in config["topic_queries"] + config["keyword_queries"]:
        found += [(r, f"search:{q}") for r in gh.search_repos(q, min_stars=config["min_stars"])]
    for q in config["kr_queries"]:
        found += [(r, f"kr:{q}") for r in gh.search_repos(q, min_stars=config["kr_min_stars"])]
    for name in config["awesome_lists"]:
        for link in gh.awesome_links(name):
            try:
                r = gh.repo(link)  # 이름이 바뀐 링크는 리다이렉트로 최신 이름·gh_id 를 얻는다
            except NotFound:
                continue
            if (r.get("stars") or 0) >= config["min_stars"]:
                found.append((r, f"awesome:{name}"))
    found += [(r, "star") for r in gh.starred(config["starred_user"])]

    by_source = Counter()
    with conn:
        for r, source in found:
            entity_id = upsert_entity(conn, r)
            add_source(conn, topic, entity_id, source)
            by_source[source] += 1
    entities = conn.execute(
        "SELECT COUNT(*) FROM screening WHERE topic = ? AND stage = 'identified'", (topic,)).fetchone()[0]
    return {"entities": entities, "by_source": dict(by_source), "truncated": list(getattr(gh, "truncated", []))}


def upsert_entity(conn, r):
    key = f"github:{r['full_name'].lower()}"
    taken = conn.execute("SELECT id, gh_id FROM entity WHERE key = ?", (key,)).fetchone()
    if taken and taken["gh_id"] != r["gh_id"]:
        # 삭제된 레포의 이름을 다른 레포가 쓰는 경우 — 옛 엔티티의 key 를 비켜준다
        conn.execute("UPDATE entity SET key = ? WHERE id = ?", (f"{key}@{taken['gh_id']}", taken["id"]))
    row = conn.execute("SELECT id FROM entity WHERE gh_id = ?", (r["gh_id"],)).fetchone()
    if row:
        conn.execute("UPDATE entity SET key = ?, url = ? WHERE id = ?", (key, r.get("url"), row["id"]))
        return row["id"]
    cur = conn.execute(
        "INSERT INTO entity (kind, key, gh_id, url, first_seen_at) VALUES ('github_repo', ?, ?, ?, ?)",
        (key, r["gh_id"], r.get("url"), utc_now()))
    return cur.lastrowid


def add_source(conn, topic, entity_id, source):
    row = conn.execute(
        "SELECT sources FROM screening WHERE topic = ? AND entity_id = ? AND stage = 'identified'",
        (topic, entity_id)).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO screening (topic, entity_id, stage, decision, sources, decided_at) "
            "VALUES (?, ?, 'identified', 'include', ?, ?)",
            (topic, entity_id, json.dumps([source], ensure_ascii=False), utc_now()))
        return
    sources = sorted(set(json.loads(row["sources"])) | {source})
    conn.execute(
        "UPDATE screening SET sources = ? WHERE topic = ? AND entity_id = ? AND stage = 'identified'",
        (json.dumps(sources, ensure_ascii=False), topic, entity_id))
