---
entity: github:openbb-finance/openbb
gh_id: 323048702
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [data-mcp, data-platform, mcp-server, rest-api, open-core, agpl]
---
## 무엇·어떻게

OpenBB 의 Open Data Platform(ODP)이다. 여러 금융 데이터 공급원을 표준 모델 하나로 묶어 Python(`obb.equity.price.historical("AAPL")`)·REST API(`openbb-api`, FastAPI, `127.0.0.1:6900`)·MCP 서버(`openbb-mcp`)·CLI·Excel/OpenBB Workspace 에 같은 데이터를 내보낸다. README 표현은 "connect once, consume everywhere". clone HEAD `3e071fcc2cd9f891cac6040ae60296dba76dab46`, `openbb_platform` 버전 4.7.3, 라이선스 AGPLv3.

- 구조: `openbb_platform/core`(공급원 표준 모델·라우터), `providers/`(35개 공급원 패키지), `extensions/`(equity·economy·fixedincome·derivatives·crypto·etf·technical·quantitative·econometrics·news·regulators·`mcp_server`·`platform_api` 등), `cli/`, `desktop/`(Tauri+React 트레이 앱. 첫 실행 때 Miniforge 를 깔고 REST API·MCP 서버·Jupyter 환경을 구성).
- 데이터 소스: 키 없이 되는 것 — yfinance, SEC, CBOE, TMX, Federal Reserve, OECD, IMF, ECB, FINRA, CFTC, multpl, WSJ, stockgrid, finviz 등. API 키가 필요한 것 — FMP, Intrinio, Alpha Vantage, Benzinga, FRED, BLS, EIA, Nasdaq(Quandl), Tradier, TradingEconomics 등(`credentials=["api_key"]`).
- 한국 시장: 전용 공급원이 없다. yfinance 참조표의 `^KS11`(KOSPI 지수)와 FMP 의 `.KS` 접미사 정의 정도만 코드에 있다.
- LLM: 레포 안에서 LLM 을 호출하지 않는다. MCP 서버는 REST 엔드포인트를 MCP 도구로 노출하고, 도구 발견(`--tool-discovery`)으로 필요한 카테고리만 세션별로 켜 토큰 부풀림을 막는 구조다. LLM 은 클라이언트(Claude·Workspace 에이전트) 쪽 몫이다.
- 1회 실행 비용: 무료 공급원만 쓰면 0. 유료 공급원은 각 사의 구독료(예: FMP·Intrinio)가 든다. Workspace Community 는 무료, Workspace Lite(자체 호스팅, 10인 미만 팀)는 연 $2,400, Enterprise 는 별도 견적(웹 검색, openbb.co/pricing·블로그).

## 성과 주장의 신뢰도

1. 주장 목록 — README·desktop/README·MCP README·`*.md` 전수 grep(`outperform|sharpe|backtest|% return` 등)에서 레포 자신의 수익률·적중률 주장은 없다. `backtest` 는 SEC 재무제표 스키마 문서에서 point-in-time 모드(`pit_mode=True`)로 look-ahead 를 피하라는 데이터 사용 안내로만 나온다.
   - 참고: 이슈 #7342 "[Discussion] Live trading signals - $100k portfolio results" 는 제3자가 올린 유료 시그널 판매 스팸(승률 67% 등)이며 메인테이너가 닫았다. 레포의 주장이 아니다.
2. 면책 문구 — README "4. Disclaimer": "Trading in financial instruments involves high risks …", "The data contained in the Open Data Platform is not necessarily accurate."
3. 검증 수단 — 성과 주장이 없어 백테스트 기간·수수료·편향 대책·포워드 기록은 해당 없음. 데이터 도구로서 SEC 재무제표의 PIT 모드 제공은 사용자 백테스트의 look-ahead 대책을 돕는 요소다.
4. 판정 — 성과를 주장하지 않는 데이터·인프라 도구(앵커 5).

심층 T 5 (판정 T 5) — 레포 자체의 성과 주장이 없는 데이터 통합 인프라다.

## 수요 신호

이슈 대부분은 버그·설치 오류와 2024 Hacktoberfest(oss.gg) 기여 과제(댓글순 상위 다수)라 제외했다. Discussions 는 133개로 활동이 적다. 넣은 신호 18개(demand 9·pain 7·gap 2):

