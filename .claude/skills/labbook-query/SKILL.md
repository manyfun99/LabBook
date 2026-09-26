---
name: labbook-query
description: LabBook 에 쌓인 조사 기록(SQLite)을 SQL 로 조회해 답한다. "지난 조사에서", "기록에서 찾아줘", "어떤 레포가", "신호가 많이 모인" 처럼 과거 조사 결과를 묻는 질문에 쓴다.
---

# 조사 기록 조회

작업 DB 는 레포 루트 `labbook.db` 다. 없으면 `python3 -m labbook import` 로 `data/*.jsonl` 에서 재구성한다.
`sqlite3 labbook.db "<SQL>"` 로 직접 질의한다. 답에는 실행한 SQL 과 결과 행을 근거로 붙인다.

## 스키마 (요지 — 원문 `labbook/migrations/`)

| 테이블 | 내용 |
|---|---|
| `entity` | 조사 대상. 주제 공통. `key`(`github:owner/repo`, 최신 이름), `gh_id`(이름 변경에도 불변) |
| `screening` | 주제·엔티티·단계별 판정. 단계는 `identified`(`sources` 출처 JSON) → `scoped` → `triaged` → `judged` → `deep` 순이다. `decision`(include·exclude·unsure·error)과 `reason`(제외 사유)을 담는다 |
| `snapshot` | 지표 이력, 레포당 하루 1행. `stars`, `d7`/`d30`/`d90`(최근 N일 스타 증가), `flags`(의심 플래그 JSON) |
| `judgment` | LLM 판정. `stage`(triage·full), `category`, `market`, `summary_ko`, `scores`(`{"P","I","N","T"}`), `evidence`(축별 인용·`injection_suspect`·`truncated`·`binary_link`), `rubric_version`, `model` |
| `signal` | 수요 신호. `kind`(demand·pain·gap), `quote`(원문), `source_url`, `weight`(반응 수) |
| `idea` | 아이디어. `jtbd`, `lens`, `signal_ids`(JSON 배열), `scores`, `status`(draft·shortlist·validating·dropped) |
| `v_repo_latest` (뷰) | 엔티티 + 최신 스냅샷 + full 판정. `P`/`I`/`N`/`T` 컬럼으로 풀려 있다 |

축 의미: P 개인 활용도 · I 인디 기회 · N 차용 가치 · T 성과 주장 신뢰도 (루브릭 `topics/<주제>/rubric-v1.md`).

## 대표 쿼리

```sql
-- 1. 심층분석에서 한국 시장 지원 요청 신호가 나온 레포
SELECT DISTINCT e.key, s.quote, s.source_url FROM signal s JOIN entity e ON e.id = s.entity_id
WHERE s.topic = 'stock-oss'
  AND (s.quote LIKE '%Korea%' OR s.quote LIKE '%한국%' OR s.quote LIKE '%KRX%' OR s.quote LIKE '%KOSPI%');

-- 2. 지난 refresh 대비 Δ30 이 두 배 이상이 된 레포
WITH ranked AS (
  SELECT entity_id, taken_at, d30, ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY taken_at DESC) AS rn FROM snapshot)
SELECT e.key, prev.d30 AS before, cur.d30 AS now FROM ranked cur
JOIN ranked prev ON prev.entity_id = cur.entity_id AND prev.rn = 2
JOIN entity e ON e.id = cur.entity_id
WHERE cur.rn = 1 AND prev.d30 > 0 AND cur.d30 >= 2 * prev.d30 ORDER BY cur.d30 DESC;

-- 3. 개인 활용도·신뢰도가 모두 높은 레포
SELECT key, P, T, summary_ko FROM v_repo_latest WHERE topic = 'stock-oss' AND P >= 4 AND T >= 4 ORDER BY P DESC, T DESC;

-- 4. demand 신호가 가장 많이 모인 JTBD
SELECT i.jtbd, COUNT(DISTINCT s.id) AS demand FROM idea i, json_each(i.signal_ids) j
JOIN signal s ON s.id = j.value AND s.kind = 'demand'
WHERE i.topic = 'stock-oss' GROUP BY i.jtbd ORDER BY demand DESC;

-- 5. 1단에서 "금융 무관"으로 뺀 레포 중 ★ 상위 10개 (제외 판정 점검용)
SELECT e.key, sn.stars FROM screening sc JOIN entity e ON e.id = sc.entity_id
JOIN snapshot sn ON sn.entity_id = e.id AND sn.taken_at = (SELECT MAX(taken_at) FROM snapshot WHERE entity_id = e.id)
WHERE sc.topic = 'stock-oss' AND sc.stage = 'triaged' AND sc.reason = 'unrelated' ORDER BY sn.stars DESC LIMIT 10;

-- 주제를 가로지르는 반복 신호 (주제가 둘 이상 쌓인 뒤)
SELECT e.key, COUNT(DISTINCT s.topic) AS topics, COUNT(*) AS signals FROM signal s JOIN entity e ON e.id = s.entity_id
GROUP BY e.id HAVING topics > 1 ORDER BY signals DESC;
```

## 출력

- 답 + 근거(SQL·결과 행). 결과가 없으면 없다고 답하고, 어느 단계까지 기록이 쌓였는지(`screening` 단계별 건수)를 함께 알린다.
- 다시 쓸 만한 답(교차 인사이트, 비교표)은 `topics/<주제>/notes/` 에 노트로 적고 `index.md` 에 한 줄을 추가한다.
