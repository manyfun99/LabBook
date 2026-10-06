---
entity: github:hkuds/vibe-trading
gh_id: 1198306812
judged: 2026-09-27  rubric: v1
t_deep: 4
tags: [llm-agent, multi-agent-swarm, backtest, alpha-zoo, grounding-gate, mcp, broker-connectors, multi-market, korea, mit]
---
> 갱신 (2026-10-06): PR #1618(2026-10-01 머지)로 백테스트 run card 가 `model_training_cutoff` 를 기록하고, 컷오프 이전에 끝나는 구간을 노출 가능으로 표시한다(미설정은 노출로 간주). 아래 "기억 누출 경고 없음" 서술은 2026-09-28 기준이다.

## 무엇·어떻게

홍콩대 데이터 인텔리전스 랩(HKUDS)이 만든 "개인 트레이딩 에이전트"다. 자연어 요청을 데이터 조회 → 전략 코드 생성 → 백테스트 → 보고서로 잇는다. clone HEAD `0244eceaaf8d9e8ae79e2355836802acae3d1fc2`(2026-09-27, v0.1.15 이후), MIT, 2026-04-01 생성, ★3.41만·포크 5,556·watcher 181. PyPI `vibe-trading-ai` 로 배포한다. 6개월 동안 PR 1,157개·이슈 423개가 쌓였다. 릴리스 노트 한 번에 커밋 수백 개가 들어갈 만큼 개발 속도가 빠르다(v0.1.15 "551 commits and 162 merged pull requests"). README 는 7개 언어이고 영어판만 33만 자다. 그 가운데 News 절이 230줄을 차지한다.

- 구조: `agent/`(FastAPI API 서버·CLI·MCP 서버, 도구 74개), `frontend/`(React 19 Web UI), `desktop/electron`, `wiki/`(vibetrading.wiki 정적 사이트)로 나뉜다. 핵심 부품은 다음과 같다.
  - 금융 스킬 90개(`agent/src/skills/*/SKILL.md`)와 스웜 프리셋 30개(투자위원회·퀀트 데스크·리스크 위원회 등 DAG 멀티에이전트)
  - 백테스트 엔진 10종: A주·글로벌·인도·한국·베트남·크립토·선물·FX·복합·옵션. 시장별 수수료·세금·호가 단위·가격제한폭을 모델링한다.
  - 검증 도구 3종(Monte Carlo 순열·Bootstrap Sharpe CI·Walk-Forward)과 run card(해시된 실행 기록·지표→CSV 참조)
  - Alpha Zoo: 공식 알파 462개(Qlib158·Alpha101·GTJA191·학술·PIT 펀더멘털)를 IC 로 채점해 alive/reversed/dead 로 분류한다.
  - Shadow Account: 증권사 거래내역(同花顺·东方财富·富途·CSV)에서 매매 규칙을 뽑아 백테스트하고, 실제 매매와 비교한다.
  - 증권사 커넥터 18종: 읽기 + 모의, 지원하는 곳은 mandate 로 한도를 건 실매매. 모의/실전은 브로커가 서버에서 보고하는 구분자로만 가르고, 에이전트가 설정으로 바꿀 수 없다.
  - IM 채널 15종(Telegram·Slack·WeChat·Feishu 등)과 예약 리서치(cron)
