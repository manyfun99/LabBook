---
entity: github:dgunning/edgartools
gh_id: 581872397
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [data-mcp, sec-edgar, xbrl, 13f, form4, mcp, us]
---
## 무엇·어떻게

SEC EDGAR 공시를 타입이 있는 Python 객체와 pandas DataFrame 으로 바꿔 주는 MIT 라이브러리다(★2751, 30일 +131, clone HEAD `b022ad2`). 메인테이너는 1인(Dwight Gunning)이다.

- 구조: `Company`/`Filing` 에서 시작해 `.obj()` 로 폼별 객체(`TenK`·`TenQ`·`EightK`·13F·Form 3/4/5·N-PORT·DEF 14A·Form D·144 등 20종 이상)를 얻는다. 주요 모듈은 `edgar/xbrl/`(XBRL 파싱·재무제표), `edgar/standardization/`(회사 간 비교용 개념 표준화), `edgar/ttm/`(TTM 계산·주식분할 보정), `edgar/documents/`(HTML → 텍스트·마크다운, 10-K 섹션 추출), `edgar/thirteenf/`, `edgar/ownership/`, `edgar/storage/`(로컬·S3/GCS/Azure 저장)다.
- 데이터 소스: SEC EDGAR 원천(`www.sec.gov`·`data.sec.gov`)만 쓴다. API 키가 없고 `set_identity(<이메일>)` 로 User-Agent 만 설정한다. 요청은 `pyrate-limiter`·`httpxthrottlecache` 로 초당 요청 수를 제한하고 HTTP 캐시를 쓴다. 엔터프라이즈·학술 미러 URL(`EDGAR_DATA_URL`)과 대량 다운로드(`download_edgar_data`)도 지원한다.
- AI: 선택 설치 `edgartools[ai]` 에 MCP 서버(`edgar/ai/mcp/server.py`, 도구 `company`·`compare`·`filing`·`fund`·`monitor`·`ownership`·`proxy`·`screen`·`search`·`text_search`·`trends` 등)와 Claude 스킬(`install_skill()` 이 `~/.claude/skills/` 에 복사)이 들어 있다. 라이브러리 자체는 LLM 을 호출하지 않는다. `edgar/ai/evaluation/` 에 Claude 로 도구 품질을 평가하는 러너가 있을 뿐이다.
- 1회 실행 비용: 0원(SEC 공개 데이터 + 로컬 실행). 병목은 SEC 초당 10회 제한이다.

## 성과 주장의 신뢰도

1. 주장 목록: 수익률·적중률·샤프·초과수익 주장이 없다. README·docs 에서 `sharpe|backtest|outperform|excess return` 을 검색해도 투자 성과 주장은 나오지 않는다(`docs/guides/proxystatement-data-object-guide.md` 의 `Outperformance` 는 DEF 14A 의 TSR 대 피어 TSR 을 출력하는 예제 코드). 성과 외 주장은 다음이 있다.
   - README "Support This Project": "EdgarTools runs in production at hedge funds, fintechs, and research desks" — 채택 주장, 근거 제시 없음.
   - README "Built for production": "1000+ tests" — 저장소에 `tests/`·회귀 테스트 워크플로가 있어 확인 가능한 편.
   - 이슈 #939 로드맵: XML 파서 "2.7–9.0x" 속도 개선 — 성능(속도) 주장.
