---
entity: github:tauricresearch/tradingagents
gh_id: 909213664
judged: 2026-09-27  rubric: v1
t_deep: 2
tags: [llm-agent, multi-agent-debate, langgraph, academic-paper, point-in-time, backtest, multi-market, apache-2.0]
---
## 무엇·어떻게

실제 트레이딩 회사의 역할 분담을 흉내 낸 LangGraph 기반 멀티에이전트 LLM 트레이딩 연구 프레임워크다. 논문(arXiv 2412.20138, v7 2025-06-03)의 공개 구현이다. clone HEAD `35543d0248bf89fcb92b17a15858ad0c0e940687`(v0.5.1, 2026-09-24), Apache-2.0, ★10.9만·포크 2.1만. 2024-12 에 만들어졌지만 코드는 2025-06 에야 공개됐다(#6 "How long do we need to wait?"). 2026 년 들어 거의 매달 릴리스가 나오고, CHANGELOG 의 기여자 명단도 길다.

- 구조: 애널리스트 4명(fundamentals·sentiment·news·market/technical) → bull/bear 리서처 토론(`max_debate_rounds` 기본 1) → Research Manager → Trader → 리스크 토론 3명(aggressive·conservative·neutral) → Portfolio Manager 순으로 흐른다. 결과는 5단계 등급(Buy/Overweight/Hold/Underweight/Sell)이다. 체결 모델은 없다. `backtest.py` 도 "It is not a portfolio simulator, and must not grow one"이라고 못 박아, 수량·체결가·현금 원장을 두지 않는다.
- 데이터 소스: 기본값은 모두 yfinance(가격·지표·재무·뉴스)다. 여기에 FRED 거시(키 필요, 무료)·Polymarket(키 없음)·StockTwits·Reddit RSS 를 쓰고, 선택으로 Alpha Vantage 와 SEC EDGAR(공시 시점 재무, 미국 상장사만, 2009년부터)를 붙인다. 시장은 Yahoo 티커 접미사로 고른다(.HK·.T·.NS·.SS·.SZ·크립토 등).
- LLM: OpenAI·Google·Anthropic·xAI·DeepSeek·Qwen·GLM·MiniMax·OpenRouter·Mistral·Kimi·Groq·NVIDIA·Bedrock·Azure·Ollama, 그리고 OpenAI 호환 엔드포인트 전반이다. 기본값은 `gpt-6-sol`(deep)·`gpt-6-luna`(quick)다. 선택 기능으로 TypeSafe 의 Jev 가 소셜 글을 걸러 준다(`TYPESAFE_API_KEY`).
- 지속 상태: 결정 로그(`~/.tradingagents/memory/trading_memory.md`)가 늘 켜져 있다. 같은 티커를 다시 돌리면 직전 결정의 실현 수익과 벤치마크 대비 알파를 계산해 회고문을 만들고, 이를 Portfolio Manager 프롬프트에 넣는다. LangGraph 체크포인트 재개는 선택(`--checkpoint`)이다.
- 1회 실행 비용: 논문은 예측 1회에 "11 LLM calls & 20+ tool calls"라고 적었다. #750 은 16~22회 호출에 프롬프트 캐시 적중률이 약 0%라고 분석했다. 실측은 #168 댓글 하나뿐이다. o4-mini/gpt-4o-mini 기준 결정 1회 약 $0.12, 3개월 일별 백테스트 1회 약 $10(2025-07)이다. 지금 기본값인 GPT-6 추론 모델에서 비용이 얼마인지는 자료가 없다. 이번 조사에서는 직접 실행하지 않았다.

## 성과 주장의 신뢰도

1. 주장 목록
   - 논문 초록: "extensive experiments reveal its superiority over baseline models, with notable improvements in cumulative returns, Sharpe ratio, and maximum drawdown".
   - 논문 Table 1(v7): AAPL CR 26.62%·AR 30.5%·SR 8.21·MDD 0.91%, GOOGL CR 24.36%·SR 6.39, AMZN CR 23.21%·SR 5.60. 비교 대상 5개(B&H·MACD·KDJ&RSI·ZMR·SMA)를 모두 이겼다고 한다. 결론 절은 "TradingAgents outperforms traditional trading strategies and baselines in cumulative return, Sharpe ratio, and other critical financial metrics"라고 쓴다.
   - 홈페이지(tauric.ai/research/tradingagents): "The system reaches up to 30.5% annualized returns, outperforming traditional trading strategies while maintaining robust risk management." 같은 표를 싣고 "consistently outperforming all baselines"라고 쓴다. 그런데 이 페이지는 데이터 구간을 "January to March 2024", 시뮬레이션 구간을 "June to November 2024"로 적어, 논문 v7(시뮬레이션 2024-01-01~03-29)과 기간이 어긋난다.
   - README 에는 수치가 없다. 첫머리 arXiv 배지와 Citation 으로 논문에 연결하고, "Backtest results are not guaranteed to match any published figure"라며 공개된 수치가 있다는 사실을 스스로 전제한다.
2. 면책 문구: README "TradingAgents framework is designed for research purposes. … It is not intended as financial, investment, or trading advice.", Reproducibility 절 "Treat the framework as a research scaffold …, not as a strategy with a fixed, replicable return." 1에 수치 주장이 있으므로 면책 문구가 있다고 5점으로 보지 않는다. 판정 T 4 는 이 면책 문구와 README 의 PIT 기능 소개를 근거로 삼았다(오독).
3. 검증 수단
   - 백테스트 기간·종목: 논문 기간은 약 3개월(2024-01-01~03-29)이다. 본문은 "Apple, Nvidia, Microsoft, Meta, and Google"이라고 했지만 결과표에는 AAPL·GOOGL·AMZN 3종목만 있다(AMZN 은 본문 목록에 없다). 논문 스스로 "We benchmarked TradingAgents over 3 months due to intensive LLM and tool use", "The highest Sharpe Ratio exceeds our expected empirical range"라고 인정한다. 롱 전용·일 1회 결정이다(#119 댓글 분석).
   - 수수료·슬리피지: 논문에 언급이 없다. 현재 `run_backtest` 도 등급별 실현 알파(기본 보유 5거래일)만 채점하고 비용은 없다.
   - look-ahead 대책: 논문은 "ensuring no future data is used (eliminating look-ahead bias)"라고 주장했다. 하지만 실제 코드에서 누출이 반복해서 보고됐다. 백테스트 중 실시간 정보를 가져왔고(#203, 모든 날이 BUY), 2025 년 뉴스가 2024 백테스트에 섞였으며(#168 댓글), 당일 데이터를 썼다(#175). 이 수정(e111388)은 2026-03 에야 들어갔다. 그 뒤로도 yfinance 뉴스(#1007), 소셜(#1220), FRED(#1275), 결정 로그 교훈(#1251), 펀더멘털 스냅샷(#1300) 누출이 2026-06~09 에 차례로 고쳐졌다. v0.5.0(2026-09-18)이 "Point-in-time integrity across every dated path"를 내세운다. 논문 수치는 이 수정들보다 앞선 파이프라인에서 나왔다.
   - LLM 기억 누출: 논문은 gpt-4o-mini·gpt-4o·o1-preview 를 썼다. 이 모델들의 공식 학습 컷오프(2023-10)를 기준으로 하면 2024Q1 은 컷오프 이후지만, 논문은 컷오프를 논하지 않는다(#203 댓글은 모델 업데이트로 실제 지식이 2024-06 까지 갔을 수 있다고 지적). 모델 수준 누출을 다룬 #805 는 열려 있고, 메인테이너는 "a separate, fundamental limitation a code change can't fully eliminate"라고 답했다. ai-hedge-fund 의 blind 모드 같은 대책은 없다. #805 댓글이 PR 을 제안했지만 아직 반영되지 않았다.
   - 재현성: 재현 실패 보고가 있다. #168 은 같은 AAPL 구간을 돌려 -25.4%(B&H -7.6%)를 얻었고, #137 은 논문 B&H(-5.23%)조차 재현되지 않는다(약 -7.5%)고 했다. 평가 코드도 공개되지 않았다(#119·#137. 2026-09 에 "addressed in the current version"이라며 닫았지만, 논문 실험을 재현하는 스크립트는 레포에 없다). #178·#1239 는 같은 입력에서 등급이 매번 달라진다고 했다. #1196 은 토론 계층이 모호한 사례를 Overweight 로 기울인다는 것을 통계로 보였다(a4acd8a 에서 프롬프트 수정).
   - 포워드·페이퍼 기록: 없다. 논문은 실매매를 "Future work"로 미뤘다. #225(돈 번 사람 있나)에 답한 사람이 없다.
4. 판정: 수치 성과 주장(SR 8.21·연 30.5%)이 있고, 기간·종목은 공개했으니 앵커 3의 형식은 갖췄다. 하지만 표본이 3개월·결과 3종목으로 매우 작다. "look-ahead 제거"라는 주장은 코드에서 반박됐고, 평가 코드가 없으며, 제3자 재현은 반대 부호로 나왔다. 그래서 앵커 3에 못 미친다. 현재 코드의 PIT 정비는 논문 주장의 근거를 뒤늦게 보강하는 것이 아니라 새 도구의 품질이다. 새 코드로 논문을 다시 평가한 공개 결과도 없다. 골드 T 2 와 같다.

심층 T 2 (판정 T 4) ⚠ — 논문·홈페이지에 SR 8.21·연 30.5% 주장이 있는데, 3개월·3종목·비용 없음·look-ahead 누출 확인·재현 실패로 근거가 앵커 3에도 못 미친다. 면책 문구와 최근 PIT 기능은 이 주장을 되살리지 못한다.

## 수요 신호

Discussions 는 켜져 있지만 글이 2개(키 변경 문의)뿐이다. 이슈는 반응순·댓글순 상위 30개씩과 키워드 검색(korea·cost·token·alpaca·paper·look-ahead 등)으로 봤다. 상위권에 설치·제공자 오류 보고가 많아 버그는 뺐다. 넣은 신호 38개(demand 17·pain 17·gap 4):

- **성과 신뢰·재현성**(가장 두드러짐): #33 "결과가 너무 좋아 누출이 의심된다"(반응 10), #178 "Random Number Generator"(반응 11), #168 재현하니 -25%(댓글 11), #137·#119 평가 코드 요청, #225 "진짜 돈 번 사람 있나"(댓글 10, "논문 쓰려고 만든 것" 댓글에 반응 11), #1239 실행할 때마다 등급이 다르다, #483 "辩论…没有数据支撑", #805 모델 수준 기억 누출(열림). 사용자들이 논문 수치를 믿지 않는다. 이 불신이 이 레포 이슈 트래커에서 가장 오래 이어진 흐름이다.
- **LLM API 비용**: #17 "heavily reliant on OpenAI models which is costly"(반응 8), #26 로컬 모델(반응 5), #621 Ollama Cloud(반응 5), #591 Copilot 구독, #1194·#1231 ChatGPT 구독으로 돌리기, #750 캐시 적중 0%, #515 토큰 예산 상한. 대부분 제공자 추가로 풀렸다. 구독형(Codex·Copilot)만 남았는데, 메인테이너는 "documented API"가 나올 때까지 보류한다고 했다.
- **다른 시장**: A주 #68(댓글 13, "FINNHUB 要付费 $4000")·#16(AKShare)·#506·#1162(A주판 포크 공개), 인도 #832, 대만 #1156·#1392, 크립토 #82(댓글 18, 반응순·댓글순 모두 상위). **한국**: 요청 이슈는 0건이다. #832 댓글에 "005930.KS <-- korea stock"으로 한국 종목을 쓴 사례가 있다. #1392 답변은 .KS/.KQ 벤치마크를 추가했다고 했지만(47ac1f2), 그 커밋은 main HEAD(35543d0)에 들어 있지 않다. HEAD 의 `benchmark_map` 에는 .KS 가 없어 한국 종목 알파는 SPY 대비로 계산된다.
- **실매매 연동**: #1225 Broker Execution Interface(댓글 6, SignalProvider 초안 PR 로 이어짐), #342 Alpaca·Robinhood, #446 MetaTrader 5, #483 "没有实盘交易能力". 메인테이너는 체결을 범위 밖으로 둔다.
- **투자자 맞춤·UX**: #665 투자 기간(장기/단기) 설정(반응 4, 열림), #704 실행 중 대화, #112 API 키 위치(댓글 11)·GUI 로 모델 설정.
- **gap**: 모델 수준 누출을 막거나 측정하는 평가(#805 댓글 두 개 — "only evaluation on post-cutoff data or live forward testing is honest"), 과거 날짜로 돌려도 뉴스·소셜은 "now"를 반영한다는 README 자인.

## 파생·상용화

- 호스팅판: 웹 검색 결과에 trading-agents.ai("Institutional-Grade Equity Research & Market Analysis")가 "powered by TauricResearch/TradingAgents and optimized & hosted with ♥ at Alpha Vantage Inc"로 나온다. 페이지를 직접 받아 보니 본문이 JS 로 그려져 운영 주체와 가격은 확인하지 못했다. 한편 옛 README 에는 Alpha Vantage 무료 한도 상향 문구가 있었는데, #305 에서 메인테이너가 "There is no formal partnership with Alpha Vantage in this project"라고 답했다.
- 자체 호스팅 템플릿: Railway 의 "Deploy & Host TradingAgents" 템플릿이 FastAPI 로 감싼 웹 UI·REST API 를 제공한다.
- 스타트업 래퍼: ZorroHQ(#199, 이 프레임워크 위의 호스팅 워크플로·SDK, 대기자 명단 단계).
- 저자 측: Tauric Research 가 후속작 Trading-R1(기술 보고서 arXiv 2509.11420, "Terminal expected to land soon")을 예고했다. 상용 제품으로 가는 흐름으로 보이지만 가격은 없다.
- 포크(★순 상위 10): 0x0funky/TradingAgents-crypto(★135), hsliuping/TradingAgents(★76 — 별도 레포 TradingAgents-CN 으로 성장, Apache-2.0 코어와 소스 공개 독점 앱 계층의 혼합 라이선스, FastAPI+Vue 웹앱·페이퍼 트레이딩), TheLocalLab/TradingAgents-GUI(★32, 로컬 GUI), Bronny-62/BigA-Analysis-Agents(A주), jiwoomap/TradingAgents-Dashboard(★13, 웹 대시보드), hkwsg/TradingAgents-A-share. 포크 2.1만 개 가운데 두드러진 것은 A주·크립토·GUI 셋뿐이다. 이슈 속 파생으로 michaelyuancb/tradingagent_a(메인테이너는 README 에 안내를 넣었다고 답했지만 HEAD README 에는 없다), cms19859230182-lang/TradingAgents-AGu-Edition(비용 모델링 포함 backtrader)이 있다.

## 내 투자에 쓰려면

- 실행: `pip install .`(Python 3.12) 또는 `docker compose run --rm tradingagents` → `tradingagents`(대화형 CLI)로 티커·날짜·제공자·리서치 깊이를 고른다. 코드에서는 `TradingAgentsGraph(config).propagate("005930.KS", "YYYY-MM-DD")`로 부른다. 여러 날짜는 `tradingagents backtest <티커들> --start --end --every 7`로 돌린다. LLM 키 하나만 있으면 되고, 데이터는 yfinance 로 무료다. Ollama·vLLM 로 로컬 모델도 쓸 수 있다. 이번 조사에서는 설치·실행하지 않았다.
- 주의: (1) 한국 종목은 `.KS`/`.KQ` 티커로 돌지만 재무·뉴스는 yfinance 뿐이다(DART 없음, EDGAR 는 미국만). HEAD 에서는 알파가 SPY 대비로 계산된다. (2) 결과는 실행마다 달라진다. 한 번의 등급을 신호로 쓰지 말고 여러 번 돌려 분포를 본다. (3) 과거 날짜 백테스트는 모델이 그 구간을 기억하고 있을 수 있다(#805). 쓰는 모델의 컷오프 이후 구간만 믿는다. 비용·슬리피지는 없다. (4) 결정 1회에 LLM 호출이 16~22회라 추론 모델을 쓰면 비싸다. `quick_think_llm` 을 싼 모델로 두고 `max_debate_rounds` 를 1로 유지한다. (5) `--portfolio` 로 보유 종목을 넘기면 포지션 기준으로 조언을 받는다. 실제 쓸모는 "종목 하나에 대한 다관점 리서치 보고서 생성기" 정도다.

## 인디 관점 메모

- 공백: (1) 신뢰 가능한 성과 기록 — 이슈 트래커에서 가장 큰 흐름이 "논문 수치를 믿을 수 없다"(#33·#168·#178·#225)다. 이 프레임워크(또는 ai-hedge-fund) 설정별로 모델 컷오프 이후 구간 포워드 기록을 공개하는 독립 리더보드가 비어 있다. (2) 모델 기억 누출 감사 — #805 에서 제3자가 12개 모델의 회상 AUC 를 쟀지만 제품은 없다. 백테스트 전에 "이 모델·이 구간은 믿을 만한가"를 알려 주는 검사가 차별점이 된다. (3) 한국판 — 요청은 0건이지만, A주판 포크가 여럿 나오고 CN 포크가 제품으로 커진 것을 보면 "현지 데이터 + 현지어" 판에 수요가 있다. DART 공시 시점 재무·네이버 뉴스·KRX 벤치마크를 붙이면 된다. (4) 장기 투자자 모드(#665) — 지금 파이프라인은 기술지표·단기 뉴스 중심이라 장기 보유자에게 "오늘 청산" 같은 조언을 낸다.
- 차용: 역할별 에이전트와 bull/bear·리스크 3자 토론 그래프(LangGraph), quick/deep 모델 이원화로 비용 조절, 데이터 벤더 체인(`data_vendors` 가 곧 fallback 순서, 조용한 우회 금지), SEC EDGAR "as filed" PIT 재무(재작성 전 원래 값 사용), 도구가 날짜를 인자가 아닌 그래프 상태에서 받아 미래 날짜를 원천 차단하는 방식(#1331), 결정 로그 → 실현 알파 → 회고문을 프롬프트에 넣는 루프(교훈에도 PIT 가드, #1251), "관측하지 못한 창은 부재가 아니라 unavailable"로 보고하는 원칙, Hold 로 떨어뜨리지 않고 `REVIEW` 로 표시하는 등급 파서.