- 설계의 중심은 "grounding gate"다. 모델은 답변에 나오는 수치마다 `figures` 블록에 성격(`observed`·`derived`·`proposed`·`cited`·`count`)을 선언한다. 게이트는 이 선언을 세션의 도구 결과와 대조해, 근거 없는 가격을 지우거나 답변을 거절한다. 여기에 종목 식별 게이트(#887, 종목 식별이 확정되기 전에는 스킬 라우팅을 막음)와 "새 관측 없이 도구 호출 8회면 중단" 규칙이 붙는다. News 절의 대부분이 이 게이트의 오탐·미탐 수정 기록이다.
- 데이터 소스: 28종. 무료 기본 체인은 Yahoo·yfinance·AKShare·mootdx·Tencent·Eastmoney·Sina·Stooq·Baostock·OKX·Binance·ccxt 이고, 키가 있으면 Tushare·Finnhub·Alpha Vantage·Tiingo·FMP·QVeris·Gildata 를 쓴다. SEC EDGAR(13F 포함)·ETF 구성종목·예측시장·arXiv/OpenAlex 도 읽는다. 한국은 `pykrx`(Naver 수정주가 경로, `.KS`/`.KQ`)와 `KoreaEquity` 엔진(±30% 밴드·통합 호가 단위·2026년 매도세 0.20%·롱 온리)으로 지원한다. 커넥터는 KIS(모의투자 서버에서 실제 주문, 실전은 읽기 전용)·토스증권(완전 읽기 전용)·업비트(읽기 + 로컬 모의)가 있다. DART 는 없다.
- LLM: LangChain 기반이고 OpenRouter·OpenAI·Anthropic·DeepSeek·Gemini·Kimi·GLM·Qwen·NVIDIA NIM·Ollama·GitHub Copilot SDK·Codex 등을 쓸 수 있다. 기본값은 OpenRouter + `deepseek/deepseek-v4-pro` 이고, README 는 이를 "~1/10 the cost"의 sweet spot 으로 권한다. 작은 모델은 "answer from memory" 하니 피하라고 적어 두었다.
- 1회 실행 비용: 공개 실측이 없다. 실행마다 `llm_usage.json` 에 토큰 사용량을 남기지만, 결과를 모아 공개한 자료는 없다. D#1611 은 OpenRouter 크레딧 한도 때문에 복잡한 작업을 못 돌렸다고 했다(스웜은 워커 여러 개가 병렬로 LLM 을 부른다). 이번 조사에서는 직접 실행하지 않았다.

## 성과 주장의 신뢰도

1. 주장 목록
   - README(HEAD): 수익률·샤프·적중률 같은 수치 주장이 없다. 수치는 기능 개수(알파 462개·스킬 90개 등)와 버그 수정 기록뿐이다. 품질 주장으로 "PIT data, validation, and run cards", "462 cross-sectional alphas, lookahead-banned at the operator layer"가 있다.
   - 홈페이지(`wiki/home/index.html`): 예시 터미널 출력에 `Backtest BTC-USDT 20/50 MA for 2024` → "return +18.6% max drawdown -7.4%"가 나온다. 시연용 예시이고, 비용·방법 설명은 없다.
   - Research Lab 글(`wiki/research-lab/posts/alpha-191-in-2026.html`, "Which of the 191 GTJA alphas still work in 2026?"): GTJA 191개 알파를 CSI 300·2018~2025 에 돌려 "only 10 (5%) still pass our alive filter"라고 한다. 상위 알파 수치도 싣는다(gtja191_171 "Mean IC = 0.0432, IR = 0.2690"). 스스로 "Treat this post as a signal-quality scan, not a profitability claim"이라고 쓴다.
   - 메인테이너 답변(D#759): "this project doesn't make a profit claim". 논문은 없다(웹 검색에서 Vibe-Trading 논문을 찾지 못했다).
2. 면책 문구: README Disclaimer "It is not investment advice, holds no funds, and runs no execution venue. … This broker-trading capability is experimental and not verified by us against a real broker account … Past performance does not guarantee future results." 1에 수익 주장은 없지만 IC 수치 주장은 있으므로, 이 문구만으로 5점을 주지 않는다.
3. 검증 수단
   - Research Lab IC 연구
     - 기간·종목: CSI 300, 2018-01-02~2025-12-31(약 1,940거래일)이다. 2014년 리포트보다 뒤라 공식 공개 시점 기준 표본 외다. 1일 IC 이고 비용·섹터 중립화는 없다(글이 명시).
     - 생존 편향: Caveats 절이 "current index membership applied across the full 2018–2025 window"라고 인정한다. 그런데 Method 절은 "We use the current index constituents on each rebalance date"라고 적어 서로 모순된다.
     - 내부 불일치: 테마별 표본을 합치면 228개, 생존 알파를 합치면 15개로, 191개·10개와 맞지 않는다. 결론 문단은 생존 알파가 "volume-price interaction, short-horizon volatility"에 몰렸다고 하는데, 표에서는 이 두 테마가 가장 약하다(5%·8%). "the numbers will follow", "final numbers land after the W4.a bench" 같은 작성 중 문구도 남아 있다. 재현 명령의 기간(`--period 2020-2025`)이 본문 기간(2018-2025)과 다르고, 데이터는 Tushare 토큰이 필요하다.
     - LLM 기억 누출: 공식 알파라 LLM 이 신호 경로에 없으므로 해당하지 않는다.
   - 제품 백테스트(사용자가 돌리는 것)
     - look-ahead: 일봉 신호를 `shift(1)` 해 다음 봉 시가에 체결한다. 외부 감사 로드맵(#1207)이 "No lookahead in the daily path"를 확인했고, 알파 연산자 단계의 look-ahead 금지 + 300행 sentinel 테스트가 있다.
     - 비용: 수수료·슬리피지·세금을 시장별로 반영한다(#1207 이 "Slippage direction … tax single vs double-sided rules" 확인). 로드맵 Phase 0~4 에서 수익을 부풀리던 버그가 여럿 고쳐졌다: 공매도 노출 계산, 펀딩비 1/3 과소 부과, 1x 숏 청산 누락, 복합 엔진 가격제한폭 미적용, 거래정지 구간 0% 수익 처리 등.
     - LLM 기억 누출 대책: 없다. #1613(열림)이 "run card doesn't record which model designed the strategy or whether the window predates its training cutoff"라고 지적했고, 이를 담은 PR #1618 은 아직 병합되지 않았다(HEAD 에 cutoff 관련 코드 없음). 메인테이너도 D#275 답글에서 학습 구간 안의 순열·DSR 수치는 "isn't evidence of much"라고 인정했다.
     - 포워드·페이퍼 기록: 프로젝트 차원의 기록은 없다. 공개 벤치마크 참여 제안 D#290(AllocationAgents)·#1390(Headline Arena)에 메인테이너는 "there is no single 'Vibe-Trading agent' whose forecasts we could submit"라며 선을 그었다.
4. 판정: 핵심 제품은 수익을 주장하지 않는 도구·인프라에 가깝고, 메인테이너도 수익 주장을 명시적으로 거부한다. 수치 주장은 Research Lab 의 IC 연구 하나다. 이 글은 기간·유니버스·지표 정의와 한계(비용 없음·생존 편향·1일 IC)를 공개했고, LLM 누출과는 무관하다. 그래서 앵커 3보다 낫다. 하지만 생존 편향을 스스로 인정했고, 비용이 빠졌으며, 방법 서술이 모순되고 합계가 맞지 않아 5에 못 미친다. 따로 짚을 점은 LLM 이 짠 전략을 과거 구간에서 백테스트할 때의 기억 누출 경고가 아직 없다는 것이다. 이는 도구 사용자가 만드는 성과 수치의 신뢰도 문제이고, 판정 요약이 짚은 약점이 HEAD 에서도 그대로다.

심층 T 4 (판정 T 4) — 프로젝트는 수익을 주장하지 않고, 유일한 수치 주장(GTJA191 IC 연구)은 방법을 공개했지만 생존 편향·비용 누락·내부 불일치가 있다. 사용자 백테스트의 LLM 기억 누출 경고는 PR #1618 로 대기 중이다.

## 수요 신호

이슈는 반응순·댓글순 상위 30개씩과 키워드 검색(korea·KIS·toss·upbit·cost·token·hosted·look-ahead·paper trading·install)으로 봤다. Discussions(23개)는 전부 봤다. 반응 수가 극히 낮다: 이슈 최고 반응 2, 최다 댓글 22(#1207, 기여자 로드맵). 상위권 대부분은 기여자가 연 기능 제안·버그라, 최종 사용자 수요는 Discussions 와 초기 이슈에 몰려 있다. 넣은 신호 19개(demand 10·pain 7·gap 2):

- **성과 검증 공백**(가장 뚜렷): #1613 LLM 이 과거 구간의 결말을 알 수 있다(12개 모델 회상 AUC 측정 인용), #1390 "run_card.json proves the backtest was reproducible — not that the judgment was right", D#290 외부 페이퍼 벤치마크로 목표 비중 제출, D#759 "얼마 벌었나", D#275 "the model has the price history in its weights"(13F 신호를 실제 공시일로 옮기자 +30%·적중 90% → +6%·46%), D#906 튀르키예 개발자가 22개월·아키텍처 19개를 거치고도 비용 차감 후 엣지를 증명하지 못했다(댓글 8). #1390·D#290 은 포워드 평가 서비스를 만드는 업체의 제안이다. 이 공백을 노린 제품이 이미 나오고 있다는 뜻이기도 하다.
- **LLM 수치 환각·비용**: D#29 댓글 "有时候大模型不会调用工具实时获取股价而是自己编一个股价"(이 흐름이 식별 게이트 #887 로 이어짐), #37 댓글 "无法连接交易所行情数据库"(약한 모델이 오류 문구를 지어냄), D#1611 "I do not have the money to buy unlimited tokens"(OpenRouter 크레딧 한도).
- **데이터 소스·펀더멘털**: #62 펀더멘털 사전 필터 전략을 옮길 수 없다(반응 1·댓글 9, 기본 전략 백테스트 성공률 "2/5" 실측), #107 mootdx(반응 2), #37 AKShare·동방재부 제한, #998 홍콩 데이터 소스, #542 Yahoo 의존을 줄일 인도 증권사 데이터.
- **실행 연결**: #100 "close the backtest → execution loop", #1435 Robinhood 옵션 주문, #1170 extraETF 포트폴리오 가져오기(독일 ETF 투자자), #1367 증권사 요청 트래커.
- **초보자 UX·설치**: #163 "the current UI feels difficult for non-technical users to understand"(중국어 UI 요청, 메인테이너는 i18n 을 보류했다가 HEAD 에는 한국어 포함 9개 로캘이 있다), D#702 Telegram 설정 문서 부족·macOS venv 실패(댓글 12), D#1035 인텔 맥 설치(llvmlite 휠), #254 예약 실행 요청 → REST 로만 제공돼 "how to using this ?".
- **한국**: #1364(기여자 as950118)가 KIS·토스증권·업비트 커넥터를 요청하고 직접 구현했다(#1407~1409). #693 은 KRX 지원을 추가했다. 최종 사용자의 한국 요청 이슈는 0건이고 한국어 README·UI 는 있다. DART 요청은 없다.
- 호스팅 버전 요청: 없다(이슈·Discussions·키워드 검색 모두 0건).

## 파생·상용화

- 공식 상용판·유료 호스팅: 없다. 웹 검색에서는 "free and open-source"라는 소개 글(coddykit·quantg.in·andrew.ooo·AgentConn 리뷰)만 나온다.
- 셀프 호스팅 템플릿: Railway "Deploy vibe-trading"이 있다. 공식 이미지가 아닌 제3자 Docker 이미지(`xiaosong233/vibe-trading-railway:latest`)를 쓴다. 이 이미지에 API 키를 넣게 되므로 주의해야 한다.
- 사칭: D#475 에 따르면 X 계정 `VibeTrading_HKU`·Virtuals 프로젝트 101845·"VIBE" 토큰이 비공식이다. D#265 는 가짜 Discord 서버가 지갑 연결을 요구했다고 공지한다. 이름값을 노린 크립토 사기가 이미 붙었다.
- 이름이 비슷한 별개 프로젝트: VibeTradingLabs/vibetrading(vibetrading.dev), vibetrader.com(상용 노코드 전략 플랫폼)은 이 레포와 무관하다.
- 포크(★순 상위 10): 모두 ★6 이하로 두드러진 파생이 없다. NieAnSHOW/Vibe-Trading-Desktop(★4, 중국어 "AI 理财专家" 데스크톱판)만 눈에 띈다. pusarla/HKUDS-Vibe-Trading 같은 미러 레포와 SourceForge 미러가 있다.
- 기여 생태계: 포크보다 PR 기여가 활발하다(he-yufeng·shadowinlife·cgycorey 등, AI 보조 기여자용 `AGENT_CONTRIBUTOR_GUIDE.md` 도 있다). 외부 업체(Horus Flow·tickerall·QVeris·Gildata·AIML API·HostDeFi 등)가 데이터·도구 통합 PR 로 들어온다. 레포를 유통 채널로 쓰는 셈이다.
- 스타 신뢰도: ★3.41만 대비 watcher 181(0.5%), 이슈 최고 반응 2 는 비정상적으로 낮다. #163 에 누군가 스타 조작 근거를 나열한 댓글을 달았고, 메인테이너는 이를 삭제했다(메일 인용으로 일부가 남음). 판정 flags 의 `low_watchers` 와 일치한다. 코드·기여 활동 자체는 실체가 있다.

## 내 투자에 쓰려면

- 실행: `pip install vibe-trading-ai` → `vibe-trading init`(.env 생성) → `vibe-trading run -p "..."` 또는 `vibe-trading serve --port 8899` 로 Web UI 를 띄운다. Docker 로도 된다. Claude Desktop 등에는 `vibe-trading-mcp` 로 붙인다. LLM 키 하나만 있으면 되고, 한국 종목은 `005930.KS` 형식으로 pykrx·Yahoo 무료 데이터를 쓴다. 인텔 맥은 `numba==0.62.1 llvmlite==0.45.1` 로 고정해야 한다(D#1035). 이번 조사에서는 설치·실행하지 않았다.
- 쓸 만한 것:
  - (1) Shadow Account: 내 거래내역으로 처분효과·과매매·추격매수를 진단한다. 파서는 중국 증권사 형식과 일반 CSV 만 지원하므로, 한국 증권사 내역은 CSV 로 바꿔야 한다.
  - (2) `KoreaEquity` 엔진: 한국 세금·호가 단위를 반영해 규칙 기반 전략을 검증한다.
  - (3) 토스증권·KIS 읽기 전용 커넥터로 보유 종목을 모아 본다. 다만 포트폴리오 평가 통화가 USD·HKD·CNY 뿐이라 KRW 계좌가 들어가는지 확인이 필요하다. README 는 지원하지 않는 통화는 "fail the source explicitly"라고 쓴다.
- 주의:
  - (1) LLM 이 짠 전략을 과거 구간에서 돌린 수익률은 모델이 그 구간을 기억한 결과일 수 있다. 쓰는 모델의 학습 컷오프 이후 구간만 믿는다(#1613, 경고 기능은 아직 없음).
  - (2) 약한 모델은 도구를 부르지 않고 수치를 지어낸다. README 권장 등급 이상의 모델을 쓰고, grounding gate 가 수치를 지웠는지(`omitted※`) 확인한다.
  - (3) 실매매 경로는 "not verified by us against a real broker account"라고 스스로 밝힌다. 한국은 KIS 모의투자까지만 연결돼 있다.
  - (4) 매일 수십 개 PR 이 병합될 만큼 변경이 잦다. 버전을 고정해 쓴다.
  - (5) 제3자 Railway 이미지는 쓰지 않는다.

## 인디 관점 메모

- 공백:
  - (1) **LLM 기억 누출 감사·포워드 기록**: 이 레포의 가장 깊은 사용자 논의(D#275·D#906·#1613)가 모두 "과거 구간 백테스트는 증거가 안 된다"로 모인다. 메인테이너는 포워드 벤치마크 참여를 거절했다(#1390·D#290). 외부 업체(Headline Arena·AllocationAgents)와 개인(llm-memory-audit)이 각각 이 자리를 노리고 있다. "모델·구간별 누출 위험 검사 + 컷오프 이후 페이퍼 기록 공증"은 이 프레임워크와 TradingAgents·ai-hedge-fund 모두에 붙일 수 있는 공통 층이다.
  - (2) **한국 증권사 거래내역 Shadow Account**: 파서가 중국 증권사 형식만 지원한다. 키움·미래에셋·토스 내역을 파싱해 행동 편향을 진단하는 기능은 한국판 틈새다. 개인정보 문제로 로컬 실행이 강점이 된다.
  - (3) **초보자판**: #163·D#702·D#1611 이 보여 주듯 비개발자가 설치·키·토큰 한도에서 막힌다. 호스팅 요청은 0건이지만, 이는 사용자층이 개발자 위주라서일 수 있다.
  - (4) **펀더멘털 사전 필터**(#62): 공시일 기준 재무로 먼저 거르는 전략은 A주에서도 성공률이 낮다. 한국이라면 DART 공시 시점 재무가 빈칸이다.
- 차용:
  - `figures` 선언 + 도구 결과 대조 grounding gate: 수치를 문장 표현이 아닌 모델의 선언으로 분류하고, 근거 없는 수치는 지운다(`omitted※`).
  - 종목 식별을 확정하기 전에는 스킬 라우팅을 막는 식별 게이트
  - 브로커 서버가 보고하는 구분자로만 모의/실전을 가르는 3단 커넥터 등급(읽기·모의·한도 실매매)
  - mandate(종목 허용 목록·주문·노출 상한)·kill switch·감사 원장
  - 해시된 run card
  - 외부 감사를 "Verified correct, please do not 'fix' these" 절과 단계별 로드맵으로 받는 방식(#1207)
  - `KoreaEquity` 엔진의 KRX 가격제한폭 계산 절차(기준가 호가 단위로 절사 → 가감 → 재절사)
  - 비용 등급별 권장 모델 표
