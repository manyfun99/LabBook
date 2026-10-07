---
entity: github:dragon1086/prism-insight
gh_id: 1038434342
judged: 2026-09-27  rubric: v1
t_deep: 4
tags: [llm-agent, multi-agent, korea, us, telegram, kis-auto-trading, forward-record, stance-leaderboard, dart, agpl-dual-license, mobile-app]
---
> 갱신 (2026-10-06): README 가 2026-10-05 KST 개편(a4d235f)으로 +244.63% 헤드라인을 내렸다. 지금은 한국 시즌 2(2025-09-30~2026-10-02, 청산 211건)의 거래별 단순합 +355.3% 와 10슬롯 계좌 수익률 +35.2% 를 나란히 싣고, 같은 기간 KOSPI +103.5% 에 뒤졌다고 스스로 밝힌다(대시보드 JSON 재계산 일치). 10슬롯 값은 "청산한 거래만 포함하며 복리가 아닙니다"(README_ko). 비용 반영 여부는 README 에 없다. 같은 개편에서 "KRX credentials (Kakao account)" 안내가 KIS API 키 안내로 바뀌었고, 후원 절의 운영비가 월 약 $310 에서 $313(OpenAI $234·Anthropic $11·Firecrawl+Perplexity $36·서버 $32, 2026-01)으로 바뀌었다. 아래의 "문서와 코드가 어긋난다"·"운영비는 README 기준 월 약 $310" 서술은 2026-09-28 기준이다.

## 무엇·어떻게

한국(KOSPI/KOSDAQ)과 미국 주식을 대상으로 급등주를 찾아 분석하고 매매까지 하는 멀티에이전트 시스템이다. 개인 개발자 dragon1086 이 2025-03 부터 텔레그램 채널로 운영하던 것을 2025-08 에 공개했다. clone HEAD `2a8cf7f4e66479b82e65822269aa19d8f2b09a91`(2026-09-28, v2.23 대), 라이선스는 AGPL-3.0 과 상용 라이선스의 이중 라이선스다. ★768·포크 262·watchers 9. 이슈는 45개뿐이고 대부분 메인테이너가 스스로 올린 작업 메모다. 반면 `docs/` 에는 2026-09 날짜의 설계·사고 경위 문서가 100개 넘게 쌓여 있다. 코드는 매일 바뀌고, CLAUDE.md 에 따르면 약 26.5만 LOC 규모다. 스타 규모에 비해 코드와 운영이 대단히 크다.

