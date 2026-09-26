"""`claude -p` 판정 호출 — 로컬 로그인 세션을 쓴다 (새 시크릿 없음).

격리 (계획 §3.1 B-2): 도구 없음, 세션 미저장, 레포 밖 cwd(.cache/llm/) — 판정 중 파일 수정·웹 조회 같은 부작용이 없고
레포의 CLAUDE.md·스킬·훅을 로드하지 않는다.
실패 시 거동 (계획 §6-6): 타임아웃 600s, 타임아웃·비정상 종료·스키마/검증 실패는 1회 재시도, 그래도 실패하면 LLMError.
"""
import json
import subprocess
from pathlib import Path

CWD = Path(__file__).parent.parent / ".cache" / "llm"
TIMEOUT = 600
ATTEMPTS = 2


class LLMError(Exception):
    pass


def run_claude(prompt, schema, model, *, validate=None, runner=subprocess.run, cwd=CWD, timeout=TIMEOUT):
    """구조화 출력과 실제 모델 ID 를 돌려준다. validate(out) 가 예외를 던지면 실패로 보고 재시도한다."""
    cwd.mkdir(parents=True, exist_ok=True)
    args = ["claude", "-p", "--tools", "", "--no-session-persistence", "--output-format", "json",
            "--json-schema", json.dumps(schema, ensure_ascii=False), "--model", model]
    reason = None
    for _ in range(ATTEMPTS):
        try:
            proc = runner(args, input=prompt, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        except subprocess.TimeoutExpired:
            reason = f"타임아웃 {timeout}s"
            continue
        if proc.returncode != 0:
            reason = f"종료 코드 {proc.returncode}: {proc.stderr.strip()[:200]}"
            continue
        try:
            body = json.loads(proc.stdout)
        except json.JSONDecodeError:
            reason = "JSON 이 아닌 출력"
            continue
        out = body.get("structured_output")
        if body.get("is_error") or out is None:
            reason = f"구조화 출력 없음: {str(body.get('result'))[:200]}"
            continue
        if validate:
            try:
                validate(out)
            except ValueError as e:
                reason = f"검증 실패: {e}"
                continue
        used = list(body.get("modelUsage") or {})
        return out, (used[0] if used else model)
    raise LLMError(reason)
