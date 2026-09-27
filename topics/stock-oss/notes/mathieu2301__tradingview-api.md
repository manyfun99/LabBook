---
entity: github:mathieu2301/tradingview-api
gh_id: 344949361
judged: 2026-09-27  rubric: v1
t_deep: 5
tags: [data-mcp, market-data, unofficial-api, websocket, nodejs, tradingview, tos-risk]
---
## 무엇·어떻게

TradingView 웹사이트가 쓰는 내부 웹소켓 프로토콜을 역공학해 Node.js 에서 시세·차트 봉·지표값·전략 리포트를 받아 오는 비공식 라이브러리다. npm `@mathieuc/tradingview` 3.5.2, 라이선스 ISC, clone HEAD `5baea86c8c7e576f13464919c86c3b4c4b0ecf4c`(마지막 커밋 2026-06-23 "Stabilize TradingView indicator CI tests (#317)"). ★5,380·포크 961·열린 이슈 103.

- 구조(소스 약 3,000줄): `src/client.js` 가 `wss://{data|prodata|widgetdata}.tradingview.com/socket.io/websocket` 에 브라우저 User-Agent·`origin: https://www.tradingview.com` 을 달고 붙는다. 그 위에 `quote/`(실시간 호가 세션), `chart/`(봉·스터디·리플레이 세션, `graphicParser` 로 지표의 라벨·선·박스 파싱), `classes/`(`PineIndicator`·`BuiltInIndicator`·`PinePermManager` — 초대 전용 스크립트 접근 권한 관리)가 있다. `miscRequests.js` 는 HTTP 로 `scanner`(기술적 분석 요약 `getTA`)·`symbol-search`·`pine-facade`(지표 검색·소스 받기)·`accounts/signin`(`loginUser`)·`charts-storage`(내 차트 드로잉)를 호출한다.
- 인증: 로그인 없이 `unauthorized_user_token` 으로 접속하거나, 브라우저 쿠키 `sessionid`+`sessionid_sign` 을 `token`/`signature` 로 넘긴다. `loginUser` 는 아이디·비밀번호를 TradingView 로그인 폼에 그대로 POST 한다(값을 URL 인코딩하지 않음).
- 기능: 실시간 시세, 기간 지정 봉, 커스텀 타임프레임·차트 타입(Renko 등), Pine 지표·전략 값과 `strategyReport`(순이익·드로다운·거래 목록), 리플레이 모드와 무료 요금제용 "Fake Replay", 드로잉 가져오기. README 가 "Premium features", "Works with invite-only indicators", "Unlimited simultaneous indicators" 를 기능으로 내건다.
- 데이터 소스: TradingView 하나. 공식 API 가 아니므로 TradingView 가 프로토콜·인증을 바꾸면 바로 깨진다(이슈 #182·#187·#269·#294 가 모두 그 사례).
- 코드 점검: 외부 호출은 모두 `*.tradingview.com` 이고 `eval`·`child_process` 는 없다. CI(`tests.yml`)는 메인테이너의 TradingView 세션을 GitHub Secrets 로 넣어 매일 실제 서버에 붙여 본다.
- LLM: 쓰지 않는다. 1회 실행 비용: 라이브러리는 무료. 다만 지표 수·봉 수·실시간 여부는 TradingView 계정 등급(무료/Essential/Plus/Premium)과 거래소 데이터 구독에 묶인다.

## 성과 주장의 신뢰도

1. 주장 목록 — README·`docs/DOCS.md`·`examples/` 에서 수익률·적중률·샤프 같은 성과 주장은 없다. README 의 "Automatically backtest many strategies and try many settings in a very little time" 는 기능 설명이고 결과 수치가 없다.
   - 참고: 이슈 #30 에서 메인테이너가 의뢰인용 Node-RED 백테스트를 만들며 "I did not expect such good results !" 라고 적고 BTC 는 잘 되고 S&P500·NASDAQ100 은 잘 안 된다고 한 스크린샷을 올렸다. 유료 외주 작업의 중간 결과이고 레포의 주장이 아니다.
2. 면책 문구 — 없다. 투자 조언 면책도, TradingView 약관 위반·계정 차단 위험 경고도 README 에 없다.
3. 검증 수단 — 성과 주장이 없어 해당 없음. 참고로 전략 리포트는 TradingView 서버가 계산한 값을 그대로 받는 것이라 백테스트 품질(수수료·슬리피지·리페인트)은 Pine 스크립트와 TradingView 엔진에 달려 있다.
4. 판정 — 성과를 주장하지 않는 데이터 도구(앵커 5).

심층 T 5 (판정 T 5) — 레포 자체의 성과 주장이 없는 비공식 시세·지표 데이터 라이브러리다.

## 수요 신호

이슈 반응이 전반적으로 적다(반응순 1위가 6). 그래서 댓글 수와 내용으로 골랐다. 대부분의 이슈는 사용법 질문이거나 TradingView 쪽 변경으로 생긴 오류다. 단순 버그는 빼고, 오류라도 "비공식 API 라서 생기는 차단·인증 고통"을 보여 주는 것만 넣었다. 넣은 신호 25개(demand 14·pain 10·gap 1):

- **대신 만들어 달라(done-for-you)** — #30 "Can I Hire You To Set This Up For Me?"(댓글 59, 이 레포 최다)에서 비개발자가 초대 전용 지표 4개로 백테스트를 돌리고 싶다며 메인테이너에게 외주를 줬다. 메인테이너는 비공개 레포에 Node-RED 플로를 만들어 넘기고 PayPal·Wise 로 돈을 받았다. 같은 스레드에 "나도 해 달라, 비용 내겠다"는 사람과 "백테스트 예제를 공개해 달라"는 요청이 붙었고, 메인테이너는 의뢰인용 서비스라 공개하지 않는다고 답했다. #202 에서는 다른 사용자가 메인테이너가 자기 24/7 봇 시스템을 만들어 줬다며 TV 웹소켓을 잘 모르면 맡기라고 권한다. README 맨 위에도 "personalized assistance" 신청 폼이 걸려 있다.
- **파라미터 대량 백테스트** — #68(Pine 전략 파라미터 백만 조합), #207 백테스트 예제 요청(반응 6, 반응순 1위), #179(6,000 조합을 돌리다 계정 차단). TradingView UI 로는 못 하는 파라미터 스윕이 이 라이브러리를 쓰는 핵심 동기다.
- **비개발자 진입 장벽** — #218(댓글 11) "I'm an absolute zero in programming", #105·#69·D#185 실행 방법 질문, D#190 문서가 없음. 문서는 JSDoc 과 예제 폴더뿐이다.
- **인증·차단(비공식 API 고통)** — #202(댓글 13) 캡차가 새 세션마다 뜨고 세션 수명이 몇 달에서 며칠로 줄어 24/7 봇이 밤중에 멈춘다. 브라우저 쿠키를 손으로 다시 붙여야 한다. 사용자들은 TradingView 가 인증을 표준화해 주거나 IP 화이트리스트를 주기를 바란다(2FA 지원 요청도 있음). #179 은 경고 없이 계정이 차단됐다고 한다. #278 은 로컬에서는 되는데 Heroku 에 올리면 세션이 바뀌거나 IP 가 막힌다고 한다. #269·#294·D#247 에서는 2024~25년부터 게스트 접속으로 지표를 못 올리게 되어 계정 로그인이 필수가 됐고, "계정을 쓰기 싫다"는 반응이 나온다. #182·#187 은 TradingView 가 프로토콜을 바꿔 하루아침에 모두 깨진 사례다(각 댓글 10·41).
- **데이터 한도** — #173 세션 레이트리밋, #50 1분봉 5,000개 한도, D#233 5,000~20,000 봉 한도 때문에 로컬 CSV 로 백테스트하고 싶다는 요청.
- **알림·주문** — #136·#84 알림을 코드로 만들고 싶다는 요청(알림은 웹소켓이 아니라 별도 API 라 미구현). D#62 실제 주문까지 하는 봇 요청(주문은 브로커 백엔드로 간다).
- **브라우저 사용(gap)** — #161 브라우저에서 쓰고 싶다는 요청에 메인테이너가 TradingView 가 origin 을 막아 불가능하다고 답했다. 클라이언트 앱에 직접 넣을 수 없고 서버가 필요하다.
- 한국 시장·한국어 요청: 찾지 못했다(이슈 검색·상위 60개·Discussions 50개 기준).

## 파생·상용화

- 메인테이너 본인: GitHub Sponsors, README 의 맞춤 개발 신청 폼(Google Forms), Telegram 커뮤니티. 이슈 #30·#202 로 보아 라이브러리 위에 봇·백테스트 시스템을 외주로 만들어 준다. 제품이 아니라 용역으로 돈을 번다.
- 비공식 TradingView 데이터 호스팅 API: tradingviewapi.com(RapidAPI `tradingview-data1` 로도 판매)이 "unofficial third-party" 를 내걸고 REST·WebSocket·SSE·MCP 로 시세·OHLCV·스크리너를 월 $0~80 에 판다(웹 검색). 이 라이브러리를 쓰는지는 확인하지 못했지만, 같은 방식(비공식 접속)을 호스팅해 파는 수요가 실제로 있다는 근거다.
- 약관: TradingView 이용약관은 스크립트·API·스크래핑 등 모든 자동 수집을 목적과 관계없이 금지하고, 위반 시 계정 임시·영구 정지를 둔다(웹 검색, tradingview.com/policies, "How bans work"). 이 위에 유료 서비스를 올리면 계정 차단과 법적 대응 위험을 서비스가 떠안는다.
- 포크(★순 상위 10): 모두 ★5 이하의 개인 포크다(MooneDrJune·bludnic 등). 의미 있는 파생 포크는 없다. npm 에서 이 패키지에 의존하는 패키지는 4개 정도(웹 검색).

## 내 투자에 쓰려면

- 실행: Node.js 에서 `npm i @mathieuc/tradingview` 뒤 `new TradingView.Client({ token, signature })` 로 접속하고 `client.Session.Chart()` 로 `setMarket('거래소:심볼', { timeframe, range })` 를 부른다. 지표는 `TradingView.getIndicator('STD;...' 또는 'PUB;...')` → `new chart.Study(indic)`. 이번 조사에서는 설치·실행하지 않았다.
- 한국 종목: TradingView 가 KRX 종목을 다루므로 `KRX:<종목코드>` 형식으로 조회될 것으로 보이나 확인하지 못했다. 실시간 여부는 TradingView 쪽 거래소 데이터 구독에 달려 있다.
- 주의: (1) 약관 위반이다. 본 계정이 아닌 별도 계정을 쓰고, 조합 수천 개를 한 번에 돌리지 않는다(#179 은 약 4,000 조합에서 차단). (2) 세션 쿠키는 계정 비밀번호와 같은 무게다. 코드·로그·이슈에 붙여 넣지 않는다. 이 레포 이슈에는 실제 쿠키로 보이는 값이 붙은 댓글이 있다. (3) 서버·클라우드 IP 에서는 캡차·차단이 더 잦다. (4) TradingView 가 프로토콜을 바꾸면 수정본이 나올 때까지 멈추므로 매매 주문 경로에 두지 않는다. 데이터 확인·파라미터 탐색 보조로만 쓴다.

## 인디 관점 메모

- 공백: (1) 비개발자 트레이더가 "내 Pine 전략·초대 전용 지표로 파라미터 스윕 백테스트"를 원하고 돈을 낸다(#30 외주, #68·#179). 코드 없이 쓰는 파라미터 최적화 도구 수요다. 다만 TradingView 에 기대면 약관·차단 위험을 떠안으므로, 전략을 로컬 백테스트 엔진과 자체 데이터로 옮겨 돌리는 쪽이 안전하다(D#233 의 로컬 CSV 요청과 같은 방향). (2) 세션 관리·캡차·재접속을 대신해 주는 관리형 호스팅은 이미 tradingviewapi.com 이 하고 있고, 약관상 회색지대라 인디가 들어갈 자리로는 위험하다. (3) 알림을 코드로 관리하거나 주문까지 잇는 기능은 이 라이브러리 범위 밖이다. 사용자는 웹훅→브로커 연결을 따로 붙인다.
- 차용: 웹소켓 패킷 포맷(`protocol.js` 의 `~m~길이~m~` 프레이밍)과 세션별 콜백 구조, 지표 그래픽(라벨·선·박스)을 표 데이터로 바꾸는 `graphicParser` 의 아이디어, 무료 요금제에서 `to` 를 음수 범위와 함께 써 과거 구간을 받는 Fake Replay 방식. 모두 TradingView 에 종속되므로 참고용으로만 본다.
