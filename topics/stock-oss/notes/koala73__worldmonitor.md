---
entity: github:koala73/worldmonitor
gh_id: 1130564872
judged: -  rubric: -
t_deep: 4
tags: [dashboard, osint, macro, geopolitics, finance-variant, open-core, mcp, agpl, user-star]
---
## 무엇·어떻게

지정학·인프라·시장 데이터를 3D 지구본과 WebGL 지도 위에 패널로 모아 보여 주는 실시간 "상황 인식" 대시보드다. clone HEAD `a213b425a7e86f084ff6a8581f4ab386612651c9`(2026-09-27), 라이선스 AGPL-3.0-only, ★약 87k·포크 1.3만. 1단 선별에서는 "금융 특화가 아님"을 이유로 제외됐다. 하지만 코드 하나로 여섯 변형(world·tech·finance·commodity·happy·energy)을 빌드하고, 그중 `finance.worldmonitor.app` 는 사실상 거시·시장 리서치 대시보드다. 이 노트는 금융 쪽에 초점을 둔다.

- 구조: Vanilla TypeScript + Vite 프런트엔드(`src/`), Vercel Edge Functions API(`api/` 171개 파일, `server/worldmonitor/<도메인>/v1/*` 핸들러), Protocol Buffers 계약(`proto/`, sebuf 로 클라이언트 생성), Railway 크론 시더(`scripts/` 630개 파일, `seed-*.mjs`)가 Upstash Redis 에 데이터를 채우고 엣지가 그걸 읽는 "시드 우선" 구조다. 결제·권한은 Convex(`convex/`), 데스크톱은 Tauri 2 + Node 사이드카(`src-tauri/`)가 맡는다. MCP 서버·REST API·CLI(`cli/`)·Python/Ruby/Go SDK(`sdk/`)를 함께 낸다.
- 금융 변형 패널(`src/config/panels.ts` 의 `FINANCE_PANELS`): Live Markets·섹터 히트맵·Forex·Fixed Income·Yield Curve·Central Bank Watch·Macro Stress·Market Regime·Fear & Greed·AAII 심리·Market Breadth·COT 포지셔닝·Financial Stress·실적/경제 캘린더·IPO/M&A·BTC ETF 흐름·스테이블코인·DeFi/AI 토큰·Polymarket 예측·News ↔ Markets 상관·걸프 경제 등 60여 개. 유료 잠금(`premium: 'locked'`)은 Premium Stock Analysis, Premium Backtesting, Daily Market Brief, WSB Ticker Scanner, Trade Policy, Global Procurement, Latest Brief 다.
- 종목 범위: `shared/stocks.json` 카탈로그는 93종목·6개 지역(US·Europe·Asia-Pacific·India·GCC·Americas)이고 기본 관심종목은 59개다. 한국은 `^KS11`(KOSPI)과 `005930.KS`(삼성전자)만 들어 있다. Finnhub 검색으로 사용자 종목을 50개까지 더할 수 있다. UI 는 한국어 로케일(`src/locales/ko.json`)이 있다.
- 데이터 소스(`docs/finance-data.mdx`): 시세는 Alpha Vantage(시더 주 경로) → Finnhub(요청 시 빈칸 채우기)이고, 일부 종목과 종목 분석·백테스트는 Yahoo Finance 비공식 차트 API 를 쓴다. 거시는 FRED·BLS·BIS·ECB·Eurostat·World Bank, 암호화폐는 CoinGecko → CoinPaprika. FMP 는 약관상 재배포 금지라 뺐다고 적혀 있다.
- 유료 종목 분석(`server/worldmonitor/market/v1/analyze-stock.ts`, 2,071줄): Yahoo 6개월 일봉으로 이동평균 배열·MACD·RSI·거래량 상태를 계산해 기술 신호(`Strong buy`~`Strong sell`)와 손절·목표가를 내고, 펀더멘털을 섞은 `ratingSignal`/`compositeScore` 를 따로 낸다. 그 위에 LLM 오버레이(요약·why now·강세/위험 요인·헤드라인 감성 −1~1)를 얹는다. 문서에 따르면 중국 `daily_stock_analysis` 프로젝트의 핵심 로직을 TypeScript 로 옮긴 것이다(`docs/premium-finance.mdx`).
- LLM: 공용 체인 `server/_shared/llm.ts` 이 OpenRouter(DeepSeek V4 Flash 계열, 중국 호스팅 공급자는 라우팅 차단) → OpenRouter 무료(`google/gemma-4-26b-a4b-it:free`, `nvidia/nemotron-3-super-120b-a12b:free`) → Groq(`openai/gpt-oss-20b`) → Ollama(`llama3.1:8b`)·generic 순이다. LLM 이 실패하면 규칙 기반 템플릿 문장으로 대체한다. 브라우저에서는 Transformers.js 도 쓴다.
- 1회 실행 비용: 종목 분석 1회에 LLM 호출 1회(저가 Flash 급)라 무시할 만하다. 부담은 데이터 쪽에 있다. 자체 호스팅에서 시세를 쓰려면 Finnhub·Alpha Vantage 키가 필요하고, 무료 등급은 호출 수가 빠듯하다. 제작자는 운영비가 크다고 밝혔다(토론 #94 "My daily cost is super high already").

## 성과 주장의 신뢰도

1. 주장 목록 — README·`docs/overview.mdx`·`docs/PRESS_KIT.md`·`docs/features.mdx`·Pro 랜딩(`pro-test/index.html`)을 grep(`win rate|backtest|accuracy|outperform|sharpe`)해도 수익률·적중률 같은 헤드라인 수치는 없다. 홍보 문구는 "AI-powered stock analysis with backtesting"(overview.mdx), "WM Analyst chat + AI stock analysis & backtesting"(Pro 요금표) 수준이다. 성과 수치는 제품 기능 안에서만 나온다: Premium Backtesting 패널이 종목별 `winRate`·`directionAccuracy`·`avgSimulatedReturnPct` 를 보여 주고, 승률 55% 이상이면 "Profitable" 배지를 단다(`src/components/StockBacktestPanel.ts`). 전체(world) 변형의 AI Market Implications 패널은 LONG/SHORT/HEDGE 매매 아이디어에 HIGH/MEDIUM/LOW 신뢰도를 붙인다.
2. 면책 문구 — Market Implications 패널 머리: "AI-generated trade signals for informational purposes only. Not investment advice. Always do your own research."(`src/locales/en.json`). 백테스트 문서: "It does not claim to validate the live composite rating until a trustworthy point-in-time fundamentals dataset is available."(`docs/premium-finance.mdx`).
3. 검증 수단 (`server/worldmonitor/market/v1/backtest-stock.ts`)
   - 기간·종목: Yahoo `range=6mo&interval=1d` 일봉이다. 60봉 준비 구간을 빼면 신호 시점은 60여 개뿐이고, 평가 창은 기본 10거래일(3~30)이다. 대상은 사용자 관심종목 단위다. 종목군 전체 성과는 따로 내지 않는다.
   - look-ahead: 신호마다 `candles.slice(0, index + 1)` 로 그 시점까지의 봉만 쓰고, 이후 봉으로 손절·목표가 도달 여부를 판정한다. 기본 대책은 있다.
   - 기억 누출: 백테스트는 `v3-technical-only` 엔진으로 LLM 과 펀더멘털을 빼고 기술 신호만 재생한다(`ratingBasis: "technical_only"`). LLM 기억 누출 문제는 생기지 않는다. 반대로 실제 화면의 LLM 오버레이와 펀더멘털 혼합 등급은 검증되지 않는다.
   - 수수료·슬리피지: 없다. 손절·목표가에 정확히 체결된다고 가정하고, 같은 봉에서 둘 다 닿으면 손절을 먼저 본다.
   - 생존 편향: 기본 종목이 현재 대형주(AAPL·NVDA 등) 위주라 편향이 있다. 대책은 없다.
   - 포워드·페이퍼 기록: 분석 기록을 `analysisId`·`analysisAt` 과 함께 Redis 에 쌓아 두지만, 실시간 신호의 사후 적중을 집계해 공개하지는 않는다. AI 매매 아이디어(Market Implications)는 적중 기록이 없다. 메인테이너가 연 이슈 #4930(Brier 점수 공개 적중 기록 로드맵)이 아직 열려 있다.
4. 판정 — 헤드라인 성과 주장이 없는 데이터·대시보드 인프라가 중심이다(앵커 5 쪽). 다만 유료 기능이 승률·"Profitable" 배지를 팔고 AI 매매 아이디어에 신뢰도를 붙이는데, 이것들을 받치는 근거는 6개월·비용 없는 기술 신호 백테스트뿐이다. 그래서 4로 둔다.

심층 T 4 (판정 T -) — 헤드라인 성과 수치는 없고 백테스트도 시점 분리·LLM 제외로 정직하게 범위를 한정했지만, 유료 패널의 승률·"Profitable" 배지와 AI 매매 신뢰도는 6개월·비용 없는 기술 신호 재생 말고는 검증 근거가 없다.

## 수요 신호

이슈는 2,039개로 많지만 대부분 메인테이너(koala73)와 협업자가 연 작업 티켓이다. ★87k 에 비해 사용자 반응이 매우 얇아서 반응이 가장 많은 이슈도 반응 3 수준이다. 사용자 목소리는 Discussions 쪽이 더 많다. 환영 글 #94(댓글 246개)와 #869(라이선스 키), #1302(PRO 공지)가 중심이고, 이후 Discord 로 옮겨 갔다(#1883). 지정학 기능 요청(보건·우주기상·농업 레이어 등)과 버그(데스크톱 앱 검은 화면, API 키 초기화, 대기자 명단 등록 실패 #673·#941)는 신호에서 뺐다. 넣은 신호 20개(demand 16·pain 4·gap 0):

- **개인 포트폴리오·관심종목** — #680 "US 지수가 1순위고 GCC 는 2순위인데 사용자가 고를 수 없다"(반응 3, 이후 지역별 카탈로그 선택기 반영), 무료판에서 미국 주식 관심종목을 직접 만들고 싶다(#94), 개인 포트폴리오용 종목 필터 타일(#94), 티커를 넣으면 관련 뉴스를 보여 주는 패널(#94), 내가 보유한 코인을 직접 추가하고 싶다(#979). 투자자는 "세계 뉴스 + 내 종목"을 한 화면에서 보고 싶어 한다.
- **뉴스 → 시장 영향 해석** — 지정학 사건에 "S&P 500·특정 원자재에 영향 가능" 같은 AI 태그를 붙여 달라(#94), "오늘 일본 지수가 왜 빠지나"를 물을 수 있는 RAG 채팅(#94), 기관 전망 리포트 수집(#94), Trading Economics 급 글로벌 거시 지표(#972), 원자재 트레이더용 선박 데이터 강화(#94, 반응 2). 이 가운데 상당수는 이후 News ↔ Markets 패널과 WM Analyst 채팅(Pro)으로 들어갔다.
- **알림** — 피드를 AI 로 해석해 내 폰으로 맞춤 알림(#304, 반응 1·댓글 4). 지금은 Pro 의 alert rules + Telegram/Slack/Email 푸시로 구현돼 있다.
- **유료판 수요** — 라이선스 키를 어떻게 받나(#869, 추천 5·댓글 13), 유료판·후원 의향(#94). 대기자 명단 버그 이슈에 수십 명이 몰린 것도 같은 수요로 보인다(버그라 신호에서는 뺐다). 실제로 Pro(월 $39.99)가 출시됐다.
- **자체 호스팅** — 항상 켜 두는 로컬 수집 서버(#265), Vercel 없이 Docker 로 API 까지 돌리고 싶다(#1260 댓글). 현재는 `SELF_HOSTING.md` 에 Docker Compose + Redis + 시더 스크립트 경로가 있다. 그런데 Pro 출시 뒤 자체 호스팅판에도 소스 80개 제한이 걸린다는 불만이 나왔다(pain, #1302 댓글).
- **지역·접근성** — 한국어 지원 요청(#94, 이후 한국어 로케일 추가), 서방 API 가 막힌 지역에서도 쓸 수 있는 데이터 소스(#6146, 댓글 7).
- **신뢰·데이터 라이선스 (pain)** — #5498: LLM 이 타임아웃되면 템플릿 문장으로 바뀌는데 화면에서 구분이 안 된다(이후 출처 표시 PR). #3731: 외부 감사자가 "Yahoo 비공식 API 를 유료 제품의 금융 데이터 척추로 쓰고, 차단을 주거용 프록시로 우회한다"고 지적했고, 메인테이너는 이 건이 아직 미해결이라고 답했다(#3726 댓글 "all handled besides #3731 and #3732").

## 파생·상용화

- 본 프로젝트의 상용화(open-core): 핵심 대시보드는 무료·BYOK 다. 요금제(`pro-test/src/generated/tiers.json`)는 Pro 월 $39.99(연 $359.99; AI 종목 분석·백테스트·WM Analyst 채팅·알림 규칙·MCP 50회/일), Pro Business 월 $49.99(상업 라이선스·데이터 내보내기·MCP 250회/일), API Starter 월 $99.99(REST 1,000회/일·웹훅), 그 위로 API Business·Enterprise 가 있다. 결제는 Dodo Payments, 권한은 Convex 에서 서버 쪽으로 강제한다. PRO 공지(토론 #1302)의 철학은 "charge for convenience, depth, speed, and scale — never gate the core situational awareness platform"이다. 20여 개 API 키를 키 하나로 대신해 주는 편의가 핵심 상품이다. AGPL 과 별도로 상업 라이선스도 판다.
- 제3자 유료 서비스(웹 검색 2회): 이 레포를 감싼 정식 유료 서비스는 찾지 못했다. 원본에서 떼어 낸 독립 포크(`AiProducting/worldmonitor`, ★0)와 미러 사이트 `worldmonitor.apposters.com` 정도가 보인다. **주의**: `worldmonitor-app/worldmonitor`(★4, 2026-07-13 생성, 포크 아님)가 "World Monitor Pro … Far beyond the original repo"라는 이름으로 원본 README 를 베끼고 Windows·macOS 다운로드 배지를 자기 `releases` 로 걸어 두었다. 사칭 레포에서 바이너리를 퍼뜨리는 전형적인 악성코드 유포 패턴이다. 메타데이터와 README 만 봤고 릴리스는 받지 않았다.
- 포크(★순 상위 10): `cn620/world-monitor`(★134, 중국어 설명), `Yeachan-Heo/worldmonitor`(★25), `abhigyanpatwari/worldmonitor`(★20) 등이 있고, 나머지는 ★11 이하의 복제본이다. 금융 특화로 개조한 포크는 보이지 않는다. `swatfa/worldmonitor-bayesian`(★9)은 이름으로 보아 확률 모델 실험이다.

## 내 투자에 쓰려면

- 가장 싼 사용법은 공개 사이트 `finance.worldmonitor.app` 를 무료로 보는 것이다. 거시 체제·수익률 곡선·금융 스트레스·Fear & Greed·COT·실적/경제 캘린더·중앙은행을 한 화면에서 보는 "아침 거시 점검판"으로 쓸 만하다. 계정 없이도 된다.
- 자체 호스팅: `SELF_HOSTING.md` 대로 비밀값 4개 생성 → `docker compose up -d` → `./scripts/run-seeders.sh`. 시세를 쓰려면 `FINNHUB_API_KEY`·`ALPHA_VANTAGE_API_KEY` 가 필요하다. 시더 630개 파일, Redis, 릴레이까지 움직이는 무거운 스택이라 개인 PC 에서 상시로 돌리기는 부담스럽다. 이번 조사에서는 설치·실행하지 않았다.
- 한국 투자에는 약하다. 카탈로그에 KOSPI 지수와 삼성전자뿐이고, 국내 공시·수급·업종 데이터는 없다. 종목 분석은 Yahoo 심볼(`.KS`/`.KQ`)이면 돌아갈 가능성이 있지만 확인하지 않았다(Pro 전용).
- 주의: (1) 유료 종목 분석의 "Strong buy" 신호와 "Profitable" 배지는 6개월·비용 없는 기술 지표 재생 결과라 매매 근거로 삼기에는 약하다. (2) 공식 데스크톱 앱은 메인테이너가 "neglected"라고 인정했다(#3504 댓글). 웹을 쓰는 편이 낫다. (3) 데스크톱 앱을 받는다면 공식 도메인에서만 받는다. 사칭 레포가 있다.

## 인디 관점 메모

- 사용자가 스타한 이유로 추정되는 것: 금융 전용 도구는 아니지만 "지정학·거시·시장을 한 화면에"라는 문맥이 개인 투자 리서치의 출발 화면 역할을 한다. 동시에 1인 개발자가 1년도 안 돼 ★87k·유료 5단 요금제·MCP/SDK 까지 만든 open-core 사례다.
- 공백: (1) 한국판 "거시+지정학+내 종목" 대시보드. KRX·DART·한은 ECOS·KIS 데이터에 국내 뉴스 → 종목 영향 태그를 붙이는 것인데, 원본은 한국 데이터가 거의 없다. (2) 사용자 요청이 가장 뚜렷한 축은 "내 포트폴리오 기준으로 세계 뉴스를 걸러 달라"(티커 → 관련 뉴스, 보유 종목 영향 알림)다. 원본은 지도·전 세계 관점이 먼저라 개인 포트폴리오 중심 뷰가 약하다. (3) 재배포 가능한 시세 라이선스. 원본도 Yahoo 비공식 API 의존을 아직 못 끊었다(#3731). 합법 데이터(KRX 정보데이터시스템·공공 API)만으로 만드는 것 자체가 차별점이 된다. (4) AI 신호의 공개 적중 기록(Brier·포워드 기록). 원본에는 로드맵만 있다(#4930).
- 차용: 시더가 Redis 를 채우고 엣지는 읽기만 하는 "시드 우선" 구조(비용이 사용자 수가 아니라 데이터 소스 수에 비례), 공급자별 약관을 검토해 표로 공개한 "Authorized market-data providers" 문서, 백테스트를 기술 신호로만 한정하고 `ratingBasis` 필드로 범위를 밝히는 정직한 설계, LLM 실패 시 규칙 템플릿으로 대체하고 출처를 표시하는 방식, 하나의 코드베이스로 여러 변형 사이트를 내는 SEO·획득 전략, "키 20개를 키 하나로" 파는 BYOK + 편의 과금 open-core, MCP·SDK 를 유료 등급 한도로 파는 에이전트 채널. 단 AGPL 이라 코드를 가져다 서비스하면 소스 공개 의무가 있다.
