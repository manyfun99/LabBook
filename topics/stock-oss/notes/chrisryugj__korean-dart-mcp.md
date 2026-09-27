---
entity: github:chrisryugj/korean-dart-mcp
gh_id: 1213849297
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [data-mcp, dart, disclosure, xbrl, mcp-server, kr]
---
## 무엇·어떻게

금감원 OpenDART 를 감싼 TypeScript MCP 서버 겸 CLI 다. 라이선스 MIT, npm 패키지 `korean-dart-mcp`. 규모는 ★103, 포크 19, watchers 0 이다. 2026-04-17 에 만들어졌고 clone HEAD 는 `b75339b`(2026-09-12)다. 구청 AI 동호회 소속 개인이 만들었고, 자매 프로젝트로 `korean-law-mcp`(법제처)가 있다. main 과 태그는 GitHub Actions 로 정부 GitLab(`gitlab.aigov.go.kr`)에 미러링된다. 코드는 `src/` 아래 약 5,900줄이다.

- 구조: `src/index.ts` 가 stdio MCP 서버이고, `src/cli.ts` 는 `korean-dart` CLI, `src/setup.ts` 는 클라이언트 설정 파일을 자동으로 고치는 마법사다. README 는 "15개 도구"라고 쓰지만 `src/tools/index.ts` 레지스트리에는 18개가 등록돼 있다(v0.10.0 에서 `get_securities_filing`·`get_financial_indicators`·`dart_raw` 가 추가됨). 도구는 네 층으로 나뉜다.
  - 기본 조회 7개: `resolve_corp_code`, `search_disclosures`(22개 프리셋, 90일 자동분할, 페이지 병렬), `get_financials`, `download_document`(DART XML → 마크다운), `get_xbrl`(presentation/calculation linkbase 파싱과 합산 검증), `get_periodic_report`(29 섹션 enum) 등
  - 합성 래퍼 4개: 지배구조, 임원 보수, 5%룰과 임원 지분, 주요사항 36종 timeline
  - "애널리스트 프레임" 3개: `insider_signal`, `disclosure_anomaly`, `buffett_quality_snapshot`
  - 원문: `get_attachments`. DART 뷰어 HTML 을 스크래핑해 HWP/PDF 첨부를 받고, 자작 엔진 `kordoc` 으로 마크다운을 만든다.
  - 그 밖: `dart_raw` 는 임의의 OpenDART op 를 그대로 부르는 패스스루다.
- 분석 도구의 실체는 LLM 이 아니라 규칙 기반 집계다.
  - `insider_signal`: `elestock.json` 의 증감 수량 부호만 보고 매수·매도를 나눈다. 고유 매수자 수가 매도자의 2배를 넘으면 `strong_buy_cluster` 를 붙인다.
  - `disclosure_anomaly`: 가산점을 더해 100점에서 자른다. 정정공시 비율 20% 초과 +30, 감사인 교체 +20~30, 비적정 의견 +40, 자본 스트레스 공시 3건 이상 +10 이다. 70점 이상 `red_flag`, 40점 이상 `warning`, 15점 이상 `watch` 다.
  - `buffett_quality_snapshot`: ROE ≥15%, 부채비율 ≤100%, 매출 CAGR ≥5%, 순이익 CAGR ≥5% 네 가지 체크리스트다.
- 데이터 소스:
  - `opendart.fss.or.kr/api`: 키가 필요하고 무료이며 일 20,000건까지 쓸 수 있다. 첫 기동 때 전체 기업 덤프 약 11.6만 건을 `~/.korean-dart-mcp/corp_code.sqlite` 에 FTS 로 적재하고, TTL 은 24시간이다.
  - `dart.fss.or.kr` 뷰어 스크래핑(첨부): 도구 설명문 스스로 "DART robots.txt 가 크롤러에 Disallow 로 지정한 뷰어 경로"라고 밝히고, 대량 수집에는 쓰지 말라고 적어 두었다.
