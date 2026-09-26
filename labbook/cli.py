"""python3 -m labbook <명령> — 계획 §3.1 B 명령표."""
import argparse
import json
import sys
from pathlib import Path

from labbook import archive, collect, db, judge, metrics, report
from labbook.github import GitHub

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
CACHE = ROOT / ".cache"


def main(argv=None):
    p = argparse.ArgumentParser(prog="labbook")
    p.add_argument("--db", default=str(db.DEFAULT_PATH), help="작업 DB 경로 (기본: 레포 루트 labbook.db)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("collect", "refresh", "funnel"):
        sub.add_parser(name).add_argument("topic")
    for name in ("triage", "judge"):
        s = sub.add_parser(name)
        s.add_argument("topic")
        s.add_argument("--limit", type=int, help="처리할 레포 수 (나눠 돌리기)")
    sub.choices["judge"].add_argument("--gold", action="store_true", help="골드셋만 판정 — DB 에 쓰지 않음")
    s = sub.add_parser("top")
    s.add_argument("topic")
    s.add_argument("--by", choices=["P", "I", "momentum"], default="P")
    s.add_argument("--limit", type=int, default=20)
    s = sub.add_parser("select")
    s.add_argument("topic")
    s.add_argument("--add", nargs="*", default=[], metavar="OWNER/REPO")
    s.add_argument("--confirm", action="store_true", help="후보를 deep 단계로 확정")
    sub.add_parser("export")
    sub.add_parser("import")
    args = p.parse_args(argv)

    conn = db.connect(args.db)
    if args.cmd == "import":
        archive.import_(conn, DATA)
        print(f"import 완료: {DATA} → {args.db}")
        return
    db.migrate(conn)
    if args.cmd == "export":
        archive.export(conn, DATA)
        print(f"export 완료: {args.db} → {DATA}")
        return

    topic_dir = ROOT / "topics" / args.topic
    config = json.loads((topic_dir / "config.json").read_text())
    gh = GitHub(cache_dir=CACHE)
    today = db.utc_today()

    if args.cmd == "collect":
        out = collect.collect(conn, gh, config)
        for q, total in out["truncated"]:
            print(f"경고: 검색이 1000건에서 잘림 — {q} (전체 {total})", file=sys.stderr)
        detail = f"엔티티 {out['entities']}" + (f" · 잘린 검색 {len(out['truncated'])}" if out["truncated"] else "")
    elif args.cmd == "refresh":
        out = metrics.refresh(conn, gh, config)
        detail = f"조회 {out['fetched']} · 범위 내 {out['include']} · 제외 {out['exclude']}" + (
            f" · 조회 오류 {out['errors']}(이전 판정 유지)" if out["errors"] else "")
    elif args.cmd == "triage":
        detail = _processed(judge.triage(conn, gh, config, limit=args.limit))
    elif args.cmd == "judge" and args.gold:
        out = judge.gold(gh, config, topic_dir)
        rate = "전부 판정 실패" if out["overall"] is None else f"{out['overall']:.0%}"
        detail = f"골드 일치율 {rate} → reports/gold-{config['rubric_version']}.md"
    elif args.cmd == "judge":
        detail = _processed(judge.judge(conn, gh, config, topic_dir, limit=args.limit))
    elif args.cmd == "funnel":
        print(report.funnel(conn, args.topic, topic_dir, today))
        detail = f"reports/funnel-{today}.md"
    elif args.cmd == "top":
        _print_top(report.top(conn, args.topic, args.by, args.limit))
        return
    elif args.cmd == "select":
        try:
            picks = report.select(conn, args.topic, add=args.add, confirm=args.confirm)
        except ValueError as e:
            sys.exit(str(e))
        for pk in picks:
            print(f"{pk['slot']:<7} {pk['key']}")
        if not args.confirm:
            print("\n확정하려면 --confirm 을 붙여 다시 실행")
            return
        detail = f"심층분석 {len(picks)}개 확정"
    print(detail)
    _log(topic_dir, args.cmd, detail, today)


def _processed(n):
    return f"처리 {n}" if n else "대기 0건"


def _print_top(rows):
    print(f"{'repo':<45} {'cat':<18} {'★':>7} {'Δ30':>6}  P I N T  요약")
    for r in rows:
        name = r["key"].removeprefix("github:")
        print(f"{name:<45} {r['category'] or '':<18} {r['stars'] or 0:>7} {r['d30'] or 0:>6}  "
              f"{r['P']} {r['I']} {r['N']} {r['T']}  {(r['summary_ko'] or '').splitlines()[0] if r['summary_ko'] else ''}")


def _log(topic_dir, action, detail, today):
    with (topic_dir / "log.md").open("a") as f:
        f.write(f"## [{today}] {action} | {detail}\n")
