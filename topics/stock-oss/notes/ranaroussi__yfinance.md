---
entity: github:ranaroussi/yfinance
gh_id: 91948540
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [data-mcp, data-source, python-lib, yahoo-finance, scraping]
---
## 무엇·어떻게

- Yahoo Finance 의 비공식 내부 JSON 엔드포인트(`query1`/`query2.finance.yahoo.com`)를 호출해 pandas DataFrame 으로 돌려주는 Python 라이브러리. v1.7.0(clone HEAD `0c5a6c4`), Apache-2.0, ★약 25.4k·포크 3.4k, 2026-09-27 에도 푸시가 있다.
- 구성(`yfinance/`, 약 1.4만 줄): `Ticker`/`Tickers`/`download`(시세·배당·분할), `scrapers/`(재무제표·보유자·애널리스트·펀드), `screener/`(`EquityQuery`·`Screener`), `domain/`(`Sector`·`Industry`·`Market`), `live.py`(`wss://streamer.finance.yahoo.com` WebSocket, protobuf 디코드), `calendars.py`, `search.py`, `lookup.py`.
- 차단 회피가 설계의 중심이다. `_http.py` 는 `curl_cffi` 의 `impersonate="chrome"` 으로 브라우저 TLS 지문(JA3/JA4)을 흉내 내고, 없으면 `requests` 에 크롬 User-Agent 를 붙여 폴백한다. `data.py` 의 `YfData`(싱글턴)가 쿠키·crumb 을 받아 두고(`/v1/test/getcrumb`), EU 동의 화면(consent form)도 자동 처리한다. 로컬 캐시는 tz·쿠키만 `peewee`(SQLite)로 저장한다.
- `Auth` 클래스: 브라우저에서 Yahoo 로그인 쿠키 `T`·`Y` 를 복사해 넣으면 구독 등급(gold/silver/bronze/free)을 읽는다. 유료 Yahoo 구독 데이터 접근을 염두에 둔 기능이다.
- 가격 보정(`repair=True`): Yahoo 가 주는 100배 오류·통화 혼동·누락 배당을 추정해 고친다. 문서가 스스로 "Only US market data appears perfect, I guess Yahoo doesn't care much about rest of world?" 라고 쓴다.
- 한국 시장: `const.py` 에 `'XKRX': 'KS', 'KQKS': 'KQ'` 매핑이 있어 `005930.KS` 같은 접미사로 조회된다. 다만 #2554 처럼 한국 ETF 배당이 USD/KRW 환율만큼 곱해져 나오는 데이터 오류 보고가 있다.
- LLM 없음. 실행 비용 0원(무료 데이터). 대신 Yahoo 이용약관상 개인 용도 한정이고, 레이트리밋·401·crumb 무효 같은 차단이 수시로 온다.
- 참고: `scrapers/yahoo-keys.txt`(해시 8줄)는 코드 어디서도 참조하지 않는다. 2023년 Yahoo 응답 암호화 시절(#1407·#1329) 복호화 키의 잔재로 보인다. 실행 위험은 없다.

## 성과 주장의 신뢰도

1. 주장 목록 — README·문서(`doc/source`)에 수익률·적중률·샤프 같은 성과 주장이 없다. README 는 "offers a Pythonic way to fetch financial & market data from Yahoo!Ⓡ finance" 로 기능만 설명한다.
2. 면책 문구 — README: "yfinance is **not** affiliated, endorsed, or vetted by Yahoo, Inc. ... intended for research and educational purposes", "Remember - the Yahoo! finance API is intended for personal use only."
3. 검증 수단 — 해당 없음(전략·백테스트가 없는 데이터 도구). 데이터 품질은 `repair` 로직과 `tests/`(단 `pytest.yml.disabled` 로 CI 테스트가 꺼져 있음)로 다룬다.
4. 판정 — 성과를 주장하지 않는 데이터 인프라이므로 앵커 5.

심층 T 5 (판정 T 5) — 성과 주장이 전혀 없는 데이터 수집 라이브러리.

## 수요 신호

상위 이슈(반응·댓글순 60개)는 거의 전부 차단·파손 버그다(#1407 복호화 실패 284반응, #1729 `.info` 404 147댓글, #2422 레이트리밋 141댓글 등). 버그는 신호로 넣지 않았고, 그 속의 대안·비용 발언과 기능 요청만 골랐다. 신호 17개(demand 10, pain 6, gap 1).

- **유료라도 안정적인 소스를 원함**(가장 뚜렷한 수요): "Is there a paid(but not too expensive) version of Yfinance for this.. am fed up of doing this every few weeks now.."(#2422 댓글), "I’m okay with paying a reasonable amount for a robust data source."(#1729 댓글, 4반응), "even if there is any reasonable paid version of yfinance, I am okay with that?"(#732, 인도 NSE 사용자). 반대편에 "a small fee of say $10/month and stop breaking things every few weeks" 라는 가격 앵커가 있다.
- **차단 고통**: VPN·서버를 바꿔도 걸리는 429(#2125, 45), 24시간 넘게 이어지는 블랙리스트(Discussion #2431), 한도가 얼마인지 알 수 없음(Discussion #1513 "how many .info requests can I send in one minute, or hour?").
- **공유 캐시·장기 캐시**: 같은 티커를 수천 명이 반복 조회하니 분산 공유 캐시를 만들자는 제안(#1439), 1개월 단위 영구 캐시 요구(Discussion #2148). 메인테이너는 약관(재배포 금지)을 들어 선을 긋고, 사용자는 "does this mean my personal pet non commercial project can't be hosted on the web?" 라고 되묻는다.
- **대체 소스는 이 프로젝트가 안 한다**(gap): 메인테이너가 다른 무료 소스 통합 제안에 "No, that's for a different project." 로 답했다(#2340 댓글). Yahoo 가 막히면 갈 곳을 라이브러리가 제공하지 않는다.
- **기능 요청**: polars 지원(#1868, 24 — Narwhals 로 이행 논의 진행 중), `download()` MultiIndex 출력 불편(Discussion #2783), 전체 티커 목록(Discussion #2583), 과거 실적 발표일(#1013, 30 — 이후 `get_earnings_dates` 로 일부 해소), 과거 옵션 체인(Discussion #1842, Yahoo 가 제공 안 함).
- **설치 어려움**: 안드로이드 pydroid3 에서 네이티브 의존성 빌드 실패(#1419, 42). 현재는 `curl_cffi` 바이너리 문제로 폴백 경로가 생겼다(#2692 언급).
- **한국 시장·호스팅 버전 요청**: 직접 요청은 없음. 한국 관련 이슈는 #2554·#2553(한국 ETF 배당 환율 오류), #550(cp949 인코딩) 등 버그뿐이다. 호스팅 요청도 이 레포 안에서는 보이지 않는다(대신 외부에 REST 래퍼·MCP 서버가 많다 — 아래).

## 파생·상용화

- 포크: 상위 10개가 모두 ★14 이하(stefan-jansen·asafravid 는 2026-07 까지 동기화)로, 의미 있는 파생 포크는 없다. 파생은 포크가 아니라 **의존 패키지** 형태다.
- REST 래퍼: `Vorckea/yfinance-service`(FastAPI + Docker 로 yfinance 를 HTTP API 로 노출) 같은 오픈소스가 있다.
- MCP 서버: `barvhaim/yfinance-mcp-server`, `narumiruna/yfinance-mcp`, `Alex2Yang97/yahoo-finance-mcp`, PyPI `mcp-yahoo-finance` 등 다수. LLM 에이전트용 무료 시세 소스로 가장 흔히 감싸인다.
- 유료: RapidAPI 에 비공식 Yahoo Finance API(apidojo `yahoo-finance1`/`yh-finance` 등)가 무료 티어(월 수백 요청) + 월 $10~100대 유료 티어로 판매된다. 결국 같은 비공식 Yahoo 데이터를 중간상이 재판매하는 구조다. 이슈 댓글에서도 RapidAPI·Alpha Vantage·roic.ai($67/월)가 대안으로 거론된다.

## 내 투자에 쓰려면

- `pip install yfinance` 후 `yf.download(["005930.KS","AAPL"], period="5y")`, `yf.Ticker("005930.KS").financials` 식으로 쓴다. 한국 종목은 `.KS`(코스피)·`.KQ`(코스닥).
- 주의: ① 반복 루프 호출은 429 로 막히므로 요청 간격을 두고 결과를 로컬(SQLite·parquet)에 쌓아 증분만 받는다. ② 한국 배당·비미국 가격은 오류가 잦으니 `repair=True` 를 켜고 `history_metadata['currency']` 를 확인한다. KRX 공식 데이터나 증권사 API 와 교차 검증이 필요하다. ③ 약관상 개인 용도 한정 — 이 데이터로 서비스를 만들어 재배포하면 안 된다. ④ 몇 주 간격으로 Yahoo 쪽 변경에 깨지므로 버전을 자주 올린다.
- 개인 리서치·백테스트 입력용으로는 충분하지만, 실매매 신호의 유일한 소스로 쓰지 않는다.

## 인디 관점 메모

- 공백: "유료라도 안 깨지는 데이터"에 대한 명확한 지불 의사(월 $10 언급)가 있는데, 이 레포는 대체 소스 통합을 거부하고 약관상 Yahoo 데이터 재판매는 불가하다. 기회는 Yahoo 재판매가 아니라 **라이선스된 소스(KRX·증권사 API·공공데이터)를 yfinance 와 같은 API 모양으로 감싼 호환 레이어** 쪽이다. 특히 한국 시장은 yfinance 품질이 낮고(배당 환율 오류, repair 문서의 비미국 품질 자인) 전용 대안 요청을 받아 줄 곳이 없다.
- 차용할 부분: ① `Ticker`/`download` 의 단순한 API 모양(사실상 표준 인터페이스 — 호환되면 기존 코드·MCP 서버를 그대로 흡수 가능), ② `repair` 의 가격 오류 탐지 휴리스틱, ③ 개인용 로컬 증분 캐시(요구가 반복되는데 공식 지원은 tz·쿠키뿐).
- 주의: 차단 회피(TLS 지문 위장·로그인 쿠키 주입)는 법적·운영 리스크가 커서 상용 제품의 기반으로 삼지 않는다.