- LLM: 서버 안에서는 쓰지 않는다. 해석은 MCP 클라이언트(Claude 등)의 LLM 이 맡는다.
- 1회 실행 비용: 서버 쪽은 0원이다. 사용자 쪽 비용은 LLM 클라이언트 구독이다(README 는 Claude Pro $20/월과 대용량 PDF 용 상위 플랜을 "진입 장벽"으로 적는다). 사업보고서 PDF 한 건이 약 92만 자 마크다운이 되므로 컨텍스트 비용이 크다.
- 전송 방식은 stdio 뿐이다. HTTP/원격 transport 가 없다.

OpenDartReader 노트와 비교하면: 엔드포인트 매핑은 OpenDartReader·dart-fss 를 따랐다고 README 가 밝힌다. 그 위에 XBRL linkbase 파싱, 첨부 마크다운화, 규칙 기반 시그널 층을 얹은 것이 차별점이다. 이 레포는 pandas 사용자가 아니라 LLM 클라이언트를 겨냥한다.

## 성과 주장의 신뢰도

1. 주장 목록: 수익률·적중률·샤프·초과수익 주장은 없다. README·README-EN·CHANGELOG 에 있는 것은 도구 출력 예시("실측값")와 성능 수치다.
   - 도구 출력 예시: 삼성전자 "매수 2,429 vs 매도 43 → `strong_buy_cluster` (경영진이 자기 돈으로 사고 있음)", 카카오 회계 리스크 "40점 `warning`", "최근 30일 자기주식 취득 **59건**"
   - 성능 수치: "PDF 2.2MB → 마크다운 92만 자로 변환 (3.7초)", "6MB XBRL → ~30-60KB", CHANGELOG 의 kordoc 수치 "HWPX 텍스트 재현율 99.998%, 표 구조 정확일치 100%", "환각률(phantom) 0.006%"
   - 해석 주장: "자기주식 취득 = 주가 부양 시그널 / 유상증자·CB = 희석 경계", "**종목 고를 때 감각 의존 대신 수치 근거**"
   - 재현성 주장: "전부 `scripts/showcase-v0_9_1.mjs` 로 재현 가능 (12/12 PASS)"
2. 면책 문구: README "이 도구는 **리서치 보조용**. 투자 판단은 본인이.", `insider_signal` 코드 주석 "투자 권유가 아니라", `disclosure_anomaly` 설명 "(직접 권고하지 않음)".
3. 검증 수단: 백테스트가 없으므로 기간·수수료·look-ahead·컷오프 이후 항목은 해당 없음이다. 대신 시그널의 의미를 검증한 장치가 없다.
   - "12/12 PASS" 는 `showcase` 스크립트가 예외 없이 끝났다는 뜻이다. 결과가 맞는지는 대조하지 않는다(코드 읽기로 확인, 실행은 안 함).
   - `insider_signal` 은 변동 사유를 구분하지 않는다. 도구 응답의 `note` 도 "DART 는 변동사유(장내매수/증여/유상증자 등)를 구분하지 않음" 이라고 스스로 적는다. 그런데 README 는 같은 출력을 "경영진이 자기 돈으로 사고 있음" 으로 해석한다. 삼성전자의 "고유 매수자 1,047명" 은 주식보상 지급분이 섞인 값일 가능성이 높다(추정). 장내매수 시그널로 읽으면 틀린다.
   - `search_disclosures` 의 `treasury_buy` 프리셋 정규식은 `/자기주식.*취득/` 이다. 그래서 README 예시의 "최신 5건" 가운데 4건이 "자기주식취득신탁계약해지결정"(취득의 반대 방향)인데도 "자기주식 취득 결정" 59건에 함께 세어졌다.
   - kordoc 정확도 수치는 이 레포 밖의 자작 엔진 주장이고, 이 레포 안에는 근거 데이터가 없다.
   - 테스트는 v0.10 에서 들어온 vitest 5건(`dart-xml`)뿐이고 CI 테스트는 없다. 워크플로는 GitLab 미러 하나다.
   - 메인테이너는 #3 댓글에서 "제 손에 OpenDART 인증키가 없어" 실호출 재현을 못 했다고 적었다.
4. 판정: 투자 성과(수익률·적중률)를 주장하지 않는 데이터·인프라 도구이므로 앵커 5다. 다만 시그널 라벨(`strong_buy_cluster`, 자사주 프리셋)의 해석은 README 가 과장하고 있어, 그대로 믿으면 안 된다.

