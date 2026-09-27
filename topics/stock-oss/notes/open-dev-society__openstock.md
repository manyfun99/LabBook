---
entity: github:open-dev-society/openstock
gh_id: 1065936302
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [dashboard, watchlist, nextjs, tradingview-widget, finnhub, self-host, agpl, tutorial-derived]
---
## 무엇·어떻게

Next.js 15(App Router)·React 19로 만든 무료 주식 대시보드 웹앱이다. 관심종목·종목 상세·시장 히트맵·뉴스를 보여 주고, 가입하면 AI 가 쓴 환영 메일과 주간 뉴스 요약 메일을 보낸다. clone HEAD `391e72d780c2c43d1290946057bfa9d530a19e2e`(2026-09-26), 라이선스 AGPL-3.0. 호스팅판은 `openstock-ods.vercel.app`(Vercel `bom1` 리전)에서 운영된다. README 는 JavaScript Mastery 의 유튜브 "Stock Market App Tutorial" 이 바탕이라고 밝힌다.

- 구조: `app/(root)`(dashboard·watchlist·stocks/[symbol]·profile), `app/(marketing)`(랜딩·about·sponsor·api-docs·help), `app/api/quotes`(로그인 사용자만, 한 번에 25종목까지 시세 폴링), `app/api/inngest`, `lib/actions/*`(Finnhub·Adanos·watchlist·alert 서버 액션), `lib/inngest/functions.ts`(백그라운드 작업 4개), `lib/markets.ts`(시장별 타일·종목 묶음), `database/models`(watchlist·alert). 인증은 Better Auth(이메일/비밀번호, 선택적으로 Google·GitHub) + MongoDB.
- 데이터 소스: Finnhub(검색·프로필·뉴스·시세). 무료 키 여러 개를 요청마다 돌려 쓰는 키 풀(`FINNHUB_API_KEYS`, 키당 분당 60회)을 쓰고, 공유 캐시(stale-while-revalidate)로 호출을 줄인다. 차트·히트맵·기술지표·재무 위젯은 TradingView 임베드 위젯에 맡긴다. 선택 기능으로 Adanos API 의 Reddit·X·뉴스·Polymarket 감성 카드가 있다.
- 시장 범위: `lib/markets.ts` 주석대로 Finnhub 무료 키는 미국 주식·암호화폐만 되고 다른 거래소는 403 을 돌려준다. TradingView 임베드는 미국·암호화폐·외환만 실시간이고, TSX·ASX 는 지연, BSE·Xetra 는 일봉 종가 기준이다. **한국(KRX)은 `CHART_BLOCKED_EXCHANGES` 에 들어 있어** 캔들 차트가 막히고 재무·기술지표·프로필 위젯만 뜬다. 자체 시세·알림은 안 된다(MARKET_SUPPORT.md).
- LLM: Gemini(`gemini-2.5-flash-lite` 기본)이고, 실패하면 MiniMax(`MiniMax-M3`)나 Siray.ai 로 넘어간다(`lib/ai-provider.ts`). 쓰임은 가입 환영 메일 도입부(국가·투자 목표·위험 성향·선호 업종으로 개인화), 주간 뉴스 요약(최신 10건), TradingView 심볼 매핑 프롬프트 정도다. 리서치·추천에는 LLM 을 쓰지 않는다.
- 백그라운드 작업(Inngest): 가입 환영 메일, 매주 월 09:00 뉴스 요약(Kit 브로드캐스트), 5분마다 가격 알림 확인(realtime 모드 전용), 매일 10:00 휴면 사용자 재참여 메일.
- 1회 실행 비용: 자체 호스팅은 Finnhub 무료 키·MongoDB Atlas 무료 등급·Gemini Flash Lite 로 사실상 0 에 가깝다. 메일 1통당 LLM 호출 1회라 비용은 무시할 만하다. 공개 사이트는 기본 `cached` 모드(시세 1시간마다 갱신, 모든 사용자 공유)라 비용이 사용자 수가 아니라 종목 수에 비례한다.

## 성과 주장의 신뢰도

