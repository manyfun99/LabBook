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
- [virattt/ai-hedge-fund](notes/virattt__ai-hedge-fund.md) — 투자 대가 페르소나 LLM 과 PEAD 퀀트를 pod·리스크·원장 구조로 엮은 교육용 AI 헤지펀드. PIT·blind 백테스트는 갖췄지만 데이터가 저자의 유료 Financial Datasets 에 묶인 미국 전용이다 (갱신 2026-10-06: 해시체인 원장 페이퍼 트레이딩 추가)
- [valuecell-ai/valuecell](notes/valuecell-ai__valuecell.md) — LLM 에이전트로 크립토 선물 자동매매와 A주·미국 리서치를 하는 데스크톱·웹 앱. 호스팅판과 검증 안 된 수익률 리더보드를 두며, 자체 호스팅·Docker 요청이 가장 많다
- [wbh604/uzi-skill](notes/wbh604__uzi-skill.md) — 종목 하나를 22개 데이터 차원·기관식 템플릿 22종·투자 대가 페르소나 66명으로 채점해 HTML 리포트로 내는 에이전트 플러그인. 자체 성과 주장은 스스로 부정하지만 성과 추적과 호스팅 UI 가 비어 있다
- [tauricresearch/tradingagents](notes/tauricresearch__tradingagents.md) — 역할 분담 LLM 에이전트들이 토론해 등급을 내는 LangGraph 연구 프레임워크. 최근 PIT 정비는 탄탄하지만 논문의 SR 8.21 성과는 3개월·3종목·누출·재현 실패로 믿기 어렵다
- [open-dev-society/openstock](notes/open-dev-society__openstock.md) — Finnhub 무료 키와 TradingView 위젯으로 만든 튜토리얼 기반 무료 주식 대시보드(미국·크립토 위주, KRX 차트 차단). ★19k 에 비해 이슈가 얇고 수요는 자체 호스팅 간소화와 미국 밖 시장에 몰린다
- [666ghj/mirofish](notes/666ghj__mirofish.md) — 문서 GraphRAG 위에서 페르소나 수백 개를 가상 SNS 에서 부딪혀 정성 예측 리포트를 내는 여론 시뮬레이터. 검증 기록이 없고 Zep·토큰 비용이 크며 ★급증은 미디어 효과다
- [financedata/financedatareader](notes/financedata__financedatareader.md) — KRX·네이버·Yahoo·FRED 를 한 API 로 묶은 한국 개인 퀀트의 표준 무료 데이터 크롤러. KRX 로그인 필수화 뒤 메인테이너 계정 기반 GitHub 캐시로 버티며 90일 비밀번호 주기마다 끊기는 단일 장애점이 드러났다
- [financedata/opendartreader](notes/financedata__opendartreader.md) — 금감원 Open DART 를 pandas DataFrame 과 dart CLI 로 감싼 무료 MIT 래퍼. 고유번호 변환·주요사항·지분공시는 바로 쓸 수 있지만 재무 표준화·본문 검색·실적 알림은 공백이다
- [koala73/worldmonitor](notes/koala73__worldmonitor.md) — 지정학·거시·시장을 한 화면에 모은 AGPL open-core OSINT 대시보드. 금융 변형은 거시·시장 리서치에 쓸 만하지만 한국 데이터가 거의 없고, 유료 AI 종목 분석·백테스트는 6개월 기술 신호 재생이라 검증이 얇다
- [dragon1086/prism-insight](notes/dragon1086__prism-insight.md) — 1인 개발자가 2025-03 부터 운영해 온 무료 한국·미국 AI 급등주 분석·가상매매 텔레그램 시스템. 포워드 기록은 공개하지만 헤드라인 수익률은 비용 없는 단순합이라 KOSPI 에 지고, 봉인 리더보드 Stance 가 차용할 핵심이다 (갱신 2026-10-06: README 가 단순합 +355.3% 와 10슬롯 계좌 수익률 +35.2% 를 나란히 싣고, 계좌 수익률이 KOSPI +103.5% 에 뒤졌다고 밝혔다)
- [hkuds/vibe-trading](notes/hkuds__vibe-trading.md) — HKUDS 의 자연어→백테스트 개인 트레이딩 에이전트. 수치 grounding gate·시장별 비용 엔진(KRX 포함)·18개 증권사 커넥터(KIS·토스·업비트)를 갖췄다. LLM 기억 누출 경고는 2026-10-01 에 들어왔지만 컷오프 날짜는 사용자가 넣는다(PR #1618)
- [chrisryugj/korean-dart-mcp](notes/chrisryugj__korean-dart-mcp.md) — OpenDART 를 18개 MCP 도구로 묶은 TypeScript 서버. XBRL 합산 검증·HWP/PDF 첨부 마크다운화·규칙 기반 내부자·회계 리스크 시그널을 주지만 stdio pull 조회라 푸시 알림·무설치 호스팅이 비어 있다

## 아이템 원페이저

- [AI 주식 오픈소스 실사 보고서 + 성과 주장 감사](ideas/oss-duediligence-report.md) — 429개 판정·노트 19개를 한국 지원·실제 비용·성과 주장 신뢰도 3열로 정리한 평가형 카탈로그. 추가 조사비 0, 약점은 노후화와 수익화 (27점)
- [한국 AI·리딩 채널 봉인 성적표](ideas/sealed-scorecard-kr.md) — 한국어 AI 종목 채널의 신호를 받은 시각에 서버가 봉인하고 거래세·슬리피지 반영해 채점. 채널 1,226개·구독 월 3천~6만원이 시장이고, 약점은 표본 확보와 저작권 (26점)
- [대가 공시 속보·13F 파생 한국어 확장](ideas/guru-filing-newsflash.md) — GuruNote 워커·봇·13F DB 에 Form 4·13D/G 속보와 8-K 한국어 요약·시트 내려받기를 얹는다. 실현성·재사용 만점, 약점은 수익화와 본체 검증 미완료 (26점)
- [한국어 설치 생존 가이드 + 지표 카드](ideas/install-survival-guide-kr.md) — 상위 도구의 한국어 설치 문서와 "이 오류 → 이 해결" 사전. 근거가 가장 넓고(13레포·w186) 원재료가 신호 DB 에 있다. 약점은 경시성과 과금 경로 (25점)
- [DART 공시 조건 알림 봇](ideas/dart-alert-bot.md) — 종목·공시유형 조건을 걸어 두면 접수 직후 텔레그램으로 사실 요약이 온다. DIY 봇은 이미 여럿이고 비어 있는 건 비개발자용 호스팅판이다 (25점)
- [관리형 LLM 종목 리포트](ideas/managed-llm-report.md) — 키 설정·토큰 비용 없이 종목만 넣으면 리포트를 받는다. 수익화 만점(go-stock VIP 월 28.8 RMB)이지만 유사투자자문 신고가 필요하고 구독 한도가 곧 용량 상한이다 (24점)
- [거래내역 성과 리포트 — 업로드형](ideas/trade-history-tearsheet.md) — 증권사 거래내역 CSV 로 승률·손익 분포·벤치마크 대비를 계산한다. LLM 이 필요 없고, 리밸런싱 제안은 등록업이라 넣지 않는다 (24점)

## 도구

- [개인 투자 툴킷](toolkit.md) — P≥4 인 12개 + worldmonitor 의 용도·실행법·신뢰 주의점. AI 신호를 다루는 규칙과 쓰지 않기로 한 6개의 사유를 함께 담았다

## 게시글

- [실사 보고서 1편 — 성과 주장을 거르는 5가지 질문](posts/duediligence-01.md) — 감사 5항목(단순합·비용·벤치마크·컷오프·표본)과 AI 도구 5개(TradingAgents·MiroFish·ai-hedge-fund·Vibe-Trading·PRISM-INSIGHT) 채점표. 원페이저 `oss-duediligence-report` 의 검증 글이고 클리앙판은 `posts/duediligence-01.clien.txt` (기준일 2026-10-06)