심층 T 5 (판정 T 5) — 성과 주장이 없는 DART MCP. 시그널 해석의 과장(주식보상의 매수 집계, 신탁해지의 취득 집계)은 T 밖의 품질 문제로 적는다.

## 수요 신호

이슈·PR 은 모두 6개(이슈 1, PR 5)이고 반응은 전부 0, 댓글은 최대 1이다. Discussions 는 꺼져 있다. 유일한 이슈 #3(감사보고서 손익계산서 표 누락)은 버그라 신호에 넣지 않았다. 신호는 5건이다(pain 4, demand 1).

- 설치 어려움(pain):
  - #5: better-sqlite3 11.x 에 node 24 용 윈도우 프리빌트가 없다. 그래서 node-gyp 소스 빌드로 넘어가고, 빌드 도구가 없는 윈도우 사용자는 설치에서 막힌다.
  - #7: 윈도우 Claude Desktop 은 MSIX 패키지라 `%APPDATA%` 가 다른 곳으로 리다이렉트된다. setup 마법사는 성공이라고 표시하지만, 앱이 읽지 않는 경로에 설정을 쓴다.
  - README 도 이미 `npx not found`, `MODULE_NOT_FOUND` 우회법을 싣고 있다. "30초 설치"를 내걸었지만 비개발자의 로컬 MCP 설치는 여전히 마찰이 크다.
- 운영 요구(demand): #4 댓글. 여러 MCP 클라이언트 세션이 각자 서버를 띄우는 환경에서 캐시가 경합한다. 댓글 작성자는 "서버 앞단에서" 우회 중이라고 했고, 캐시 폴더·TTL 을 환경변수로 지정하게 해 달라고 요청했다. `.env.example` 에는 `DART_CACHE_DIR` 가 적혀 있지만 `src/` 어디서도 읽지 않는다(코드 확인).
- 비용·전문성 장벽(pain, README 자체 서술): Claude 구독료와 대용량 PDF 용 상위 플랜 필요, "ROE · CAGR · 부채비율 용어" 를 알아야 결과를 이해할 수 있다는 점이다.
- 호스팅 수요: 이슈로 나온 것은 없다. 다만 포크 `yunoim/dart-mcp-railway` 가 Dockerfile·`railway.json`·HTTP 진입점(`src/http.ts`)과 응답 캐시를 붙여 원격 배포판을 만들었다. 인용할 이슈·토론이 없어 신호에는 넣지 않았다.
- 한국어 지원·API 비용 불만 요청: 없음. 한국어 전용 도구이고 OpenDART 가 무료라서다.

## 파생·상용화

- 포크 19개. ★ 상위 10개도 ★1 이하다.
  - 독자 변경이 있는 포크는 `yunoim/dart-mcp-railway`(Railway 원격 배포, 5커밋 앞섬) 정도다.
  - `zzocrypto`·`renovys` 는 PR 용 포크다.
  - 나머지는 원본과 같은 설명·같은 커밋을 그대로 둔 포크다.
- 상용 래핑: 웹 검색 3회로는 이 레포를 감싼 유료 서비스를 찾지 못했다. 주로 Glama·PulseMCP·awesome-mcp-korea 같은 디렉터리에 등록돼 있다.
- 경쟁 DART MCP 가 많다: `snaiws/DART-mcp-server`, `jjlabsio/korea-stock-mcp`, `anboyu-alt/dart-risk-mcp`(불공정거래 위험 신호), `jackjhjin/mydart-mcp`, `keioseung/MCP`(재무제표 시각화), README 가 비교한 `hypn4/opendart-fss-mcp`·`RealYoungk/opendart-mcp` 등이다.
- 인접 상용: DartPoint AI(dartpoint.ai)가 MCP 서버를 제공한다(OpenDartReader 노트 참조).
- 같은 이름의 다른 계정 레포 `aesthetic-legalism5470/korean-dart-mcp` 가 Glama 에 따로 등록돼 있다. 받지 않았다. 사칭·재배포인지는 확인하지 않았다.

## 내 투자에 쓰려면

