"""refresh — 스냅샷·Δ7/30/90·의심 플래그·범위 컷 (계획 §3.1 B·C, §6-5)."""
import datetime
import json

from labbook.collect import upsert_entity
from labbook.db import utc_now
from labbook.github import NotFound, normalize_repo

SPIKE_SHARE = 0.7        # 3일에 30일 증가분의 70% 이상
SPIKE_MIN_D30 = 30       # 30일 증가가 이보다 작으면 급등을 보지 않는다 (소수 스타의 우연한 몰림)
LOW_WATCHERS = 0.015     # watchers/★
LOW_FORKS = 0.01         # forks/★ — 계획의 "레포 나이 대비 커밋 수" 대용 (커밋 수는 레포마다 API 한 번 더 필요)


def daily_counts(history, today):
    """stargazers/history(최신 주 먼저, 주는 일요일 시작, days[0]=일요일)를 최신일부터 일별로 펼친다. 오늘 이후는 뺀다."""
    out = []
    for w in history:
        start = datetime.datetime.fromtimestamp(w["week"], datetime.UTC).date()
        for i in reversed(range(len(w["days"]))):
            if start + datetime.timedelta(days=i) <= today:
                out.append(w["days"][i])
    return out


def momentum(days):
    return sum(days[:7]), sum(days[:30]), sum(days[:90])


def flags(repo, days30):
    out = []
    total = sum(days30)
    if total >= SPIKE_MIN_D30 and len(days30) >= 3:
        top3 = max(sum(days30[i:i + 3]) for i in range(len(days30) - 2))
        if top3 / total >= SPIKE_SHARE:
            out.append("spike")
    stars = repo.get("stars") or 0
    if stars and repo.get("watchers") is not None and repo["watchers"] / stars < LOW_WATCHERS:
        out.append("low_watchers")
    if stars and repo.get("forks") is not None and repo["forks"] / stars < LOW_FORKS:
        out.append("low_forks")
    return out


def scope(snap, sources, cfg):
    """범위 컷 → (decision, reason). 의심 플래그는 제외 사유가 아니다 (사람이 확인)."""
    stars, d30 = snap["stars"] or 0, snap["d30"] or 0
    if snap["archived"]:
        return "exclude", "archived"
    if "star" in sources:
        return "include", "starred"
    if stars >= cfg["famous_stars"]:
        return "include", "famous"
    if d30 >= cfg["rising_d30"] or (stars >= cfg["rising_min_stars"] and d30 / stars >= cfg["rising_ratio"]):
        return "include", "rising"
    if any(s.startswith("kr:") for s in sources) and stars >= cfg["kr_min_stars"]:
        return "include", "kr"
    return "exclude", "below_threshold"


def refresh(conn, gh, config, today=None):
    topic, cfg = config["topic"], config["scope"]
    today = today or datetime.datetime.now(datetime.UTC).date()
    rows = conn.execute(
        "SELECT e.id, e.gh_id, s.sources FROM screening s JOIN entity e ON e.id = s.entity_id "
        "WHERE s.topic = ? AND s.stage = 'identified' ORDER BY e.id", (topic,)).fetchall()
    counts = {"fetched": 0, "include": 0, "exclude": 0}
    for row in rows:
        with conn:  # 레포 단위로 커밋 — 중단 후 재실행하면 오늘 스냅샷이 있는 레포는 건너뛴다
            snap = conn.execute("SELECT * FROM snapshot WHERE entity_id = ? AND taken_at = ?",
                                (row["id"], today.isoformat())).fetchone()
            if snap is None:
                try:
                    snap = _take_snapshot(conn, gh, row, today)
                except NotFound:
                    _set_scope(conn, topic, row["id"], "exclude", "gone")
                    counts["exclude"] += 1
                    continue
                counts["fetched"] += 1
            decision, reason = scope(snap, json.loads(row["sources"]), cfg)
            _set_scope(conn, topic, row["id"], decision, reason)
            counts[decision] += 1
    return counts


def _take_snapshot(conn, gh, row, today):
    # gh_id 로 조회 — 이름 변경에 강하고, 삭제된 레포의 이름을 다른 레포가 쓰는 경우에도 엉뚱한 레포를 보지 않는다
    repo = normalize_repo(gh.get(f"repositories/{row['gh_id']}"))
    upsert_entity(conn, repo)
    try:
        history = gh.get(f"repositories/{row['gh_id']}/stargazers/history") or []
    except NotFound:
        history = []
    days = daily_counts(history, today)
    d7, d30, d90 = momentum(days)
    snap = {"entity_id": row["id"], "taken_at": today.isoformat(), "stars": repo["stars"], "forks": repo["forks"],
            "watchers": repo["watchers"], "open_issues": repo["open_issues"], "pushed_at": repo["pushed_at"],
            "created_at": repo["created_at"], "archived": int(bool(repo["archived"])),
            "d7": d7, "d30": d30, "d90": d90, "flags": json.dumps(flags(repo, days[:30]))}
    conn.execute(f"INSERT INTO snapshot ({', '.join(snap)}) VALUES ({', '.join('?' * len(snap))})", list(snap.values()))
    return snap


def _set_scope(conn, topic, entity_id, decision, reason):
    conn.execute(
        "INSERT INTO screening (topic, entity_id, stage, decision, reason, decided_at) VALUES (?, ?, 'scoped', ?, ?, ?) "
        "ON CONFLICT (topic, entity_id, stage) DO UPDATE SET decision = excluded.decision, reason = excluded.reason, "
        "decided_at = excluded.decided_at",
        (topic, entity_id, decision, reason, utc_now()))