1. 주장 목록 — README·API_DOCS.md·MARKET_SUPPORT.md·마케팅 페이지·코드를 grep(`outperform|sharpe|backtest|accura|win rate|% return|alpha`)해도 수익률·적중률·초과수익 주장은 없다. 추천·신호·예측 기능 자체가 없다. 숫자 주장은 사용자 수뿐이다: "13,000+ people use OpenStock for free."(README 상단), "used by **13,000+ registered people**"(Sponsor 절). 투자 성과 주장이 아니고, 검증할 방법도 없다.
2. 면책 문구 — README: "Note: OpenStock is community-built and not a brokerage. Market data may be delayed based on provider rules and your configuration. Nothing here is financial advice."
3. 검증 수단 — 성과 주장이 없어 백테스트 기간·수수료·편향 대책·포워드 기록은 해당 없음. Adanos 감성 카드는 외부 API 값을 그대로 보여 줄 뿐 적중률 주장이 없다.
4. 판정 — 성과를 주장하지 않는 조회·대시보드 도구(앵커 5).

심층 T 5 (판정 T 5) — 시세·위젯을 보여 주는 대시보드일 뿐 수익·적중 주장이 없다.

## 수요 신호

이슈는 1년 동안 43개뿐이다(PR 62개). 반응이 가장 많은 이슈도 반응 4·댓글 3 수준이라 신호의 무게가 전반적으로 가볍다. Discussions 는 켜져 있으나 환영 글 1개뿐이다. 버그(가입·로그인 실패, 시간대, 비밀번호 재설정)와 정치 논쟁 이슈 #34(대만 국가 표기)는 제외했다. 벤더 영업 이슈 #58(FinancialData.Net)·#86(SiftingIO)도 신호에서 뺐다. 넣은 신호 23개(demand 14·pain 6·gap 3):

- **자체 호스팅 쉽게** — 가장 반응이 많은 축이다. #15 Docker 지원(반응 4, 이후 Compose 추가), #36 공개 Docker 이미지 요청(반응 3, 열림, "이미지를 왜 각자 빌드해야 하나"), #21 Vercel·Cloudflare 자동 배포 스크립트 요청, #19 MongoDB 설치가 번거롭다며 MySQL·PG 요청, #20 "어떻게 실행하는지 모르겠다". Node·MongoDB·Finnhub·Inngest·Gmail 을 모두 맞춰야 해서 비개발자에게 설치 장벽이 높다.
- **로그인 없이 쓰기** — #56 로그인 요구를 끌 수 있게 해 달라. 요청자는 이미 포크해 로그인과 팝업을 다 걷어냈다고 한다. 메인테이너는 포크해서 고치라고 답했다. 개인 자체 호스팅 사용자는 계정 체계가 필요 없다.
- **미국 밖 시장** — #26 중국 A주, #28 외환 검색, #24 대만(`2330.TW`) 상세 오류, #83 인도 NSE "This symbol is only available on TradingView". 원인은 모두 무료 등급 한계(Finnhub 무료는 미국만, TradingView 임베드는 신흥시장 차단)다. #83 은 "외부 독점 업체에 기대면 기본 제약이 생긴다"고 짚었다. #24 댓글은 OHLC API + Lightweight Charts 로 직접 그리는 방안을 냈다(gap). 브라질 B3 스크리너 제안(#95)은 포크 사용자가 올렸다(gap). 한국 시장 요청 이슈는 없지만, 코드상 KRX 는 차트 차단 목록에 있다.
- **TradingView 수준의 차트 도구** — #47 지표 고정 저장, #50 Pine 스타일 사용자 지표 스크립트, #54 차트에 직접 선 긋기, #53·#49 지표 즐겨찾기 소실(버그라 제외). 한 사용자(nexitpl)가 연달아 올린 것이라 폭넓은 수요로 보기는 어렵다. 임베드 위젯 구조로는 풀 수 없는 요구다.
- **알림·비용** — #59 SMA 같은 동적 조건 가격 알림 요청. 댓글에서 Finnhub 기술지표 등급이 월 $45 라 TradingView Essential(월 $13, 기술 알림 20개)보다 비싸다는 불만이 나왔다(pain). #60 홈 화면 모바일 위젯 요청.

## 파생·상용화

