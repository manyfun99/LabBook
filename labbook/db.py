"""SQLite 연결과 마이그레이션 적용."""
import datetime
import sqlite3
from pathlib import Path

MIGRATIONS = Path(__file__).parent / "migrations"
DEFAULT_PATH = Path(__file__).parent.parent / "labbook.db"


def connect(path=DEFAULT_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn):
    """아직 적용하지 않은 migrations/NNN_*.sql 을 순번대로 적용하고, 적용한 번호 목록을 돌려준다."""
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
    done = {r[0] for r in conn.execute("SELECT version FROM schema_version")}
    applied = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        version = int(path.name.split("_", 1)[0])
        if version in done:
            continue
        # 레거시 트랜잭션 모드는 DDL 앞에 BEGIN 을 걸지 않으므로 명시적으로 묶는다 — 실패 시 일부만 적용되지 않게
        conn.execute("BEGIN")
        try:
            for stmt in _statements(path.read_text()):
                conn.execute(stmt)
            conn.execute("INSERT INTO schema_version VALUES (?, ?)", (version, utc_now()))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        applied.append(version)
    return applied


def _statements(script):
    """세미콜론으로 끝나는 완결 SQL 문 단위로 나눈다 (한 트랜잭션 안에서 실행하기 위해)."""
    buf, out = "", []
    for line in script.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            if buf.strip():
                out.append(buf)
            buf = ""
    return out


def utc_now():
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def utc_today():
    return datetime.datetime.now(datetime.UTC).date().isoformat()
