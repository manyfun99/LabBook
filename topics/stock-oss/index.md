# stock-oss 카탈로그

에이전트가 먼저 읽는 한 줄 카탈로그다. 노트·아이디어가 생기면 한 줄씩 더한다.

## 심층분석 노트

- [openbb-finance/openbb](notes/openbb-finance__openbb.md) — 공급원 35개를 표준 모델로 묶어 Python·REST·MCP·Workspace 로 내보내는 AGPL 금융 데이터 통합 인프라(오픈 코어). 한국 공급원은 공식 레포가 거절해 비어 있다
- [ranaroussi/yfinance](notes/ranaroussi__yfinance.md) — Yahoo Finance 비공식 API 를 쓰는 사실상 표준 무료 시세 라이브러리. 유료라도 안 깨지는 소스를 원하는 수요가 있으나 대체 소스는 공백이다
- [ranaroussi/quantstats](notes/ranaroussi__quantstats.md) — 수익률 시계열로 성과·위험 지표와 HTML 티어시트를 만드는 무료 라이브러리. 거래 내역 업로드형 호스팅 티어시트가 빈자리다
- [shashankvemuri/finance](notes/shashankvemuri__finance.md) — 150+ 스크립트 모음에서 2026-09 에 누출 방지·비용 반영 백테스트를 갖춘 미국 주식 퀀트 연구 패키지로 재작성됐다. 성과 주장 없음, 이슈 수요는 약하다
- [dgunning/edgartools](notes/dgunning__edgartools.md) — SEC EDGAR 공시 20종+ 를 타입 객체·DataFrame 으로 파싱하는 MIT 라이브러리(MCP 내장, 호스팅판 edgar.tools 월 $25~80). GuruNote 파서로 차용 가능하나 SEC 알림 영역에서는 경쟁자
- [arvinlovegood/go-stock](notes/arvinlovegood__go-stock.md) — Wails·Go 로 만든 A주 중심 AI 주식 분석 데스크톱 앱. AI 추천을 저장했다가 沪深300 대비로 채점하는 포워드 루프가 있고 VIP 후원 구독(월 28.8 RMB)으로 수익화한다
- [mathieu2301/tradingview-api](notes/mathieu2301__tradingview-api.md) — TradingView 비공식 웹소켓을 역공학해 시세·Pine 지표·전략 리포트를 받는 Node.js 라이브러리. 캡차·세션 만료·계정 차단 같은 약관 위험과 비개발자의 백테스트 외주 수요가 두드러진다
- [virattt/ai-hedge-fund](notes/virattt__ai-hedge-fund.md) — 투자 대가 페르소나 LLM 과 PEAD 퀀트를 pod·리스크·원장 구조로 엮은 교육용 AI 헤지펀드. PIT·blind 백테스트는 갖췄지만 데이터가 저자의 유료 Financial Datasets 에 묶인 미국 전용이다
- [valuecell-ai/valuecell](notes/valuecell-ai__valuecell.md) — LLM 에이전트로 크립토 선물 자동매매와 A주·미국 리서치를 하는 데스크톱·웹 앱. 호스팅판과 검증 안 된 수익률 리더보드를 두며, 자체 호스팅·Docker 요청이 가장 많다
- [wbh604/uzi-skill](notes/wbh604__uzi-skill.md) — 종목 하나를 22개 데이터 차원·기관식 템플릿 22종·투자 대가 페르소나 66명으로 채점해 HTML 리포트로 내는 에이전트 플러그인. 자체 성과 주장은 스스로 부정하지만 성과 추적과 호스팅 UI 가 비어 있다
- [tauricresearch/tradingagents](notes/tauricresearch__tradingagents.md) — 역할 분담 LLM 에이전트들이 토론해 등급을 내는 LangGraph 연구 프레임워크. 최근 PIT 정비는 탄탄하지만 논문의 SR 8.21 성과는 3개월·3종목·누출·재현 실패로 믿기 어렵다
- [open-dev-society/openstock](notes/open-dev-society__openstock.md) — Finnhub 무료 키와 TradingView 위젯으로 만든 튜토리얼 기반 무료 주식 대시보드(미국·크립토 위주, KRX 차트 차단). ★19k 에 비해 이슈가 얇고 수요는 자체 호스팅 간소화와 미국 밖 시장에 몰린다
- [666ghj/mirofish](notes/666ghj__mirofish.md) — 문서 GraphRAG 위에서 페르소나 수백 개를 가상 SNS 에서 부딪혀 정성 예측 리포트를 내는 여론 시뮬레이터. 검증 기록이 없고 Zep·토큰 비용이 크며 ★급증은 미디어 효과다
- [financedata/financedatareader](notes/financedata__financedatareader.md) — KRX·네이버·Yahoo·FRED 를 한 API 로 묶은 한국 개인 퀀트의 표준 무료 데이터 크롤러. KRX 로그인 필수화 뒤 메인테이너 계정 기반 GitHub 캐시로 버티며 90일 비밀번호 주기마다 끊기는 단일 장애점이 드러났다
- [financedata/opendartreader](notes/financedata__opendartreader.md) — 금감원 Open DART 를 pandas DataFrame 과 dart CLI 로 감싼 무료 MIT 래퍼. 고유번호 변환·주요사항·지분공시는 바로 쓸 수 있지만 재무 표준화·본문 검색·실적 알림은 공백이다