- 실행: 설치 방법은 `npx -y korean-dart-mcp setup`, Claude Code 플러그인(`/plugin marketplace add chrisryugj/korean-dart-mcp`), 수동 JSON 등록 세 가지다. OpenDART 키를 `DART_API_KEY` 에 넣고, Claude 에게 "삼성전자 최근 3년 지분 변동" 처럼 자연어로 묻는다. 이번 조사에서는 설치하지 않았다.
- 주의점:
  - 플러그인 매니페스트는 `npx -y korean-dart-mcp@latest` 다. 클라이언트를 켤 때마다 최신 npm 판을 검증 없이 받아 실행하므로, 패키지 탈취에 그대로 노출된다. 쓰려면 버전을 고정해 수동 등록한다.
  - `setup` 은 Claude Desktop·Cursor·VS Code 등 여러 클라이언트의 설정 파일을 직접 고친다. 실행 전에 설정 파일을 백업한다.
  - `insider_signal` 의 `strong_buy_cluster` 를 장내매수로 읽지 않는다. 주식보상·증여·유상증자까지 증가로 센다. raw 보고서의 변동 사유를 따로 봐야 한다.
  - `treasury_buy` 프리셋에는 신탁계약 해지 공시가 섞인다. 공시 제목을 직접 걸러야 한다.
  - `get_xbrl format=raw` 는 LLM 이 준 `out_dir` 에 ZIP 을 푼다(ZIP slip 방어는 있음). 에이전트가 임의 경로에 파일을 쓸 수 있다는 뜻이다.
  - `get_attachments` 는 robots.txt 가 Disallow 로 막은 뷰어 경로를 쓴다. 개별 공시 1건씩만 부른다.
  - `src/version.ts` 는 `0.9.2`, `package.json` 은 `0.10.1`, 플러그인은 `0.9.1` 이다. 보고되는 버전이 서로 어긋나 있다(PR #6 미병합).
  - 윈도우에서 Claude Desktop 을 쓰면 캐시 경합(#4)과 설정 경로(#7) 문제가 아직 main 에 남아 있다.

## 인디 관점 메모

- 차용: GuruNote 에 DART 를 붙일 때 가져올 부분은 세 가지다.
  - `get_xbrl` 의 calculation linkbase 합산 검증과 금융지주 `DX` 택소노미 처리(`src/lib/xbrl-parser.ts`, 814줄, MIT)
  - `search_disclosures` 의 22개 프리셋 사전(`pblntf_ty` + `report_nm` 정규식). 그대로 쓰지 말고 신탁해지 같은 반대 방향 공시를 빼도록 다듬는다.
  - OpenDART quirk 대응(결과 1건이 객체로 오는 문제, `status 013` 침묵 실패, ZIP 응답에 섞인 JSON 에러)
  - 공시 알림 워커는 LLM 클라이언트가 아니라 서버 폴링이므로, 이 MCP 를 끼우지 말고 라이브러리 코드만 옮기는 편이 맞다.
- 경쟁: "한국 투자자가 Claude 로 DART 를 조회한다"는 자리는 무료 MCP 여러 개와 DartPoint AI 가 이미 차지했다. 모두 사용자가 묻는 pull 방식이다. 새 공시가 올라오면 먼저 알려 주는 push 기능은 이 레포와 경쟁 MCP 어디에도 없다. stdio 전용이라 스케줄링도 못 한다.
- 공백:
  - 무설치 호스팅판: 윈도우 설치 마찰(#5·#7)이 있고, Railway 포크가 나왔고, 멀티 세션 서버 운영 요구(#4 댓글)가 있다. 원격 DART MCP 나 텔레그램 봇이 이 마찰을 없앤다.
  - 시그널 품질: 변동 사유(장내매수 vs 보상·증여)를 구분한 내부자 시그널과 방향을 제대로 가린 자사주 공시 분류가 필요하다. 이 레포가 README 로 과장한 부분을 정확하게 해 주는 것 자체가 차별점이 된다.
  - 교차 시장: GuruNote 의 SEC Form 4 워커와 DART 임원·주요주주 보고를 같은 관심 종목, 같은 한국어 요약 형식으로 묶는 서비스는 여기서도 보이지 않았다.
