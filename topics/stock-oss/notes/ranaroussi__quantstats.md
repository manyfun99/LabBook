---
entity: github:ranaroussi/quantstats
gh_id: 184420323
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [backtest-quant, portfolio-analytics, tearsheet, library, yfinance]
---
## 무엇·어떻게

- 수익률 시계열(pandas Series/DataFrame)을 받아 성과·위험 지표를 계산하고 그림·HTML 티어시트를 만드는 순수 Python 라이브러리다. Apache-2.0 라이선스이고, 조사 시점 clone HEAD `a2448a2`(2026-09-26) 기준 버전은 0.0.85다. 작성자는 yfinance 를 만든 Ran Aroussi 다.
- 구조: `stats.py`(3,600줄, Sharpe·Sortino·CAGR·VaR/CVaR·Kelly·낙폭 등 지표 60여 개), `reports.py`(2,600줄, `metrics`·`plots`·`basic`·`full`·`html`), `_plotting/`(matplotlib·seaborn), `_montecarlo.py`(수익률 순서를 `rng.permutation` 으로 섞는 방식), `utils.py`(`download_returns`·`make_index`·`make_portfolio`), `_compat.py`·`_numpy_compat.py`(pandas·numpy 버전 호환층). `extend_pandas()` 를 부르면 지표를 pandas 객체의 메서드로 붙일 수 있다.
- 데이터 소스: `download_returns` 는 yfinance(`auto_adjust=True` 종가의 `pct_change`)만 쓴다. 벤치마크도 티커 문자열이면 yfinance 로 받는다. 수익률 Series 를 직접 넣으면 외부 호출은 없다.
- LLM: 쓰지 않는다. 1회 실행 비용: 0 이다. 로컬 계산에 yfinance 무료 데이터만 쓴다.
- 입력 한계: 수익률 시계열만 받는다. 거래 단위 데이터나 보유 내역은 받지 않는다. 연 거래일 기본값은 `periods_per_year=252` 다.
- 코드 점검: `subprocess`·`eval`·`exec`·임의 네트워크 호출이 없다. 외부 호출은 `yf.download` 뿐이다. CI 는 테스트용과 PyPI 배포용(release 때 twine 업로드) 두 가지로 평범하다.

## 성과 주장의 신뢰도

