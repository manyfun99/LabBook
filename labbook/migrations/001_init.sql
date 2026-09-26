-- 조사 기록 공통 스키마 (계획 §3.1-D)
CREATE TABLE entity (
  id INTEGER PRIMARY KEY,
  kind TEXT NOT NULL,              -- 'github_repo'
  key TEXT NOT NULL UNIQUE,        -- 'github:owner/repo' (소문자, 최신 이름을 따라 갱신)
  gh_id INTEGER UNIQUE,            -- upsert 기준
  url TEXT,
  first_seen_at TEXT NOT NULL
);

CREATE TABLE screening (           -- PRISMA 흐름: 단계별 판정과 사유
  topic TEXT NOT NULL,
  entity_id INTEGER NOT NULL REFERENCES entity(id),
  stage TEXT NOT NULL,             -- identified | scoped | triaged | judged | deep
                                   -- scoped 는 refresh 마다 upsert, 나머지는 한 번만 씀 (error 만 재시도)
  decision TEXT NOT NULL,          -- include | exclude | unsure | error
  reason TEXT,
  sources TEXT,                    -- identified 단계의 출처 JSON 배열
  decided_at TEXT NOT NULL,
  PRIMARY KEY (topic, entity_id, stage)
);

CREATE TABLE snapshot (            -- 지표 이력 (레포당 하루 1행)
  entity_id INTEGER NOT NULL REFERENCES entity(id),
  taken_at TEXT NOT NULL,          -- UTC 'YYYY-MM-DD'
  stars INTEGER, forks INTEGER, watchers INTEGER, open_issues INTEGER,
  pushed_at TEXT, created_at TEXT, archived INTEGER,
  d7 INTEGER, d30 INTEGER, d90 INTEGER,
  flags TEXT,                      -- 의심 플래그 JSON 배열
  PRIMARY KEY (entity_id, taken_at)
);

CREATE TABLE judgment (
  id INTEGER PRIMARY KEY,
  topic TEXT NOT NULL,
  entity_id INTEGER NOT NULL REFERENCES entity(id),
  stage TEXT NOT NULL,             -- triage | full
  rubric_version TEXT NOT NULL,
  model TEXT NOT NULL,
  input_sha TEXT,                  -- 판정에 쓴 README 의 blob sha
  category TEXT,
  market TEXT,                     -- us | kr | cn | crypto | global | none
  summary_ko TEXT,
  scores TEXT,                     -- {"P":4,"I":3,"N":3,"T":2}
  evidence TEXT,                   -- {"P":"인용",…,"injection_suspect":false,"truncated":false}
  judged_at TEXT NOT NULL,
  UNIQUE (topic, entity_id, stage) -- 재판정 없음: 한 단계 한 번
);

CREATE TABLE signal (              -- 수요 신호: 주제를 넘어 GROUP BY 로 재활용
  id INTEGER PRIMARY KEY,
  topic TEXT NOT NULL,
  entity_id INTEGER REFERENCES entity(id),
  kind TEXT NOT NULL,              -- demand | pain | gap
  quote TEXT NOT NULL,
  source_url TEXT NOT NULL,
  weight INTEGER,
  found_at TEXT NOT NULL,
  UNIQUE (topic, source_url, quote)
);

CREATE TABLE idea (
  id INTEGER PRIMARY KEY,
  topic TEXT NOT NULL,
  title TEXT NOT NULL,
  jtbd TEXT, lens TEXT,
  signal_ids TEXT,                 -- JSON 배열
  scores TEXT,
  status TEXT NOT NULL,            -- draft | shortlist | validating | dropped
  reason TEXT, doc_path TEXT,
  created_at TEXT NOT NULL
);

-- 엔티티 + 최신 스냅샷 + 정밀(full) 판정
CREATE VIEW v_repo_latest AS
SELECT e.id AS entity_id, e.key, e.url, e.gh_id,
       j.topic, j.category, j.market, j.summary_ko,
       json_extract(j.scores, '$.P') AS P,
       json_extract(j.scores, '$.I') AS I,
       json_extract(j.scores, '$.N') AS N,
       json_extract(j.scores, '$.T') AS T,
       json_extract(j.evidence, '$.injection_suspect') AS injection_suspect,
       j.rubric_version, j.model, j.judged_at,
       s.taken_at, s.stars, s.forks, s.watchers, s.open_issues, s.pushed_at, s.archived,
       s.d7, s.d30, s.d90, s.flags
FROM entity e
JOIN judgment j ON j.entity_id = e.id AND j.stage = 'full'
LEFT JOIN snapshot s ON s.entity_id = e.id
  AND s.taken_at = (SELECT MAX(taken_at) FROM snapshot WHERE entity_id = e.id);
