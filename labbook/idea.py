"""브레인스토밍 아이디어 적재 — JSONL → idea 테이블 upsert (4차 계획 §3.4)."""
import json

from labbook import db

STATUS = ("draft", "shortlist", "validating", "dropped")
COLS = ("jtbd", "lens", "signal_ids", "scores", "status", "reason", "doc_path")
REQUIRED = ("signal_ids", "status")  # 새 행을 만들 때 반드시 있어야 하는 키
JSON_COLS = ("signal_ids", "scores")


def load(conn, topic, path):
    """파일 전체를 검증한 뒤 한 트랜잭션으로 쓴다 — 한 줄이라도 틀리면 아무것도 쓰지 않는다."""
    if not path.is_file():
        raise ValueError(f"아이디어 파일이 없다: {path}")
    known = {r[0] for r in conn.execute("SELECT id FROM signal WHERE topic = ?", (topic,))}
    seen, rows = set(), []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        where = f"{path}:{n}"
        try:
            row = json.loads(line)  # 줄 단위로 파싱해야 줄 번호를 붙일 수 있다
        except ValueError as e:
            raise ValueError(f"{where} JSON 이 아니다 — {e}") from None
        if not isinstance(row, dict):
            raise ValueError(f"{where} 객체가 아니다: {type(row).__name__}")
        title = row.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{where} title 이 비어 있다")
        if title in seen:
            raise ValueError(f"{where} 같은 파일 안에 title 이 두 번 나온다: {title}")
        cur = conn.execute("SELECT id FROM idea WHERE topic = ? AND title = ?", (topic, title)).fetchone()
        _check(where, row, known, is_new=cur is None)
        seen.add(title)
        rows.append((row, cur))

    added = updated = 0
    with conn:
        for row, cur in rows:
            cols = [c for c in COLS if c in row]  # 파일에 담긴 키만 건드린다 — 없는 필드를 null 로 덮지 않는다
            vals = [_value(c, row[c]) for c in cols]
            if cur:
                conn.execute(f"UPDATE idea SET {', '.join(c + ' = ?' for c in cols)} WHERE id = ?",
                             (*vals, cur["id"]))
                updated += 1
            else:
                conn.execute(f"INSERT INTO idea (topic, title, {', '.join(cols)}, created_at) "
                             f"VALUES (?, ?, {', '.join('?' * len(cols))}, ?)",
                             (topic, row["title"], *vals, db.utc_now()))
                added += 1
    total = conn.execute("SELECT COUNT(*) FROM idea WHERE topic = ?", (topic,)).fetchone()[0]
    return {"added": added, "updated": updated, "total": total}


def _check(where, row, known, is_new):
    if is_new:
        for key in REQUIRED:
            if key not in row:
                raise ValueError(f"{where} 새 아이디어에는 {key} 가 필요하다")
    elif not any(c in row for c in COLS):
        raise ValueError(f"{where} 갱신할 키가 없다 — {' · '.join(COLS)} 중 하나는 있어야 한다")
    if "status" in row and row["status"] not in STATUS:
        raise ValueError(f"{where} status 는 {' · '.join(STATUS)} 중 하나여야 한다: {row['status']!r}")
    if "signal_ids" in row:
        ids = row["signal_ids"]
        if not isinstance(ids, list) or any(isinstance(i, bool) or not isinstance(i, int) for i in ids):
            raise ValueError(f"{where} signal_ids 는 정수 배열이어야 한다: {ids!r}")
        missing = [i for i in ids if i not in known]
        if missing:
            raise ValueError(f"{where} 이 주제에 없는 signal id: {missing}")
    if "scores" in row and row["scores"] is not None and not isinstance(row["scores"], dict):
        raise ValueError(f"{where} scores 는 객체이거나 null 이어야 한다: {row['scores']!r}")
    if row.get("status") == "dropped" and not row.get("reason"):
        raise ValueError(f"{where} dropped 에는 reason 이 필요하다")
    if row.get("status") == "shortlist" and not row.get("doc_path"):
        raise ValueError(f"{where} shortlist 에는 doc_path 가 필요하다")


def _value(col, value):
    return json.dumps(value, ensure_ascii=False) if col in JSON_COLS and value is not None else value
