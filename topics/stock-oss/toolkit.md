# 개인 투자 툴킷 — stock-oss

조사한 레포 중 **실제로 쓸 만한 것**만 골랐다. 기준은 정밀 판정의 개인 활용도 축 **P≥4 인 12개 + worldmonitor**(정밀 판정 없음, 심층 T 4)다. 근거는 `topics/stock-oss/notes/<owner>__<repo>.md` 이고, 이번 회차에 설치·구동하지는 않았다 — 실행법은 노트의 설치·의존성 기록에서 가져왔다.

> 갱신 (2026-10-06): 본문은 2026-09-28 노트 기준이다. 그 뒤 바뀐 것 — prism-insight 는 README 에 거래별 단순합(+355.3%)과 10슬롯 계좌 수익률(+35.2%)을 나란히 싣고, 계좌 수익률이 같은 기간 KOSPI(+103.5%)에 뒤졌다고 밝혔고, vibe-trading 은 모델 학습 컷오프 노출 경고를 넣었으며(PR #1618, 컷오프는 사용자가 입력), ai-hedge-fund 는 해시체인 원장 페이퍼 트레이딩을 추가했다. 세부는 각 노트 머리의 갱신 줄.

쓰기 시작하면 `log.md` 에 `## [YYYY-MM-DD] use | owner/repo` 를 남긴다(UTC 날짜). 원 계획 §2.3 의 두 번째 가설(4주간 주 1회 이상)을 그걸로 잰다.

---

## 1. 한국 데이터 — 여기부터 시작한다

### financedata/FinanceDataReader (P5 · ★1.5k) — 국내 시세·상장목록의 기본
- **용도**: KRX·네이버·Yahoo·FRED 를 한 API 로. 국내 개인 퀀트의 사실상 표준.
- **실행**: `pip install finance-datareader` → `fdr.DataReader('005930', '2020')` · `fdr.StockListing('KRX')` · `fdr.SnapDataReader('NAVER/FINSTATE-2Q/005930')` · `fdr.DataReader('USD/KRW')`
- **신뢰 주의**
  - `StockListing('KRX')`·KS11 은 **메인테이너 계정으로 모은 GitHub CSV** 다. KRX 로그인 필수화(2026-02) 뒤의 우회책이고 **90일 비밀번호 주기마다 1~2일 끊긴다**. 전일 목록을 로컬에 두고 404 면 그걸 쓰는 폴백을 반드시 짠다.
  - `KRX:005930`(KRX 직접 가격)은 로그인화 이후 지원 목록에서 빠졌다. README 예시를 믿지 않는다.
  - 네이버 개편(2026-09-10) 뒤 기본 시세·재무 경로가 깨질 수 있다. 버전을 자주 올리고 결과를 검증한다.
  - 거래량은 수정 전 값이고 상장폐지 종목은 수정주가가 없다. 백테스트에 쓰면 직접 보정한다.
- **쓸 곳**: 리서치·스크리닝·장기 백테스트의 입력. 실시간 매매 신호 소스로는 증권사 API 를 쓴다.

### financedata/OpenDartReader (P5 · ★477) — 국내 공시·재무
- **용도**: 금감원 Open DART 를 pandas·CLI 로 감싼 MIT 래퍼. 고유번호 변환·주요사항·지분공시가 바로 나온다.
- **실행**: Open DART 키를 `.env` 의 `DART_API_KEY` 로 → `uv tool install opendartreader` → `dart list "삼성전자" --start 2026-01-01 --pretty` · `dart finstate "005930, 000660" 2025` (Python 3.13+)
- **신뢰 주의**
  - `list_date_ex()` 는 기본 `cache=True` 라 같은 날짜를 파일 캐시로 계속 돌려준다. **당일 공시 폴링에는 반드시 `cache=False`** — 다만 그 경로는 headers 를 쿼리 파라미터 자리로 넘겨 User-Agent 가 빠진다.
  - 모든 요청에 timeout·재시도가 없다. 워커에 넣으면 바깥에서 타임아웃을 건다.
  - `list_presenter` 는 `verify=False` 로 TLS 검증을 끈다.
  - 실행 디렉터리에 `docs_cache/` 를 무기한 쌓는다. 작업 디렉터리를 정해 두고 주기적으로 지운다.
  - 이름 조회는 첫 일치 회사를 고른다. **종목코드 6자리나 고유번호 8자리로 부른다.**
- **공백**: 재무 표준화·본문 검색·실적 알림은 범위 밖이라고 메인테이너가 명시했다.

### chrisryugj/korean-dart-mcp (P5 · ★103) — 에이전트로 공시 묻기
- **용도**: OpenDART 를 18개 MCP 도구로. XBRL 합산 검증·HWP/PDF 첨부 마크다운화·내부자/회계 리스크 시그널.
- **실행**: `DART_API_KEY` 설정 후 수동 JSON 등록 → Claude 에게 "삼성전자 최근 3년 지분 변동" 처럼 묻는다.
- **신뢰 주의**
  - **플러그인 매니페스트가 `npx -y korean-dart-mcp@latest` 다.** 클라이언트를 켤 때마다 최신 npm 판을 검증 없이 받아 실행한다 — 패키지 탈취에 그대로 노출된다. **버전을 고정해 수동 등록한다.**
  - `setup` 이 Claude Desktop·Cursor·VS Code 설정 파일을 직접 고친다. 실행 전 백업한다.
  - `insider_signal` 의 `strong_buy_cluster` 를 장내매수로 읽지 않는다. 주식보상·증여·유상증자까지 증가로 센다.
  - `treasury_buy` 프리셋에 신탁계약 해지 공시가 섞인다.
  - `get_xbrl format=raw` 는 LLM 이 준 경로에 ZIP 을 푼다.

---

## 2. 해외 데이터·공시

### ranaroussi/yfinance (P5 · ★25k) — 무료 시세의 기본
- **실행**: `pip install yfinance` → `yf.download(["005930.KS","AAPL"], period="5y")` (한국은 `.KS`/`.KQ`)
- **신뢰 주의**: ① 루프 호출은 429 로 막힌다 — 간격을 두고 로컬(SQLite·parquet)에 증분 적재 ② 한국 배당·비미국 가격 오류가 잦다. `repair=True` 를 켜고 KRX·증권사 API 와 교차 검증 ③ **약관상 개인 용도 한정 — 이 데이터로 서비스를 만들어 재배포하면 안 된다** ④ 몇 주 간격으로 깨진다.
- 실매매 신호의 **유일한** 소스로 쓰지 않는다.

### dgunning/edgartools (P5 · ★2.8k) — SEC 공시
- **실행**: `pip install edgartools` → `set_identity("이름 이메일")` → `Company("AAPL").get_financials().income_statement()`. 13F 는 `get_filings(form="13F-HR").latest().obj().holdings`, 내부자는 `form="4"`.
- **신뢰 주의**: ① SEC 초당 10회 제한 ② **표준화 재무제표는 회사별 커스텀 개념 때문에 틀릴 수 있다** — 숫자는 원문과 대조 ③ Q4 는 10-K 에서 역산해야 하고 8-K 실적 표는 구조화가 불완전 ④ 의존성 상한이 촘촘하니 별도 venv ⑤ `install_skill()` 은 `~/.claude/skills/` 에 파일을 쓴다.

### openbb-finance/openbb (P5 · ★73k) — 공급원 통합
- **실행**: `pip install openbb` (Python 3.9.21~3.12) → `obb.equity.price.historical(...)`. `openbb-mcp` 로 Claude 에 붙일 수 있다.
- **신뢰 주의**: **한국은 yfinance `.KS`/`.KQ` 가격 정도뿐이고 재무·공시·수급이 없다**(한국투자증권 공급원 제안 #7386 은 거절됐다). 무료 공급원은 수시로 깨지고 README 가 정확성을 보장하지 않는다. `[all]` 은 의존성이 무겁다. MCP 를 `0.0.0.0` 으로 열면 인증을 따로 챙긴다.

---

## 3. 성과·분석

### ranaroussi/quantstats (P5 · ★7.7k) — 성과·위험 티어시트
- **실행**: `pip install quantstats` → `qs.reports.html(returns, "SPY", output="report.html")`
- **신뢰 주의**
  - 입력은 일간 **수익률**이다. 가격·평가금액을 넣으면 안 된다. **입출금이 섞인 계좌 평가금액으로 바로 수익률을 만들면 틀린다** — 시간가중수익률로 먼저 바꾼다.
  - KRX 는 연 거래일이 252일과 다르고 코인은 365일이다. `periods_per_year` 를 맞춘다. 0.0.85 이상을 쓰고 `qs.stats` 와 리포트 값을 대조한다.
  - **Win Rate·Profit Factor·Kelly 는 거래가 아니라 "기간" 단위 지표다.** 스윙 매매 평가 근거로 쓰지 않는다.
  - PR·이슈가 적체돼 있다.
- **쓸 곳**: 내 계좌 수익률 vs KOSPI·SPY 월간 티어시트.

### shashankvemuri/finance (P5 · ★4.3k) — 미국 퀀트 연구 패키지
- **실행**: `pip install -e '.[data,portfolio,models]'` (Python 3.12+). **예제 기본값이 합성 데이터라 `--live` 를 반드시 붙인다.**
- **쓸 만한 것**: 정규화 OHLCV, 누출 방지·비용 반영 `backtest`(t+1 시가 체결), `select_strategy` 의 학습/holdout 분리, `efficient_frontier`.
- **신뢰 주의**: 미국 전용. 구성종목이 현재 스냅샷이라 **과거 유니버스 백테스트에 생존 편향**이 있다. 2026-09 재작성 직후라 API 가 불안정하다(버전 `0.0.0`, PyPI 미배포) — **커밋 해시를 고정**한다.

### hkuds/vibe-trading (P4 · ★34k) — 자연어 백테스트
- **실행**: `pip install vibe-trading-ai` → `vibe-trading init` → `vibe-trading serve --port 8899`. 한국은 `005930.KS` 로 pykrx·Yahoo. 인텔 맥은 `numba==0.62.1 llvmlite==0.45.1` 고정.
- **쓸 만한 것**: ① **Shadow Account** — 내 거래내역으로 처분효과·과매매·추격매수 진단(파서는 중국 증권사·일반 CSV 만 지원하니 한국 내역은 CSV 로 변환) ② **`KoreaEquity` 엔진** — 한국 세금·호가 단위 반영 ③ 토스·KIS 읽기 전용 커넥터.
- **신뢰 주의**: 포트폴리오 평가 통화가 USD·HKD·CNY 뿐이라 KRW 계좌가 들어가는지 확인이 필요하다. **LLM 기억 누출 경고가 아직 없다.**

---

## 4. AI 분석 — 리서치 초안으로만

> 아래 넷은 **매매 신호가 아니라 리서치 초안 생성기**로만 쓴다. 근거는 §5 다.

### tauricresearch/tradingagents (P4 · 심층 T **2** · ★109k)
- **실행**: `pip install .` (Python 3.12) 또는 `docker compose run --rm tradingagents` → 대화형 CLI. 코드는 `TradingAgentsGraph(config).propagate("005930.KS", "YYYY-MM-DD")`.
- **신뢰 주의**: ① 한국은 `.KS`/`.KQ` 로 돌지만 재무·뉴스가 yfinance 뿐이다(DART 없음) ② **실행마다 결과가 다르다** — 한 번의 등급을 신호로 쓰지 말고 여러 번 돌려 분포를 본다 ③ **과거 날짜 백테스트는 모델이 그 구간을 기억할 수 있다(#805)** — 쓰는 모델의 컷오프 이후 구간만 믿는다. 비용·슬리피지가 없다 ④ 결정 1회에 LLM 호출 16~22회 — `quick_think_llm` 을 싼 모델로, `max_debate_rounds` 는 1 ⑤ **실제 쓸모는 "종목 하나에 대한 다관점 리서치 보고서 생성기" 정도다.**

### dragon1086/prism-insight (P4 · ★767) — 한국 종목 리포트
- **실행**: 미국 종목만 보려면 `python3 demo.py NVDA --language ko`. 한국 전체 파이프라인은 설정 파일 4종 + 외부 키 5개 이상 + cron + SQLite 가 필요하다.
- **신뢰 주의**: ① 2026-09-11 **KIS 단일 제공자 전환** 뒤 한국 데이터는 KIS 앱키가 있어야 돈다(2026-10-04 UTC 개편 a4d235f 로 README 도 KIS 키 안내로 바뀌었다) ② 무겁다 — **직접 돌리기보다 무료 텔레그램 채널·대시보드를 소비하는 편이 싸다** ③ **채널의 매수 신호를 따라 할 근거로 성과표를 쓰지 않는다**(§5) ④ 쓸모는 `demo.py 005930` 의 DART 근거 인용 리포트와 1차 스크리닝 ⑤ 월 $300 대 API 비용 구조.

### wbh604/uzi-skill (P4 · ★7k) — 종목 채점 리포트
- **실행**: 격리된 venv 에 `pip install -r requirements.txt` → `python run.py 600519.SH --depth lite --no-browser`. **실제 가치는 A주·홍콩 종목에 있다** — `005930.KS` 는 Yahoo 수준이다.
- **신뢰 주의(보안)**: 플러그인으로 설치하면 SessionStart 훅이 세션마다 백그라운드 Python 을 실행하고 에이전트 컨텍스트에 안내를 주입한다(`UZI_NO_UPDATE_CHECK=1` 로 끔). README 는 보안 검사를 우회하는 `curl … | bash` 를 권한다. **설치하지 말고 clone 해서 CLI 로만 쓴다.**
- **신뢰 주의(분석)**: 점수가 키워드·규칙 화이트리스트에 민감하고 계산 버그가 여러 번 보고됐다(DCF ¥0, PE 분위수 파싱 오류로 점수가 늘 9 등). **리포트 숫자를 원자료와 대조한다.**

### koala73/worldmonitor (심층 T 4 · ★—) — 거시 점검판
- **실행**: **가장 싼 사용법은 `finance.worldmonitor.app` 을 무료로 보는 것이다.** 거시 체제·수익률 곡선·금융 스트레스·Fear & Greed·COT·캘린더를 한 화면에서 본다. 계정도 필요 없다.
- **신뢰 주의**: ① **한국에는 약하다** — 카탈로그에 KOSPI 와 삼성전자뿐 ② 유료 종목 분석의 "Strong buy"·"Profitable" 배지는 **6개월·비용 없는 기술 지표 재생 결과**라 매매 근거로 약하다 ③ 공식 데스크톱 앱은 메인테이너가 "neglected" 라고 인정했다. 웹을 쓴다. 사칭 레포가 있다.

---

## 5. AI 신호를 다루는 규칙

원 계획 §1.2 문제 3 의 결론이다. **백테스트 수익률은 믿지 않는다.**

- LLM 은 학습 컷오프 이전 가격을 기억한다. 그 구간의 백테스트는 회상이지 예측이 아니다 [2504.14765]. 조사에서도 확인됐다 — 12개 모델 중 10개가 회상을 보였다(tradingagents #805).
- 20년·100종목 이상으로 넓히면 LLM 전략의 우위가 크게 약해지고 [FINSABER 2505.07078], 오염 없는 구간에서는 단순 기준선을 이기는 경우가 드물다 [StockBench 2510.02209, LiveTradeBench 2511.03628].
- **실제 사례 둘**
  - tradingagents 논문의 SR 8.21 은 **3개월·3종목**이고, 누출 반박이 붙었으며 제3자 재현은 **−25%** 였다. 심층 T 2.
  - prism-insight 의 헤드라인 **+244%** 는 비용 없는 단순합이다. 10슬롯으로 환산하면 약 +25% 이고, **같은 기간 KOSPI 는 +62%** 였다 — 진다.
- **그래서 이렇게 쓴다**: ① 성과 주장을 보면 먼저 5가지를 묻는다 — 단순합인가 / 비용을 뺐나 / 벤치마크가 있나 / 모델 컷오프 이후인가 / 표본이 몇 건인가 ② 검증은 **컷오프 이후 구간이나 페이퍼 트레이딩**으로만 한다 ③ AI 출력은 리서치 초안으로 쓰고 숫자는 원자료와 대조한다 ④ 같은 질문을 여러 번 돌려 흔들리면 결론으로 쓰지 않는다.
- 참고할 만한 설계: go-stock 은 AI 추천을 저장했다가 沪深300 대비로 채점하는 **포워드 루프**를 갖고 있고, prism-insight 의 **봉인 리더보드 Stance**(append-only 해시체인·서버 접수 시각)는 자기 성과를 소급 수정할 수 없게 만든 구조다.

---

## 6. 쓰지 않기로 한 것 (P≤3)

| 레포 | P | 이유 |
|---|---|---|
| valuecell-ai/valuecell | 3 | 크립토 자동매매 중심이고 검증 안 된 수익률 리더보드를 둔다(심층 T 3). 설치 이슈가 많다 |
| mathieu2301/tradingview-api | 3 | TradingView 비공식 웹소켓 역공학 — 캡차·세션 만료·**계정 차단** 위험을 사용자가 진다 |
| arvinlovegood/go-stock | 3 | A주 전용 데스크톱 앱. 포워드 채점 루프 설계는 볼 값이 있지만 한국 종목에는 쓸 곳이 없다 |
| virattt/ai-hedge-fund | 3 | **데이터가 저자의 유료 Financial Datasets 에 묶인 미국 전용**(월 $199 불만이 이슈에 반복). 교육용이다 |
| open-dev-society/openstock | 3 | 튜토리얼 기반 무료 대시보드. **KRX 차트가 차단**되고 무료 티어는 비미국 15분 지연 |
| 666ghj/mirofish | 2 | 여론 시뮬레이터. **검증 기록이 없고**(심층 T 1) Zep·토큰 비용이 크다. ★급증은 미디어 효과 |