- 파이프라인: `trigger_batch.py` 가 오전·오후에 전 종목을 통계로 스크리닝한다(min-max 정규화·가중 합성 점수·유동성 하위 20% 컷, discussion #131). 트리거마다 후보 3개를 뽑는다. 이어 `stock_analysis_orchestrator.py` 가 분석 에이전트 6개(기술·수급·재무·산업·뉴스·시장)를 순서대로 돌리고, Investment Strategist 가 이를 종합한다. 결과는 PDF 리포트가 되고, 400자 텔레그램 요약(평가 에이전트가 EXCELLENT 가 나올 때까지 반복)과 4개 언어 번역으로 배포된다. `stock_tracking_agent.py` 의 매수·매도 에이전트가 10슬롯 가상 포트폴리오를 운용하고, 설정에 따라 KIS 주문도 낸다(다중 계좌 팬아웃, 기본 `demo`). 매매일지 에이전트가 청산 결과를 원칙·직관으로 압축해 다음 매수 판단 프롬프트에 넣는 피드백 루프가 있다(`tracking/`, `docs/TRADING_JOURNAL.md`). 2026-08~09 에는 결정론적 게이트(레짐 오버라이드·재진입 쿨다운·Market Pulse)와 O'Neil 브레이크아웃 전략, PRISM-BTC(데모)가 붙었다.
- 데이터 소스: 한국은 2026-09-11 에 KIS 단일 제공자로 바꿨다(`docs/KIS_ONLY_MIGRATION_20260911.md`, KRX Open API·FDR/Naver 우회 제거). 여기에 자체 MCP 서버 kospi_kosdaq, DART 공시 원문 파싱(`prism_core/dart_*`, 사업보고서 섹션·재무표를 근거로 인용), Firecrawl·Perplexity 웹 검색을 쓴다. 미국은 yahoo-finance-mcp·sec-edgar-mcp 와 Adanos 소셜 센티먼트(선택)를 쓴다. 신호는 Redis·GCP Pub/Sub 로 외부에 무료로 흘린다(`docs/EXTERNAL_SUBSCRIBER_GUIDE.md`).
- LLM: OpenAI 가 주력이다(README 는 GPT-5 / GPT-5.4-mini, HEAD 의 `report_model_config.py` 기본값은 `gpt-5.6-luna`, DART 리포트는 `gpt-6-luna`). 여기에 Anthropic(보조)이 붙는다. ChatGPT Plus/Pro 구독을 Codex OAuth 프록시로 쓰는 모드(`PRISM_OPENAI_AUTH_MODE=chatgpt_oauth`)가 있는데, 이슈 #221 요청으로 만들어졌다.
- 1회 실행 비용: 종목당 비용을 따로 공개한 자료는 없다. `docs/US_FULL_PIPELINE_VALIDATION_20260918_ko.md` 에 따르면 미국 리포트 1건의 SDK 측정 구간이 24작업·125만 토큰에서 22작업·56만 토큰으로 줄었다(검색·요약 비용 제외). 운영비는 README 기준 월 약 $310(OpenAI $235, Anthropic $11, Firecrawl+Perplexity $35, 서버 $30, 2026-01 기준)이다. 한국·미국 일일 파이프라인 전체를 돌리는 비용이다. 이번 조사에서는 직접 실행하지 않았다.

## 성과 주장의 신뢰도

1. 주장 목록
   - README "Trading Performance / KR Market — Season 2": 기간 2025.09.30~2026.03.24, 거래 86건, 승률 45.35%, 거래당 평균 +2.84%, **누적 수익률 +244.63%**(굵게). US(Beta)는 기간과 거래 13건만 적고 수익률은 없다. README_ko 도 같은 표다.
   - Discussion #86(메인테이너 답변): Season 1 은 "Achieved 408% returns in simulation"이라고 했다. Season 2 는 "Real trading with actual capital (10M KRW ≈ $7,500 USD)"와 "All commissions are fully accounted for in our performance metrics"라고 했다. Threads(@stock_simulation) 홍보글도 "시즌1('25.3월~9월) 시뮬레이션 실적은 누적수익률 408.6%"라고 쓴다.
   - README 이미지 `docs/images/trading-evolution-ko.png`: "관망 종목 30일 평균 +13.3%"(사후 관찰값이라고 표기), "2025 최대 낙폭 -36.86%p". 자기개선 루프 설명은 "past trigger win rates automatically inform future buy decisions"다.
   - 라이브 대시보드(analysis.stocksimulation.kr, `dashboard_data.json` 2026-09-25 생성본을 받아 계산): 거래 210건(청산 2025-10-14~2026-09-16), 승률 40.5%, 거래당 평균 +1.72%, 수익률 단순합 361.2%, 대시보드의 `prism_simulator_return`(단순합 ÷ 10슬롯) 36.1%.
2. 면책 문구: README "Analysis information is for reference only, not investment advice." 성과표 바로 아래에는 "The figures are diagnostic. Cumulative return is the sum of trade-level return rates … not a time-weighted portfolio return or a realizable backtest"가 있다. 누적 수익이 거래별 수익률의 단순합이라고 스스로 밝힌 것이다. 성과 주장이 있으므로 5점 근거로 보지 않는다.
3. 검증 수단
   - 백테스트가 아니라 포워드 기록이다. 매일 실시간 배치가 그 시점 현재가로 가상 매수·매도하고 `trading_history` 에 쌓는다(`stock_tracking_agent.py` 는 `profit_rate = (sell_price - buy_price) / buy_price * 100`). LLM 학습 컷오프·look-ahead 문제는 구조적으로 거의 없다. 대시보드가 종목·매수일·매수가·매도일·매도가를 거래 단위로 모두 공개하므로, 제3자가 실제 시세와 대조할 수 있다(이번 조사에서는 대조하지 않았다).
   - 기간·종목 수: 한국은 약 1년·210건이다. 유니버스는 급등·거래량 트리거로 뽑은 전 종목 후보다. 미국은 13건에 수익률 미공개다.
   - 수수료·슬리피지: 시뮬레이터 수익률 공식에 수수료·거래세·슬리피지가 없다. `examples/generate_dashboard_json.py` 도 `profit_rate` 를 그대로 더한다. #86 의 "commissions fully accounted"는 실계좌 이야기다. 그런데 공개 대시보드의 `real_portfolio`·`account_summary` 는 비어 있어 실계좌 성과를 확인할 수 없다. 같은 답변에서 "I sometimes manually intervene"이라며 실계좌에 수동 개입한 사실도 인정했다.
   - 집계 방식: 헤드라인 +244.63% 는 거래 86건 수익률의 단순합이다. 10슬롯 균등 비중으로 환산하면 약 +24.6% 다(대시보드 값 24.60%). 같은 기간 대시보드 데이터의 KOSPI 는 3424.6→5553.9(약 +62%)였다. 2026-09-16 까지 늘려도 +36.1% 대 KOSPI +95% 로 지수를 크게 밑돈다. README 는 이 비교를 싣지 않는다. 대시보드에는 "KOSPI/KOSDAQ 대비 수익률 비교" 차트가 있다고 적혀 있다. README 표도 2026-03-24 에서 멈췄다. 그 뒤 이미지 속 "2026.06-07 누적수익 재훼손" 구간이 헤드라인에 반영되지 않았다.
   - 기록 무결성: 대시보드 수치는 운영자 자신의 SQLite 에서 나온다. 사후 수정을 막는 장치가 없다. 이를 보완하려고 Stance(`stance/`, 2026-08~)를 만들었다. append-only 해시체인 원장, 서버가 접수 시각을 먼저 박은 뒤 시세를 찍는 방식, 소급 입력 금지, 매도 시 법정 거래세 0.2% 반영(증권사 수수료는 의도적으로 0)을 갖췄다. 하지만 공개 리더보드(2026-09-27 생성)에는 PRISM 자신의 전략 2개만 있다. KR 은 30거래일·누적 -1.88%·청산 0건으로 공식 순위 요건(63거래일·청산 20건)에 못 미치고, US 는 0일이다. 외부 참가 전략은 없다.
4. 판정: 실시간 포워드 기록이 1년 치 있고 거래 단위로 공개되어 있다. 이는 앵커 5(실시간 평가)의 핵심 요소다. 그러나 헤드라인 수치는 단순합이라 실제보다 크게 보이고, 비용이 빠져 있으며, 벤치마크에 크게 진다는 사실은 README 에 없다. 게다가 운영자가 고칠 수 있는 자체 DB 기록이다. 제3자 봉인 기록(Stance)은 30일·청산 0건이라 아직 근거가 되지 못한다. 그래서 5에서 한 단계 내린다. 판정 T 4 와 같고, 골드 T 5 보다 1 낮다.

심층 T 4 (판정 T 4) — 컷오프 문제가 없는 1년·210건 실시간 포워드 기록을 거래 단위로 공개했지만, +244.63% 헤드라인은 비용 없는 단순합이고(10슬롯 환산 약 +25%, 같은 기간 KOSPI +62%) 자체 DB 라 봉인되지 않았다.

## 수요 신호

이슈 45개(반응순·댓글순 상위 30은 사실상 전부)와 Discussions 4개를 모두 봤다. 반응 수가 거의 0~3이라 가중치는 낮다. 이슈의 절반가량은 메인테이너의 작업 메모이고, 나머지는 설치·KIS·Pub/Sub 오류 보고라 버그는 뺐다. #291·#292 는 무관한 스팸이다. 넣은 신호 9개(demand 6·pain 2·gap 1):

- **API 비용·구독형 LLM**: #221 ChatGPT OAuth 요청(Codex OAuth 프록시로 반영됨), #64 텔레그램 끄기 요청(사유 "API 비용 절감"), #48 무료 tier TPM 3만 한도에 걸림(메인테이너는 조회 기간을 2년에서 1년으로 줄이거나 tier 를 올리라고 답함). 운영 채널은 OpenAI tier4 계정으로 돈다고 밝혔다.
- **유료 검색 API 대체**: #751 Perplexity 구독이 없어 Tavily 등 다른 검색 도구를 원한다(열림).
- **성과 검증 투명성**: discussion #86 "페이퍼 트레이딩인지 실매매인지, 수수료·슬리피지가 중요하다"(반응 3, Discussions 중 최다).
- **KIS 주문 구조 재사용**: #412 매수·매도 에이전트 분리와 KIS 실제 주문 실행 구조를 다른 프로젝트에 이식하고 싶다는 외부 기여자 제안. 메인테이너가 OrderIntent·Broker Adapter 구조로 실제 구현했다.
- **다른 시장**: #272·discussion #273 인도(거절). 한국어·한국 시장 요청은 없다. 이 레포가 이미 한국 1순위라서다.
- **gap**: Stance README 의 문제 정의, 즉 수익률 인증은 조작할 수 있고 검증하려면 계좌를 통째로 열어야 한다는 것. 제3자 봉인 포워드 성적표가 시장에 없다는 공백이다. #685 에서 Headline Arena(매크로 예측 포워드 채점)가 같은 철학이라며 제휴를 제안했지만 거절됐다. 홍보성이라 신호에서 뺐다.

## 파생·상용화

- 본인 운영 채널(모두 무료): 텔레그램 KR 채널 `stock_ai_agent` 구독자 862명, EN 33명, JA 3명(2026-09-28 t.me 공개 페이지). README 는 "Currently serving 450+ users for free"라고 쓴다. 2025-08 공개 당시 Threads 글은 "100명+ 구독자"였다. 1:1 분석 봇(`telegram_ai_bot.py` 의 /report·/us_report·/ask 등)은 채널 구독자만 쓸 수 있고, 한때 하루 1회 한도가 있었다. #307 에서 메인테이너는 "어차피 사용자 별로 없음"이라며 한도를 풀었다. 카카오봇(`kakao_bot/`, 카카오 공모전 출품 문안이 `docs/KAKAO_PRISM_BOT_COMPETITION_KO.md` 에 있음)과 iOS·Android 앱(Google Play·App Store)도 있다. 앱은 필터링된 알림과 PDF 리포트를 준다. README 에 "20 free credits (normally 10)" 프로모가 있어 크레딧 과금 구조로 보이지만, 앱 코드는 레포에 없고 가격도 확인하지 못했다.
- 수익화: GitHub Sponsors, 플래티넘 스폰서 AI3(WrksAI), 상용 SaaS 라이선스가 있다(`COMMERCIAL-LICENSE.md`: 비독점 Startup $500/월·SME $2,000/월·Enterprise 협의, 1개 SaaS 에 독점권을 주는 12개월 계약 별도). AGPL 이라 이 코드를 SaaS 로 감싸려면 소스를 공개하거나 이 라이선스를 사야 한다. CLA 로 기존 기여에 소급 동의를 받는 중이다(#603, 댓글 9). 상용 라이선스를 팔 준비로 보인다.
- 규제 위치: 채널·봇·Pub/Sub 신호가 모두 무료다. 대가를 받지 않으니 유사투자자문업 신고 요건 밖에 두는 구조로 보인다(추정). 카카오봇 문안은 "투자 리딩봇이 아닙니다"와 "가상 포트폴리오"를 강조한다. Stance 설계 문서(`docs/superpowers/specs/2026-08-10-otd-declaration-protocol-design-v0.2.md` §10)는 "실시간 공개는 사실상 매매 시그널 방송"이라며 유사투자자문 위험을 직접 다룬다. 그 대응으로 종목·사유 공개를 T+1 로 늦추고 복사매매를 명시적으로 제외했다. 반면 텔레그램 채널은 매수·매도 알림을 실시간으로 보낸다.
- 포크(★순 상위 10): 모두 ★0~2 다. don9x2E/prism-insight-crypto(★2, 크립토판)가 있을 뿐 눈에 띄는 파생은 없다. 웹 검색(2회)에서도 이 레포를 감싼 제3자 유료 서비스는 찾지 못했다. 홍보는 Threads(@stock_simulation)·velog 로 한다.

## 내 투자에 쓰려면

- 실행: 미국 종목 리포트만 보려면 `./quickstart.sh <OPENAI_KEY>` 또는 `python3 demo.py NVDA --language ko` 로 PDF 를 만든다(키 하나면 된다). 한국 전체 파이프라인은 `mcp_agent.config.yaml`·`mcp_agent.secrets.yaml`·`.env`·`trading/config/kis_devlp.yaml` 을 채운 뒤 `python stock_analysis_orchestrator.py --mode morning --no-telegram` 으로 돌린다. Playwright(PDF), perplexity-ask MCP(npm 빌드), Firecrawl 키도 필요하다. 이번 조사에서는 설치·실행하지 않았다.
- 주의: (1) 2026-09-11 KIS 단일 제공자 전환 뒤로 한국 데이터는 KIS 앱키가 있어야 돈다. README 는 아직 "KRX credentials (Kakao account)"라고 적어 문서와 코드가 어긋난다. (2) 설정 파일 4종과 외부 키 5개 이상, cron, SQLite 가 필요해 무겁다. 직접 돌리기보다 무료 텔레그램 채널과 대시보드를 소비하는 편이 싸다. (3) 채널의 매수 신호를 따라 할 근거로 성과표를 쓰지 않는다. 10슬롯 환산으로 KOSPI 를 크게 밑돌았고 비용도 빠져 있다. (4) 쓸모가 있는 곳은 DART 원문을 근거로 인용하는 한국 종목 리포트(`demo.py 005930`)와 기술·수급·재무·뉴스를 한 번에 정리해 주는 1차 스크리닝이다. (5) 월 $300 대 API 비용이 드는 구조다. 개인이 돌린다면 ChatGPT 구독 OAuth 모드를 쓴다(비공식 경로라 약관 위험은 스스로 판단해야 한다).

## 인디 관점 메모

- GuruNote 와의 관계: 한국 투자자 대상 텔레그램 AI 종목 분석이라는 같은 판에서 가장 가까운 무료 경쟁자다. 1인 개발자가 1년 넘게 매일 운영하고, 5개 언어 채널·앱·카카오봇·대시보드를 이미 갖췄다. 다만 KR 채널 862명이라는 도달 규모는 작다. 메인테이너가 "사용자 별로 없음"이라고 한 것을 보면 무료 AI 리포트 채널만으로 사람을 모으기는 어렵다. 이 레포는 공시 해설이 아니라 급등주·단기 매매에 치우쳐 있다. SEC 공시를 한국어로 풀어 주는 영역(GuruNote)과는 겹치는 부분이 작다. 미국 모듈은 sec-edgar-mcp 로 공시를 읽지만 공시 이벤트 알림 제품은 아니다.
- 공백: (1) 제3자 봉인 성적표 — Stance 가 "과거 실적 안 받음·서버 봉인 시각"이라는 올바른 규칙을 만들었지만 참가자는 운영자 자신뿐이다. 중립 운영자가 한국 AI 신호 채널·텔레그램 리딩방의 판단을 받아 채점하는 서비스는 아직 없다(#685 도 같은 방향). (2) 헤드라인 정직성 — 거래 수익률 단순합을 굵게 내세우는 관행이 이 레포에도 있다. 시간가중 수익률과 지수 대비 수치를 기본으로 보여 주는 것만으로 차별점이 된다. (3) 규제 설계 — 무료 실시간 신호, T+1 공개, 복사매매 제외 같은 판단 근거가 문서로 남아 있어 참고할 만하다.
- 차용: Stance 프로토콜(목표 비중만 선언 → 서버가 가격·체결·성과 계산, append-only 해시체인, 같은 seq 재전송 시 멱등 응답, 시세 장애 시 거부가 아닌 보류, 법정 거래세만 반영하고 공식 순위 문턱은 63거래일·청산 20건), 매매일지 → 원칙·직관 압축 → 다음 판단 프롬프트로 이어지는 피드백 루프, 텔레그램 요약을 평가 에이전트가 통과시킬 때까지 다시 쓰는 루프, 번역 에이전트 하나로 채널 여러 개에 배포하는 구조, 채널 구독 여부로 봇 사용을 제한해 채널 성장으로 잇는 방식, ChatGPT 구독 OAuth 로 API 비용을 없애는 모드(수요 #221), DART 원문 섹션·표를 근거로 인용하는 리포트 방식.