- **한국 시장** — #7386 에서 한국투자증권(KIS) Open API 공급원을 제안("There is currently no OpenBB provider for Korean stock market data.")했으나, 메인테이너가 한국 증권 계좌 가입이 필요한 공급원은 레포에서 유지할 수 없다며 별도 확장으로 PyPI 에 내라고 거절했다(gap). 공식 레포는 한국 데이터를 넣지 않는다는 방침이 확인된다. 같은 결로 인도(#256)·중국 A주(Discussion #7072) 문의가 있다.
- **브로커 연동** — #343 Interactive Brokers 지원(반응 11·댓글 13, 2021년부터 열림, 가장 반응 높은 기능 요청). 데이터 플랫폼이지만 사용자는 계좌·주문까지 한곳에서 원한다.
- **무료 데이터 취약성·비용** — #4169 Yahoo Finance 가 또 깨져 대체 공급원으로 옮긴 작업(댓글 19). #7121 EconDB 가 월 $16 구독이라 무료 대안을 원함.
- **설치 어려움** — #524 Windows 설치 파일·실행 파일 요청, #3041 Homebrew 요청. 지금은 Desktop 앱(Miniforge 자동 설치)으로 일부 대응했다.
- **자체 호스팅** — #7175 클라우드에 띄운 백엔드를 Workspace(pro.openbb.co)에 연결하지 못함(열림, 댓글 11, 여러 사용자 +1). #6020 홈 서버 컨테이너를 브라우저로 쓰고 싶음. 로컬은 되지만 원격 호스팅·인증 구성은 사용자에게 어렵다.
- **오픈 코어 우려** — #6434 v3 기능이 v4 에서 빠졌는데 Pro 에서만 되는지 질문, 기존 터미널 사용자가 이탈할 거라는 우려. 메인테이너 답변: 백테스트는 플랫폼 밖에서 직접 짜야 한다(gap) — ODP 는 데이터 수집에만 집중한다.
- **AI·MCP** — #7455 MCP 도구 호출의 서명 감사 기록 요청(댓글 23). 단 제안자와 댓글 다수가 자기 제품(protect-mcp 등)을 홍보하는 벤더 토론이라 무게를 낮춰 봐야 한다. Discussion #7425 "Connect openBB to Claude AI".
- **다국어** — #2855 다국어 지원 요청(닫힘).

## 파생·상용화

- 본사 상용: OpenBB Workspace(pro.openbb.co) — ODP 를 백엔드로 붙이는 분석가용 UI·AI 에이전트. Community 무료 / Lite 연 $2,400(자체 호스팅) / Enterprise(프라이빗 배포·RBAC). 전형적 오픈 코어 구조로, 오픈소스는 데이터 층이고 UI·협업·에이전트가 유료다.
- 호스팅 템플릿: Railway 에 OpenBB API 배포 템플릿이 있다(웹 검색). 제3자 유료 호스팅 서비스는 찾지 못했다.
- 포크(★순 상위 10): TraderAlice/OpenBB-Alice(★45)는 README 까지 원본과 같은 미러, 나머지는 ★14 이하의 옛 OpenBBTerminal 개인 포크. 의미 있는 파생 포크는 없다.
- 확장 생태계: 메인테이너는 공급원 추가를 별도 PyPI 확장 + `awesome-openbb` 목록 등재로 유도한다.

## 내 투자에 쓰려면

- 실행: 가상환경에서 `pip install openbb`(또는 `"openbb[all]"`), Python 3.9.21~3.12. `obb.equity.price.historical(...)` 로 조회, `openbb-api` 로 로컬 REST, `openbb-mcp`(또는 `uvx --from openbb-mcp-server --with openbb openbb-mcp`)로 Claude 등에 MCP 도구로 붙인다.
- 주의: 한국 종목은 yfinance 의 `.KS`/`.KQ` 티커로 가격 정도만 가능하고 재무·공시·수급은 없다(DART·KRX·KIS 는 직접 확장을 써야 함). 무료 공급원(특히 yfinance)은 수시로 깨진다. README 스스로 데이터 정확성을 보장하지 않는다. 설치 의존성이 무겁다(`[all]`). MCP 서버를 `0.0.0.0` 으로 열 때는 인증을 따로 챙겨야 한다. 이번 조사에서는 설치·실행하지 않았다.

## 인디 관점 메모

- 공백: (1) 한국 시장 공급원 — 공식 레포가 거절했으므로 `openbb-kis`/DART/KRX 공급원 확장을 PyPI 에 내면 ODP·MCP·Workspace 전체에 한국 데이터가 들어간다. 확장 하나로 유통 채널을 얻는 구조. (2) 자체 호스팅이 어렵다 — 원격 배포·인증·Workspace 연결을 한 번에 해 주는 관리형 ODP/MCP 호스팅(개인 투자자용 저가)이 비어 있다. 단 AGPLv3 라 수정본을 네트워크 서비스로 제공하면 소스 공개 의무가 있다. (3) 백테스트·주문은 범위 밖으로 명시 — 데이터 층 위의 전략·브로커 연동은 남의 몫이다.
- 차용: 공급원별 fetcher 를 표준 모델로 정규화하는 `openbb_core.provider` 구조, 엔드포인트→MCP 도구 자동 변환과 세션별 카테고리 활성화(도구 발견)로 토큰을 아끼는 설계, SEC 재무의 point-in-time 모드.
