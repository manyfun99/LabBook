"""export/import — SQLite 작업 DB ↔ git 에 커밋하는 테이블별 JSONL (계획 §3.1 B·D, §6-8)."""
import json

from labbook import db

# 외래키 순서대로 (import 시 entity 가 먼저 들어가야 한다)
TABLES = ["entity", "screening", "snapshot", "judgment", "signal", "idea"]
ORDER = {
    "entity": "id",
    "screening": "topic, entity_id, stage",
    "snapshot": "taken_at, entity_id",  # 주간 refresh 의 diff 가 파일 뒤에 붙게
    "judgment": "id",
    "signal": "id",
    "idea": "id",
}


def export(conn, data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    for table in TABLES:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY {ORDER[table]}")
        text = "".join(json.dumps(dict(r), ensure_ascii=False) + "\n" for r in rows)
        (data_dir / f"{table}.jsonl").write_text(text)


def import_(conn, data_dir):
    """빈 DB 에 마이그레이션(뷰 포함)을 먼저 적용하고 행을 id 그대로 넣는다."""
    db.migrate(conn)
    if conn.execute("SELECT COUNT(*) FROM entity").fetchone()[0]:
        raise ValueError("비어 있지 않은 DB 에는 import 하지 않는다 — labbook.db 를 지우고 다시 실행")
    with conn:
        for table in TABLES:
            path = data_dir / f"{table}.jsonl"
            if not path.exists():
                continue
            for line in path.read_text().splitlines():
                row = json.loads(line)
                cols = ", ".join(row)
                conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({', '.join('?' * len(row))})", list(row.values()))
