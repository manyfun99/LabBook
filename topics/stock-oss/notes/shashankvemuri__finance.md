---
entity: github:shashankvemuri/finance
gh_id: 239389449
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [backtest-quant, python-library, toolkit, us-market, data-scraping]
---
## 무엇·어떻게

- 조사 시점 HEAD `20799035` (2026-09-11 머지 #69). ★4291, 포크 374, Discussions 꺼짐.
- **2026-09-07 에 전면 재작성됐다.** 그 전(2020~2025)에는 "150+ Python for Finance programs" 라는 독립 스크립트 모음(`find_stocks`·`machine_learning`·`portfolio_strategies`… + 번들된 `chromedriver` 바이너리·티커 CSV)이었다. 재작성 커밋("retire audited legacy programs and obsolete bundled assets")에서 레거시를 모두 걷어내고 `src/finance/` 패키지(`finance-toolkit`, Python ≥3.12, PyPI 미배포)로 바꿨다. 브랜치명 `codex/*` 로 보아 코딩 에이전트로 재작성한 것으로 보인다. d30 +100 은 이 재작성 시점과 겹친다.
- 구조: `data`(Yahoo·Finviz·Nasdaq·CFTC·TradingView scanner·Motley Fool 트랜스크립트·RSS·Reddit) → `indicators`·`analytics`·`screening`·`portfolio`(계산) → `strategies`(목표 비중) → `backtesting`(t 종가 신호 → t+1 시가 체결, 수수료·슬리피지·공매도 대차비용, 손절·익절·트레일링) → `models`(ridge·boosting·ARIMA·PCA·레짐·클러스터링, 선택적 LSTM/CNN·Prophet) → `reports`·`apps/research.py`(Streamlit) → `integrations`(이메일·Twilio SMS·웹훅, Alpaca 기본 paper 엔드포인트, 실거래는 `allow_live=True` 필요).
- 규모: `src` 약 5.1k 줄, 예제·앱 약 0.7k 줄, 테스트 15개 파일. CI 는 3.12~3.14 × core/full 매트릭스로 오프라인 테스트, 실데이터 테스트는 `--live -m integration` 으로 따로 돈다.
- 데이터 소스는 전부 무료 공개·비공식 엔드포인트다. LLM 은 쓰지 않고(감성 분석은 VADER), 1회 실행 비용은 0 이다. Alpaca·Twilio 는 사용자 자격증명이 있을 때만 쓴다.
- 문서(`docs/methodology.md`)가 지표 초기화, 체결 규칙, 벤치마크 정의, 생존 편향(S&P500·거래소 목록은 현재 스냅샷), 발표일과 기준일 구분(CFTC·내부자 거래)까지 적어 둬서 이례적으로 꼼꼼하다.

## 성과 주장의 신뢰도

1. **주장 목록** — 현재 HEAD 의 README·`docs/*.md`·예제·앱·코드 주석에서 수익률·적중률·샤프·초과수익 주장을 찾지 못했다. 노트북·스크린샷·결과 이미지 파일도 없다. `cagr`·`sharpe` 는 `analytics/returns.py` 의 지표 계산 함수로만 나온다. 레거시 README(2025-05 시점)에도 성과 주장은 없었다.
   오히려 주장을 부정하는 문장이 곳곳에 있다. README "Forecast experiments report held-out errors against simple baselines and make no claim of predictive advantage.", methodology "No model is advertised as predictive alpha.", "They are causal rule implementations, not evidence of profitability.", 예제 `forecast_time_series.py` 출력 "predictive skill is not assumed."
2. **면책** — README 끝 "for educational purposes only and should not be considered professional investment advice." 1에서 주장이 나오지 않았으므로 이 문구와 별개로 5점을 받을 수 있다.
3. **검증 수단** (성과를 주장하지 않는 대신 도구가 제공하는 검증 장치)
   - 백테스트 기간·종목: 예제 기본값은 합성 데이터이고 `--live` 는 단일 종목(AAPL 등) 위주다. 넓은 종목군 평가는 없다.
   - 수수료·슬리피지: 있음. 공매도 대차비용·파산 시 예외 처리까지 모델링한다. 시장충격·유동성·배당 현금흐름은 없다고 명시한다.
   - look-ahead: 신호는 t 종가, 체결은 t+1 시가. prefix-invariance 테스트로 미래 데이터가 과거 신호·자산곡선을 바꾸지 않는지 확인한다. 예측은 시간순 holdout 에서 horizon 만큼 purge 하고, 스케일링은 학습 구간에만 맞추고, 0 수익률 기준선과 비교한다. `select_strategy` 는 학습 70% 에서 고른 1개만 holdout 에서 돌린다.
   - 생존 편향: 대책은 없지만 "Historical backtests using them have survivorship bias." 라고 명시한다.
   - LLM 컷오프: LLM 을 쓰지 않으므로 해당 없음. 포워드·페이퍼 기록: 없음(Alpaca paper 연동만 있고 실제 기록은 없다).
4. **판정** — 데이터·계산·백테스트 인프라이고 성과 주장이 없다. 이 점은 앵커 5의 "성과를 주장하지 않는 도구"에 해당한다.

심층 T 5 (판정 T 5) — 성과 주장이 없고, 오히려 누출 방지·기준선 비교·편향 경고를 문서와 테스트로 강제하는 연구 도구다.

## 수요 신호

이슈 24개를 모두 봤다(반응순·댓글순 상위 30 조회 결과가 전체와 같다). 반응 수는 모두 0, 댓글도 최대 4개라 신호는 약하다. 구성: 레거시 스크립트 실행 오류(#14·#26·#28·#39·#40), 기여 제안·과제 배정 요청(#6·#12·#29·#30·#31·#54), 인도 금융 기사 스팸(#45~#51), 빈 이슈(#25·#57). 재작성 뒤 관리자가 오래된 이슈를 일괄 답변·종료했다(2026-09).

- demand — #6 옵션 트레이딩 스크립트 추가 제안(w4). 기여자가 먼저 제안한 것이지만, 옵션 기능이 없다는 수요로 본다. #12(PPO 자동매매)·#31(트레이딩 봇)·#54(GB/LSTM 하이브리드)는 자기 작업을 알리거나 과제 배정을 요청하는 성격이라 넣지 않았다. 관리자는 #31 에 "live brokerage automation is outside the project scope" 라고 답했다.
- pain — 설치 어려움. #13 무엇을 설치해야 하는지 모르겠다는 문의(w1), #33 초보자의 `No module named Numpy`(w0). 비개발자·입문자가 스크립트 모음을 직접 돌리다 막힌 사례다.
- gap — README 가 "Current constituents and fundamentals are snapshots, not historical point-in-time inputs." 라고 인정한다. 무료로 쓸 수 있는 point-in-time 구성종목·펀더멘털 데이터가 없다는 공백이다.
- 넣지 않은 것: 공개 스크래핑이 깨진 버그(#14 FMP 403, #26 Finviz 403·NLTK 사전, #40 pandas-datareader Yahoo 경로 붕괴). "무료 데이터 소스가 자주 깨진다"는 고통이 반복되지만, 모두 개별 버그 보고라 pain 으로 넣지 않고 여기에만 적는다.
- 한국 시장·한국어·호스팅 버전·API 비용 불만: 없음.

## 파생·상용화

- 인기 포크 상위 10개가 모두 ★4 이하이고, 레거시 스크립트 모음을 그대로 복사한 것이다(`mdancho84/150_quant_finance_programs` ★4 등). `ACquantclub/Quick-Python-Scripts-for-Quant-Finance` 처럼 이름을 바꾼 복사본도 있다.
- 이 레포를 감싼 유료 서비스는 찾지 못했다(웹 검색 2회). 뉴스레터(QuantSeeker Substack)에 레포 소개로 언급된 정도다.
- 상용 연결 시도: 열린 PR #71(2026-09-27)이 Adanos 의 유료 API(Reddit·X·News·Polymarket 일별 감성)를 선택적 reader 로 넣자고 제안한다. 작성자가 "I contribute on behalf of Adanos." 라고 밝혔고, `adanos-software/Finance` 포크도 있다. 별이 많은 도구 레포에 데이터 벤더가 어댑터 PR 로 들어오는 유통 경로의 사례다.

## 내 투자에 쓰려면

- `python -m venv` 후 `pip install -e '.[data,portfolio,models]'`(Python 3.12+). 예제는 기본값이 합성 데이터이므로 반드시 `--live` 를 붙여야 실데이터로 돈다.
- 쓸 만한 것: `YahooFinance().history` 정규화 OHLCV, 지표(초기화 규칙이 문서화돼 있다), `backtest`(t+1 시가 체결·비용 반영), `select_strategy` 의 학습/holdout 분리, `efficient_frontier`, Finviz 스크리너 페이지네이션 검증. Streamlit 앱 하나로 차트·전략·밸류에이션·배분을 한 번에 볼 수 있다.
- 주의: 미국 시장 전용이다(Finviz·Nasdaq·S&P500). 한국 종목은 Yahoo 티커(`005930.KS`)로 가격만 받을 수 있고, 스크리닝·펀더멘털 어댑터는 없다. 구성종목이 현재 스냅샷이라 과거 유니버스 백테스트에는 생존 편향이 있다. Finviz·TradingView scanner 는 비공식이라 언제든 깨질 수 있다. Alpaca 는 paper 가 기본이다.
- 2026-09 재작성 직후라 API 가 안정됐다고 보기 어렵다(버전 `0.0.0`, PyPI 미배포). 커밋 해시를 고정해서 쓴다.

## 인디 관점 메모

- 차용할 것: `docs/methodology.md` 의 "체결·지표·편향 규약 문서" 형식. 성과를 주장하지 않는 대신 "무엇을 믿으면 안 되는지"를 명시하는 태도는 신뢰를 파는 서비스의 표준 문서로 그대로 쓸 만하다. prefix-invariance 테스트(미래 데이터가 과거 결과를 바꾸지 않는지)는 백테스트 서비스의 검증 기능으로 차용할 수 있다.
- 공백: (1) 무료 point-in-time 유니버스·펀더멘털. 이 레포도 인정하는 한계이고, 한국 시장(KRX 과거 구성종목·상폐 종목 포함)이라면 더 비어 있다. (2) 설치 없이 쓰는 호스팅 버전. 이슈 #13·#33 처럼 입문자는 환경 구성에서 막힌다. Streamlit 앱을 호스팅하면 바로 풀리는 문제다. (3) 옵션 분석 기능이 없다.
- 시사점: ★4.3k 는 레거시 "150+ 스크립트" 시절의 교육용 인기다. 이슈에 비개발자 수요가 거의 없어 제품 수요의 근거로 쓰기는 약하다. 오히려 벤더가 이 레포에 어댑터 PR 로 들어오려는 시도(#71)가 "별 많은 오픈소스 = 데이터 API 유통 채널"이라는 점을 보여 준다.