- 본 프로젝트의 상용화: README·마케팅 페이지에 "OpenStock Cloud"(월 $5, coming soon)가 있다. 실시간 시세(15초)와 이메일 가격 알림을 붙인 호스팅판이다. 2026-09-25 커밋 "feat(alerts): make price alerts an OpenStock Cloud feature" 로 공개 사이트의 알림을 유료판 몫으로 돌렸다. 자체 호스팅은 `NEXT_PUBLIC_OPENSTOCK_DATA_MODE=realtime` 으로 같은 기능을 쓸 수 있다. 그 밖에 GitHub Sponsors 등급($5~$500, Partner 는 앱 사이드바 스폰서 슬롯)이 있고, 이전 후원사는 Siray.ai(LLM 대체 공급자로 코드에 들어가 있음)다. README 에 같은 팀의 다른 제품(Onto, kitbash) 홍보가 올라와 있다.
- 웹 검색(2회): 이 레포를 감싼 제3자 유료 서비스는 찾지 못했다. 검색 결과는 원본을 그대로 복제한 포크와 트렌딩 집계 페이지(web1992/github-trending, trendshift, star-history)가 대부분이다.
- 포크(★순 상위 10): 포크는 2,371개로 많지만 상위 포크도 ★13 이하이고, 설명문까지 원본과 같은 복제본이다. `Gopinathsgn/OpenStockIndia`(★3)처럼 현지 시장용으로 바꾼 흔적이 조금 있고, 이슈 #95~#98 을 보면 한 사용자가 B3(브라질) 터미널로 개조한 포크를 운영 중이다.

## 내 투자에 쓰려면

- 실행: `.env` 에 MongoDB URI·Better Auth 시크릿·Finnhub 키를 넣고 `docker compose up`(앱+MongoDB) 또는 `npm install && npm run dev`. 메일·AI·Inngest 는 선택이다. 이번 조사에서는 설치·실행하지 않았다.
- 주의: 한국 종목은 캔들 차트가 막히고 자체 시세·알림도 안 돼서, 한국 투자에는 사실상 쓸모가 없다. 미국 주식 관심종목 보드로는 쓸 만하지만 차트·지표는 TradingView 위젯 그대로라 TradingView 무료판을 직접 쓰는 것과 큰 차이가 없다. `NEXT_PUBLIC_FINNHUB_API_KEY` 는 이름대로 브라우저에 노출된다. 공개 사이트에 가입하면 국가·투자 목표·위험 성향을 LLM 프롬프트에 넣고, 주간 뉴스 작업은 Kit 구독자 이메일 목록을 Inngest 로그에 그대로 찍는다(`lib/inngest/functions.ts` 의 `sendWeeklyNewsSummary`). 개인정보를 생각하면 자체 호스팅이 낫다.

## 인디 관점 메모

- 공백: (1) "튜토리얼 수준 대시보드"에도 ★19k 가 붙는 걸 보면, 무료·깔끔한 관심종목 대시보드라는 포지션에 관심이 크다. 다만 실사용 요구(이슈)는 얇다. (2) 무료 데이터 한계로 미국 밖 시장이 비어 있다. 한국은 KRX 차트 차단 + Finnhub 무료 403 이라 KIS·KRX·DART 데이터에 Lightweight Charts 로 직접 그리는 한국판 대시보드면 공백을 메울 수 있다. 현지 시장용 포크(인도·브라질)가 자생적으로 나오는 것도 같은 수요다. (3) 원클릭 자체 호스팅(공개 Docker 이미지·로그인 없는 단일 사용자 모드·MongoDB 없이 SQLite)이 요청 1순위인데 아직 비어 있다. (4) 동적 조건 알림(SMA 교차 등)을 싸게 주는 것 — TradingView 유료 알림과 Finnhub 유료 등급 사이의 가격 공백.
- 차용: 무료 키 풀을 요청마다 돌리는 방식 + 공유 캐시로 "비용을 사용자 수가 아닌 종목 수에 묶는" `cached`/`realtime` 두 모드 설계, 시세 폴링 API 를 로그인 사용자·25종목으로 제한해 공유 할당량을 지키는 방식, 시장별 커버리지를 실제로 테스트해 표로 공개한 MARKET_SUPPORT.md, LLM 공급자 폴백 추상화. 단 AGPL 이라 코드를 가져다 서비스하면 소스 공개 의무가 있다.
