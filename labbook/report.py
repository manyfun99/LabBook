"""funnel(퍼널 리포트)·top(축별 상위)·select(심층분석 후보) — 계획 §3.1 A·B, §6-8."""
import json
from collections import Counter

from labbook.db import utc_now

ORDER = {
    "P": "P DESC, T DESC, stars DESC",
    "I": "I DESC, T DESC, stars DESC",
    "momentum": "d30 DESC, stars DESC",
    "kr": "MAX(P, I) DESC, T DESC, stars DESC",
}
SLOTS = [("P", 5, ""), ("I", 5, ""), ("rising", 3, ""), ("kr", 2, "AND market = 'kr'")]
OUT_OF_SCOPE = ("AND entity_id NOT IN (SELECT entity_id FROM screening "
                "WHERE topic = :topic AND stage = 'scoped' AND decision = 'exclude')")
SOURCE_LABELS = [("search:", "검색"), ("awesome:", "awesome"), ("star", "스타"), ("kr:", "한국")]


def top(conn, topic, by, limit=20):
    return [dict(r) for r in conn.execute(
        f"SELECT * FROM v_repo_latest WHERE topic = :topic {OUT_OF_SCOPE} ORDER BY {ORDER[by]} LIMIT :limit",
        {"topic": topic, "limit": limit})]


def select(conn, topic, add=(), confirm=False):
    """P 상위 5 → I 상위 5 → 라이징(d30) 상위 3 → 한국 상위 2. 앞에서 뽑힌 레포는 건너뛰어 다음 순위로 채운다."""
    picks, taken = [], set()
    for slot, n, where in SLOTS:
        order = ORDER["momentum" if slot == "rising" else slot]
        rows = conn.execute(f"SELECT entity_id, key FROM v_repo_latest WHERE topic = :topic {where} {OUT_OF_SCOPE} "
                            f"ORDER BY {order}", {"topic": topic})
        got = 0
        for r in rows:
            if got == n:
                break
            if r["entity_id"] in taken:
                continue
            picks.append({"slot": slot, "key": r["key"], "entity_id": r["entity_id"]})
            taken.add(r["entity_id"])
            got += 1
    for name in add:
        row = conn.execute("SELECT id, key FROM entity WHERE key = ?", (f"github:{name.lower()}",)).fetchone()
        if row is None:
            raise ValueError(f"수집되지 않은 레포: {name}")
        if row["id"] not in taken:
            picks.append({"slot": "user", "key": row["key"], "entity_id": row["id"]})
            taken.add(row["id"])
    if confirm:
        with conn:
            for p in picks:
                conn.execute(
                    "INSERT INTO screening (topic, entity_id, stage, decision, reason, decided_at) "
                    "VALUES (?, ?, 'deep', 'include', ?, ?) ON CONFLICT (topic, entity_id, stage) DO NOTHING",
                    (topic, p["entity_id"], p["slot"], utc_now()))
    return picks


def funnel(conn, topic, topic_dir, date):
    def stage(name):
        return conn.execute("SELECT entity_id, decision, reason, sources FROM screening WHERE topic = ? AND stage = ?",
                            (topic, name)).fetchall()

    identified = stage("identified")
    per_entity = [json.loads(r["sources"]) for r in identified]
    by_label = {label: sum(any(s.startswith(p) for s in srcs) for srcs in per_entity) for p, label in SOURCE_LABELS}
    scoped = stage("scoped")
    included = {r["entity_id"] for r in scoped if r["decision"] == "include"}
    excluded = Counter(r["reason"] for r in scoped if r["decision"] == "exclude")
    triaged = stage("triaged")
    tri_ex = Counter(r["reason"] for r in triaged if r["decision"] == "exclude")
    tri_other = Counter(r["decision"] for r in triaged if r["decision"] in ("unsure", "error"))
    judged = [r for r in stage("judged") if r["decision"] == "include"]
    judged_err = sum(1 for r in stage("judged") if r["decision"] == "error")
    cats = Counter(r[0] for r in conn.execute(
        "SELECT category FROM judgment WHERE topic = ? AND stage = 'full'", (topic,)))
    deep = [r for r in stage("deep") if r["decision"] == "include"]

    lines = [
        f"# 퍼널 리포트 — {topic} ({date})", "", "```",
        f"식별 {len(identified)} (" + " · ".join(f"{label} {by_label[label]}" for _, label in SOURCE_LABELS)
        + f", 중복 제거 전 {sum(map(len, per_entity))})",
        f" └ 범위 컷 제외 {sum(excluded.values())} ({_fmt(excluded)})",
        f"범위 내 {len(included)} (의심 표시 {_suspects(conn, topic, included)} — 제외하지 않고 사람이 확인)",
        f" └ 1단 제외 {sum(tri_ex.values())} ({_fmt(tri_ex)})"
        + (f" · 보류 {tri_other['unsure']}(2단으로 넘김)" if tri_other["unsure"] else "")
        + (f" · 오류 {tri_other['error']}(재시도 대기)" if tri_other["error"] else ""),
        f"정밀 판정 {len(judged)}   카테고리: {_fmt(cats)}" + (f" · 오류 {judged_err}(재시도 대기)" if judged_err else ""),
        f"심층분석 {len(deep)}", "```", "",
    ]
    text = "\n".join(lines)
    path = topic_dir / "reports" / f"funnel-{date}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return text


def _suspects(conn, topic, included):
    """범위 내 레포 중 최신 스냅샷 플래그나 판정 증거(인젝션·바이너리 링크)가 선 것."""
    flagged = {r[0] for r in conn.execute(
        "SELECT s.entity_id FROM snapshot s "
        "WHERE s.taken_at = (SELECT MAX(taken_at) FROM snapshot WHERE entity_id = s.entity_id) "
        "AND json_array_length(COALESCE(s.flags, '[]')) > 0")}
    flagged |= {r[0] for r in conn.execute(
        "SELECT entity_id FROM judgment WHERE topic = ? "
        "AND (json_extract(evidence, '$.injection_suspect') OR json_extract(evidence, '$.binary_link'))", (topic,))}
    return len(flagged & included)


def _fmt(counter):
    return " · ".join(f"{k} {v}" for k, v in counter.most_common()) or "-"
