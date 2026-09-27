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