1. 주장 목록: 전략 수익률·적중률·"시장 대비 초과" 같은 주장이 없다. README 의 `0.7604779884378278` 은 `qs.stats.sharpe(stock)`(META 매수 보유) 예시 출력이고, 도구가 내세우는 성과가 아니다. `docs/montecarlo.md` 도 방법 설명뿐이다.
2. 면책 문구: README·docs 에 "투자 조언 아님" 같은 문구가 없다. Legal Stuff 절에는 라이선스 안내만 있다.
3. 검증 수단: 성과를 주장하지 않으므로 백테스트 기간·수수료·편향 대책 항목은 해당 없다. 대신 지표 계산이 맞는지가 신뢰 문제다. 2026년에도 계산 오류가 이어서 보고·수정되고 있다. `rar()` 가 연 무위험수익률을 매 기간 뺀 오류(#552), Kelly 계산 오류(#535·#537), Probabilistic Sharpe 가 1을 넘는 오류(#550), 결측을 0 수익률로 채운 문제(#546), `qs.stats` 와 `qs.reports.metrics` 결과 불일치(#556, 열림)가 있다. 또 Win Rate·Profit Factor·Payoff 는 거래가 아니라 기간 단위로 계산한다. README 에 "Period-Based vs Trade-Based Metrics" 절을 따로 둘 정도로 오해가 잦다(#493). 몬테카를로는 순서만 섞으므로 최종 누적수익이 모든 경로에서 같다. 경로 위험(낙폭·bust)만 달라진다(docs 에도 적혀 있다).
4. 판정: 성과를 주장하지 않는 분석 도구라 앵커 5에 해당한다. 다만 지표 계산 정확도는 버전마다 다르다는 점을 따로 새겨 둔다.

심층 T 5 (판정 T 5) — 성과를 주장하지 않는 지표·리포트 라이브러리이고, 신뢰 문제는 주장이 아니라 계산 버그 쪽에 있다

## 수요 신호

이슈는 반응순·댓글순 상위 60개가 모두 닫혀 있다. 대부분 계산·pandas/numpy 호환성 버그라 신호에서 뺐다. 신호는 `.cache/signals/ranaroussi__quantstats.jsonl` 에 16건(demand 14, pain 2, gap 0)을 넣었다. 기능 요청은 Discussions(35개)에 더 많았다.

- 웹앱 삽입·인터랙티브 차트 (가장 큼): Streamlit 에 `reports.html` 을 띄우려는 요청(#179, 반응 6·댓글 8)과 Plotly 로 바꿔 인터랙티브하게 보려는 시도(#179 댓글), 리포트에 plotly/Chart.js 같은 인터랙티브 차트를 달라는 요청(#135, D474)이 있다. 사람들이 "파이썬 노트북 밖에서 공유·조작 가능한 티어시트"를 원한다는 뜻이다.
- 여러 포트폴리오·벤치마크 비교: 리포트 하나에 포트폴리오 하나만 들어간다는 불만(#161), 벤치마크·전략을 여럿 넣고 싶다는 요청(D208)이 있다.
- 실제 계좌(거래 내역) 기반 분석: 매수·매도가 섞인 개인 포트폴리오를 분석하고 싶다는 요청(D141), 거래 단위 지표를 달라는 요청(#493, D362), 명목금액 없이 현금 손익으로 분석하고 싶다는 요청(D250)이 있다. 수익률 시계열만 받는 설계의 빈틈이다. D503 에서는 거래 내역을 입력하면 보유를 재구성하는 앱을 따로 만들었다는 사용자도 있다.
- 주기·시장 확장: 인트라데이(D169), 주간·월간 주기 파라미터(D312), 비미국 종목과 수동 데이터 입력(#131, 브라질 #146, GIFT NIFTY #538), 다국어 i18n(D324), 표를 csv/excel/gsheet 로 내보내기(#80)가 있다.
- 유지보수 신뢰(pain): "방치됐나?" 이슈(#323, 반응 13)가 반응 1위다. 이슈 200여 개를 설명 없이 한꺼번에 닫은 일에 대한 항의(#473)도 있다. 2025~2026년에 다시 활발해졌지만(0.0.64→0.0.85), 한동안 포크(quantstats_lumi)로 옮겨 간 사용자가 있었다.
- 한국 시장·한국어: 직접 요청은 없다. i18n 요청(D324)과 비미국 데이터 요청이 가장 가깝다.
- 호스팅 버전 요청·API 비용 불만: 없다. LLM 을 쓰지 않고 무료 데이터만 쓰기 때문이다.

## 파생·상용화

- 포크: 상위 10개가 모두 ★11 이하다(gauss314 11, gnzsnz/quantstats-cagr 9 — CAGR 수정). 의미 있는 파생은 GitHub 포크가 아니라 별도 레포인 `Lumiwealth/quantstats_lumi`(★152, 2026-09 push)다. 원본이 방치되던 시기에 갈라져 나왔다(#323 댓글). 거래 기반 지표를 뺐고, Lumiwealth 의 트레이딩봇 프레임워크 Lumibot 백테스트 티어시트의 엔진으로 쓰인다(Lumibot 문서 "Tearsheet HTML"). 라이브러리 자체는 무료 공개다.
- 그 밖의 파생: `marketcalls/openstatz`(티커 입력·CSV 업로드 대시보드 `serve`, 오프라인 HTML 티어시트), `Jebel-Quant/jquantstats`, PyPI `QuantStatsQd`, `joedenis/quantstats` 같은 재구현·변형이 있다.
- 유료 서비스: 웹 검색 3회로는 quantstats 를 감싼 유료 SaaS 를 찾지 못했다. 티어시트를 웹에서 생성해 주는 무료 대시보드(openstatz)는 있다.

## 내 투자에 쓰려면

- 설치는 `pip install quantstats` 로 하고(이번 조사에서는 실행하지 않았다), 예시는 `qs.reports.html(returns, "SPY", output="report.html")` 다. 한국 종목은 yfinance 티커(`005930.KS`, `^KS11`)로 `download_returns` 해도 되지만, 증권사 계좌 수익률은 직접 일간 수익률 Series 로 만들어 넣어야 한다.
- 주의점
  - 입력은 일간 **수익률**이다. 가격·평가금액을 넣으면 안 된다(`utils.to_returns` 로 바꾼다). 입출금이 섞인 계좌 평가금액으로 바로 수익률을 만들면 틀린다. 시간가중수익률로 먼저 바꿔야 한다.
  - KRX 는 연 거래일이 252일과 조금 다르고 코인은 365일이므로 `periods_per_year` 를 맞춘다. rf 를 0이 아닌 값으로 쓰면 버전별 버그가 잦았으니 0.0.85 이상을 쓰고, 주요 수치는 `qs.stats` 와 리포트 값을 서로 대조한다(#556).
  - Win Rate·Profit Factor·Kelly·Risk of Ruin 은 거래가 아니라 "기간" 단위 지표다. 스윙 매매를 평가하는 근거로 쓰지 않는다.
  - 몬테카를로 bust/goal 확률은 수익률 순서만 섞은 결과다. 분포가 바뀌는 상황(체제 변화)은 반영하지 않는다.
- 쓸 곳: 내 전략·계좌 수익률과 KOSPI·SPY 를 비교하는 월간 티어시트, 백테스트 결과의 표준 지표 산출기로 쓴다.

## 인디 관점 메모

- 공백
  - "코드 없이 쓰는 티어시트": 수요 신호의 중심은 Streamlit·인터랙티브·공유다. 증권사 거래 내역 CSV 를 올리면 보유를 재구성해 시간가중수익률을 계산하고, quantstats 티어시트를 인터랙티브 웹으로 보여 주는 호스팅 서비스는 조사 범위에서 보이지 않았다. 특히 한국 증권사 CSV·KOSPI 벤치마크·한국어 리포트를 갖춘 것은 없다.
  - 거래 단위 지표 + 수익률 지표 통합: 원본은 설계상 거래 단위 지표를 거부했고(#493), 포크는 그 지표를 지웠다. 두 입력을 함께 받아 정확히 나누어 보여 주는 도구가 비어 있다.
  - 여러 전략·벤치마크를 한 리포트에서 비교하는 기능과 csv/excel 내보내기도 오래된 요청이다.
- 차용할 부분
  - Apache-2.0 이라 지표 엔진으로 그대로 쓸 수 있다. `report.html` 템플릿과 `template_path` 로 리포트를 바꿔 입힐 수 있고, "Period-Based vs Trade-Based" 설명 방식도 참고할 만하다.
  - 버전 호환층(`_compat.py`)과 최근 버그 수정 기록(CHANGELOG)은 지표를 직접 구현할 때 확인할 목록으로 쓸 만하다(rf 연환산, 결측 처리, 벤치마크 날짜 맞추기).
- 위험: 계산 정확도 이슈가 계속 나온다. 상용화하려면 버전을 고정하고, 핵심 지표는 회귀 테스트로 교차 검증해야 한다.
