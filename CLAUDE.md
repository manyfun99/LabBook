# LabBook

조사·아카이빙 레포. 주제를 전수조사해 결과를 구조화해 기록하고(SQLite 등), 쌓인 기록을 다시 조회해 인사이트(인디해커 아이템 구상, 서비스 벤치마크 등)를 얻는다.
예: GitHub 의 금융·주식투자 오픈소스 전수조사 → 요약 기록 → 아이템 구상 / 주식투자 참고 서비스 벤치마크.

하네스(plan-* 스킬)는 indie-forge 플러그인 `forge` 로 받는다 (`.claude/settings.json`). 스킬 수정은 indie-forge 레포에서 한다.

## 구성

| 경로 | 역할 |
|------|------|
| `docs/ai-discussions/` | 계획·결정 기록 |
| `labbook/` | 수집·판정 도구 (Python 표준 라이브러리). `python3 -m labbook <명령>` — collect·refresh·triage·judge·funnel·top·select·export·import. 스키마는 `labbook/migrations/` |
| `topics/<주제>/` | 주제별 설정(`config.json`)·루브릭·골드셋·노트·아이디어·리포트·`index.md`·`log.md` |
| `data/*.jsonl` | 조사 기록 이력 정본 (git 커밋). 작업 DB `labbook.db` 는 gitignore — `python3 -m labbook import` 로 재구성 |
| `.claude/skills/labbook-*` | 이 레포의 조사 스킬 (심층분석·브레인스토밍·기록 조회) — 하네스(plan-*)와 별개로 이 레포에서 수정한다 |

## 빌드/테스트

plan-execute·plan-verify 가 이 표를 참조한다.

| 대상 | 빌드 | 테스트 (영향 범위) | 테스트 (전체) |
|------|------|------|------|
| `labbook/` | - | `python3 -m unittest tests.test_<모듈>` | `python3 -m unittest discover tests` |

## 개발 워크플로

- 기능 단위 작업: `/forge:plan-gen` → `/forge:plan-check` → `/forge:plan-execute` → (내부에서 `/forge:plan-verify`)
- 작은 수정(오타·한두 줄 버그·설정값)은 파이프라인 없이 바로 처리한다
- 계획·결정 기록: `docs/ai-discussions/YYYYMMDD-주제.md` — 작업 전에 관련 결정이 있는지 먼저 확인한다 (요청에 언급되지 않았더라도)
- 하네스 갱신: `claude plugin marketplace update indie-forge`
- 하네스(plan-*) 마찰은 계획 문서 7.2 의존성에 적고, 모이면 indie-forge 에서 별도 계획으로 반영한다

## 언어 규칙

- 모든 응답과 출력은 **한글**로 작성할 것
- 코드 식별자, 기술 용어, 명령어 등은 원문 그대로 유지
- PR 본문, 코드 주석, 계획 문서도 한글로 작성
- 파일로 쓰는 문서(계획·경위·PR 본문)는 과제에 맞는 분량으로 쓴다 — 내용은 빠짐없이, 채우기용 절·중복 요약·상투구 없이

## 컨벤션

- 커밋 메시지: conventional commits 형식 (feat:, fix:, chore:, docs:, refactor:, test:), 본문은 한글
- 브랜치 네이밍: feature/xxx, fix/xxx, hotfix/xxx

## 행동 규칙

### 1. 가정 드러내기
- 작업에 깔린 가정은 밝히고 진행한다. 사소한 판단은 스스로 내린다.
- 질문은 해석에 따라 결과물이 실질적으로 달라질 때만 한다. 그때는 해석들을 나란히 놓고 권장안을 붙인다.

### 2. 단순함 우선
- 요청받지 않은 기능을 추가하지 말 것.
- 한 번만 쓰이는 코드에 추상화를 만들지 말 것.
- 요청이 잘못됐거나 더 나은 방법이 보이면 한 문장으로 말하고, 요청대로 진행한다 — 조용히 범위를 줄이거나 넓히거나 바꾸지 않는다.

### 3. 외과적 변경
- 인접 코드, 주석, 포맷팅을 "개선"하지 말 것.
- 본인의 변경으로 사용되지 않게 된 import/변수/함수는 제거할 것.
- 기존에 존재하던 죽은 코드는 요청받지 않는 한 제거하지 말 것.

### 4. 목표 지향 실행
- 작업을 시작할 때 검증 가능한 성공 기준으로 바꿔 둔다.
- 맡은 작업은 끝까지 마치되, 요청 범위를 분명히 넘는 행동은 하지 않는다.