2. 면책 문구: "투자 조언 아님" 류 문구는 없다. 데이터 도구라 필요성도 낮다.
3. 검증 수단: 백테스트가 없으므로 기간·수수료·look-ahead·컷오프 이후 구간 항목은 해당 없음. 대신 데이터 정확성 검증으로 회귀 테스트(`regression-tests.yml`), 카세트 기반 네트워크 테스트, 재무제표 불일치 이슈(#52·#228·#779 등) 처리 이력이 있다. 단 `#1033`(main 빌드 실패, 봇 댓글 80개)이 열려 있어 main 이 늘 녹색은 아니다.
4. 판정: 성과를 주장하지 않는 데이터·인프라 도구이므로 앵커 5.

심층 T 5 (판정 T 5) — 투자 성과 주장이 없는 SEC 공시 파싱 라이브러리.

## 수요 신호

반응 수는 전반적으로 작다(최대 2). 이슈 상당수가 파싱 버그·사용법 질문이라 버그는 넣지 않았고, 기능 요청·운영 수요만 13건 뽑았다(demand 9, pain 3, gap 1).

- 분기 데이터 공백: 10-K 에서 Q4 를 역산해 달라는 요청(#335, 댓글 16)과, 10-Q 보다 몇 주 먼저 나오는 8-K EX-99.1 실적 표를 파싱해 공백을 메우자는 제안(#560). 실적 발표 직후 숫자를 원하는 수요다.
- 회사 간 비교·표준화: 여러 회사 재무 비교가 어렵다(#161, 댓글 17). 회사마다 다른 매출 개념을 표준화해 달라(#411, fiscal.ai 를 참조로 언급). 값으로 XBRL 식별자를 역조회하고 싶다(#223). 매출 세그먼트 계층 구조가 필요하다(Discussion #675, 메인테이너가 "real gap" 이라고 인정함).
- 공시 종류 확대: 해외 기업 분기보고서인 6-K 지원(#788, #332). 회사별 최신 보도자료(8-K EX-99.1) 조회(#34).
- 운영·호스팅: 클라우드 저장소 백엔드(Discussion #507, 댓글 15개. 요청자가 "주말 내내 설정했다"고 할 만큼 셀프 호스팅이 어려움). 셀프 호스팅 EDGAR 미러(Discussion #179). 앱에서 붙일 수 있는 MCP 래퍼(#367). 모두 이후 기능으로 반영되었다(cloud extras, MCP 서버).
- 한국 시장·한국어 요청, API 비용 불만: 없음. SEC 전용이고 무료라 해당 수요가 생길 여지가 적다.

## 파생·상용화

- 공식 상용판 [edgar.tools](https://www.edgar.tools): 같은 엔진 위의 호스팅 플랫폼이다. 웹 UI, REST API(20개 이상 엔드포인트), 호스팅 MCP 서버, AI 요약 이벤트 인박스, 알림, 벌크 데이터셋을 제공한다. 무료 티어가 있고 유료는 월 $24.99~$79.99(검색 결과 기준, 월간 결제 $109 옵션 언급도 있음). sec-api.io($49+/월)·BamSEC($69/월)를 비교 페이지로 겨냥한다.
- 오픈소스 수익화: GitHub Sponsors 기업 티어 월 $250~$1,500(SLA·로드맵 참여·7일 선공개), 컨설팅(SEC Data Sprint 1~3일, Pipeline Build 2~4주). 오픈코어 + 호스팅 + 컨설팅 3단 구조의 교과서 사례다.
- 포크: ★ 상위 포크도 ★21(hanzalahwaheed)·★10(virattt, 2024-04 이후 멈춤) 수준이고 나머지는 ★1~2 다. 독자 파생 제품은 보이지 않는다.
- 유사 오픈소스: `stefanoamorelli/sec-edgar-mcp`(★359, AGPL-3.0)는 SEC MCP 서버 경쟁작이지만 README·pyproject 에서 edgartools 의존은 확인되지 않았다.

## 내 투자에 쓰려면

- 실행: `pip install edgartools` → `set_identity("이름 이메일")` → `Company("AAPL").get_financials().income_statement()`, 13F 는 `get_filings(form="13F-HR").latest().obj().holdings`, 내부자 거래는 `Company(t).get_filings(form="4")`. Claude Desktop 에서는 `uvx --from "edgartools[ai]" edgartools-mcp` 로 MCP 서버를 붙인다.
- 주의점:
  - SEC 초당 10회 제한을 지켜야 한다. 대량 수집은 `download_edgar_data`·로컬 저장소를 먼저 받아 두는 편이 낫다.
  - 표준화 재무제표는 회사별 커스텀 개념 때문에 틀릴 수 있다(#52·#228·#408·#779 등 불일치 이슈가 꾸준하다). 숫자는 원문 공시와 대조한다.
  - Q4 값은 10-K 에서 역산해야 하고, 8-K 실적 표는 구조화가 불완전하다.
  - 의존성 상한이 촘촘하다(`httpx<0.29`, `mcp<2.0.0`). 별도 venv 에 격리한다.
  - `install_skill()` 은 `~/.claude/skills/` 에 파일을 쓴다. 이 레포의 Claude 설정과 섞이지 않게 `to=` 로 경로를 지정하거나 쓰지 않는다.

## 인디 관점 메모

- 공백: 분기 데이터 속보성(8-K 실적 표 → 구조화), 회사 간 표준화 비교, 해외 기업 6-K 는 사용자가 반복해서 요구하는데 라이브러리가 아직 약한 곳이다. 이 중 8-K EX-99.1 실적 속보는 edgar.tools 의 이벤트 인박스와 겹치므로, 틈은 "좁은 사용자층 + 채널(텔레그램·한국어)"에 있다.
- 차용: GuruNote 의 SEC 공시 수집 워커는 이 라이브러리를 파서 계층으로 바로 가져다 쓸 수 있다(13F·Form 4·8-K 항목 파싱, 레이트리밋·캐시 포함, MIT). 반면 edgar.tools 는 알림·AI 요약·MCP 까지 호스팅으로 팔고 있어 영어권 SEC 알림 서비스로는 직접 경쟁이 된다. GuruNote 는 한국어 요약 + 텔레그램 전달 + 한국 개인투자자 관심 종목으로 차별해야 한다.
- 수익화 구조(무료 라이브러리 → 호스팅 SaaS → 기업 스폰서·컨설팅)와 sec-api 대비 가격 비교 페이지는 참고할 만한 판매 방식이다.
