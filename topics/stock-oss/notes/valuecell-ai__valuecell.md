---
entity: github:valuecell-ai/valuecell
gh_id: 1048320382
judged: 2026-09-27  rubric: v1
t_deep: 3
tags: [llm-agent, multi-agent, crypto-trading, a-share, desktop-app, hosted-saas, apache-2.0]
---
## 무엇·어떻게

LLM 에이전트 여러 개(리서치·뉴스·전략)를 A2A 프로토콜로 묶은 금융 앱이다. Python 백엔드(FastAPI, Agno 2.x, `a2a-sdk`)와 React Router + Tauri 프런트(데스크톱 앱 겸 `localhost:1420` 웹 UI)로 되어 있다. clone HEAD `9793e9c0563fbf56fc096757d8bb80e209ac7aab`(2026-02-11), `pyproject` 버전 0.1.20, 라이선스 Apache-2.0.

- 구조: `python/valuecell/core`(SuperAgent·플래너·태스크·대화·이벤트 라우터), `agents/`(`research_agent`·`news_agent`·`prompt_strategy_agent`·`grid_agent`), `agents/common/trading/`(데이터→피처→LLM 결정→실행→포트폴리오→이력·다이제스트로 도는 전략 프레임워크), `adapters/assets`(시세 어댑터), `server/`(REST API·SQLite). 에이전트마다 에이전트 카드(`configs/agent_cards/*.json`)를 두고 따로 uvicorn 프로세스(`localhost:1000x`)로 뜬다.
- 데이터 소스: 시세는 yfinance(미국·홍콩)·akshare·baostock(A주), 거래소 시세·주문은 ccxt. 공시는 SEC(edgartools)와 A주 cninfo(巨潮) 크롤링. 크립토 프로젝트·VC 정보는 rootdata.com 스크래핑. 웹 검색은 OpenRouter 의 `perplexity/sonar` 또는 Gemini 로 한다(SiliconFlow 키만으로는 안 됨, #246 메인테이너 답변). `Exchange` 열거형은 NASDAQ·NYSE·AMEX·SSE·SZSE·BSE·HKEX·CRYPTO 뿐이고 한국 거래소는 없다.
- 실거래: 크립토 무기한 선물 계약만 된다(현물도 1배 계약으로 처리). Binance·Hyperliquid·OKX 는 "Tested", Coinbase·Gate.io·MEXC·Blockchain 은 "Partially Tested". 기본값은 가상 거래(`PaperExecutionGateway`, 수수료 10bps, 지시별 `max_slippage_bps`).
- 전략: `prompt_strategy_agent` 는 매 주기 캔들·스냅샷 피처와 포트폴리오를 프롬프트에 넣어 LLM 이 `TradeInstruction` 을 내게 한다. 템플릿은 `default`·`aggressive`·`insane`(손절 없이 물타기·최대 레버리지. 파일 안에 "simulation … only" 경고가 있음). `grid_agent` 는 규칙 기반 그리드이고, LLM 은 파라미터 조언만 한다.
- LLM: OpenRouter·SiliconFlow·Azure·OpenAI·Google·DeepSeek·DashScope·Ollama·OpenAI 호환. 기본 모델은 리서치가 `google/gemini-2.5-flash`(OpenRouter), 임베딩이 `Qwen/Qwen3-Embedding-4B`(SiliconFlow), 전략이 `deepseek-ai/DeepSeek-V3.1-Terminus`(SiliconFlow). 지식 저장소는 LanceDB 다.
- 1회 실행 비용: 직접 재지 않았다. 전략 에이전트의 `decide_interval` 기본값이 60초라서 전략 하나가 하루 약 1,440번 LLM 을 부른다. 비용은 모델 단가에 비례한다. #184 에는 Gemini(OpenRouter)가 도구 호출 루프에 빠져 한 시간 동안 출력 없이 입력 토큰만 불어나며 과금됐다는 보고가 있다.
- 외부 통신: 데스크톱 앱은 첫 실행 때 `client_id`(UUID)와 OS 를 `backend.valuecell.ai/api/v1/analytics/event` 로 보내고, 프런트도 로그인·로그아웃·에이전트 사용(`agent_name`) 이벤트를 같은 곳에 보낸다. 로그인·전략 리더보드·기본 티커도 `backend.valuecell.ai` 에서 받는다. README 의 "keeps all your sensitive information stored locally" 는 키·거래 데이터 이야기이고, 사용 텔레메트리는 밖으로 나간다.
- 활동: 기본 브랜치의 마지막 커밋은 2026-02-11, 마지막 릴리스는 v0.1.20(2026-01-10)이다. 2026-04 이후 이슈(#621 등)에는 답이 없고, 외부 PR(#630 한국어 번역, #631 MiniMax, #632 Tavily)은 병합되지 않았다. ★11,025 / 포크 1,804.

## 성과 주장의 신뢰도

1. 주장 목록
   - README "Description": "It provides a team of TOP investment Agents to help you with stock selection, research, tracking, and even trading." 수치 없는 마케팅 문구다.
   - README 스크린샷 `assets/product/AutoTradingAgent.png`: 가상 거래(Virtual)에서 DeepSeek V3.1 Terminus 전략이 "+18.73 (+1.87%)"로, 포트폴리오 곡선이 1,000 → 1,018.73 으로 올라간 화면이다. 시간축은 Nov 12 16:05~17:08, 약 1시간이다. 같은 화면의 Qwen Max·Claude Haiku 4.5 는 0%다.
   - 앱 내 "Profit Leaderboard"(`frontend/src/app/rank/board.tsx`, i18n `rank.title`): `backend.valuecell.ai/strategy/list` 에서 사용자 전략의 `return_rate_pct` 를 7D·1M 순위로 받아 보여 주고, "copy strategy" 로 프롬프트를 복제할 수 있다. 수익률은 클라이언트가 계산해 `strategy/report` 로 올리는 값(`StrategyReport.return_rate_pct`, `trading_mode` 포함)이다. 현재 HEAD 에서 업로드 호출(`usePublishStrategy`)은 주석 처리돼 있다.
   - 거래소 표의 "✅ Tested: Fully tested and verified in production environment" 는 연동 검증이지 성과 주장이 아니다.
2. 면책 문구 — README "This project is for technical exchange only. Investing involves risk. ⚠️", `insane.txt` 의 "Use only for simulation, stress testing, or demo purposes. Do NOT deploy live without adding firm risk limits…". 위 1의 주장(스크린샷·리더보드)이 있으므로 면책 문구가 있다고 성과를 주장하지 않는 도구로 보지 않는다.
3. 검증 수단
   - 백테스트: 엔진이 없다. `common/trading/README.md` 에 `BacktestDataSource` 를 직접 짜라는 예시 스텁만 있다. 기간·종목 수는 해당 없음.
   - 수수료·슬리피지: 가상 거래에 수수료 10bps 고정과 지시별 슬리피지 bps 가 있다. 펀딩비·청산은 모델링하지 않는다(코드에서 찾지 못함).
   - look-ahead·생존 편향: 백테스트가 없고 실시간 실행이라 look-ahead 위험은 작다. 리더보드는 상위 수익만 7일·1개월 창으로 보여 주므로 생존·선택 편향이 크다.
   - LLM 컷오프 이후 구간: 실시간 실행이므로 구조상 컷오프 이후다.
   - 포워드·페이퍼 기록: 페이퍼·실거래 포워드 기록은 있으나 사용자 자기 보고이고 공개 검증 수단(거래소 체결 대조·가상/실거래 구분 공개)은 확인되지 않는다. 레포 팀이 낸 체계적 평가는 없다.
4. 판정 — 앵커 5(성과를 주장하지 않는 도구)로 보기에는 데모 수익 스크린샷과 수익률 리더보드가 제품의 일부다. 앵커 1(방법 불명의 수익 주장)만큼 강한 주장도 아니다. 레포 스스로 제시하는 숫자는 1시간 가상 거래 데모뿐이고, 리더보드 숫자는 사용자 자기 보고라 검증할 수 없다. 그래서 중간인 3으로 둔다.

심층 T 3 (판정 T 4) — 수익률 주장은 1시간 가상 거래 데모 스크린샷과 검증 불가한 사용자 수익률 리더보드뿐이고, 백테스트·체계적 평가는 없다.

## 수요 신호

이슈 반응이 매우 적다(최대 반응 3). 댓글순 상위도 대부분 설치·데이터 조회·연결 오류라 버그는 뺐다. Discussions 는 꺼져 있다. 넣은 신호 19개(demand 11·pain 7·gap 1):

- **자체 호스팅·원격 접속(가장 반복됨)** — #279(댓글 14) 다른 IP 에서 접속하는 방법, #304(댓글 8) 서버 배포, #230, #180, #522 Docker·배포 문서 요청, #469 Docker 배포 요청. #469 댓글은 NAS 에 Docker 로 띄워 API 키만 넣고 인터넷에서 웹으로 쓰는 사용 방식을 원한다. 원인은 에이전트 카드 URL 이 `localhost` 고정이고 프런트 dev 서버가 `localhost` 에 바인딩되는 구조다. 메인테이너는 "not currently a high-priority item" 이라고 답했다. #621(답 없음)은 "유료 홈페이지를 홍보하려고 일부러 자체 구축을 어렵게 한 것 아니냐"고 불만을 제기했다. 호스팅판(valuecell.ai)과 자체 호스팅 난이도가 부딪히는 지점이다.
- **설치 어려움** — #563(댓글 9)·#586 Windows 설치 파일이 99%에서 멈춘다. 원인은 `C:\Program Files` 쓰기 권한과 중국 내 프록시에서 uv 가 python-build-standalone 을 받지 못하는 문제다. #591 M5 맥에서 앱이 안 열린다. #222 어떤 API 키를 설정해야 하는지 모르겠다며 더 자세한 튜토리얼을 요청했다.
- **API 비용** — #184 에이전트가 출력 없이 돌며 OpenRouter 크레딧만 계속 빠진다.
- **데이터 신뢰성** — #345 yfinance 레이트리밋 때문에 대체 공급원을 요청했다(메인테이너는 우선순위가 낮다고 답함). #196·#216(댓글 12·9)은 지수 시세 조회 실패로, 버그라 신호에서 뺐지만 무료 데이터 의존이 반복적인 고통이다.
- **트레이딩 기능** — #167 크립토 시장 기능, #188 레버리지(Alpha Arena 식), #372 거래소별 전체 심볼 동기화(밈코인 등 저유동 토큰), #462 댓글 OKX US 리전(us.okx.com) 지원, #546 X/CryptoPanic/LunarCrush 기반 SentimentAgent 제안(Alpha Arena S1.5 의 Grok 4.20 우승 언급). 사용자층이 nof1.ai Alpha Arena 식 "LLM 크립토 선물 봇"을 원하는 쪽으로 쏠려 있다.
- **한국어·한국 시장** — README 로드맵의 다국어 목록에 Korean 이 계획으로만 있다(gap). 외부 기여자의 한국어 번역 PR #630 은 병합되지 않고 작성자가 닫았다. 한국 거래소 시세는 코드에 없다. #232 웹 UI 국제화 요청은 중국어 지원(#573)으로 닫혔다.

## 파생·상용화

- 본사 상용: valuecell.ai — README 가 "A-share deep research, market analysis and requires no deployment" 라고 소개하는 호스팅판이다. 로그인·전략 리더보드·텔레메트리 백엔드(`backend.valuecell.ai`)도 같은 회사가 운영한다. 가격 정보는 웹 검색과 홈페이지 조회(태그라인 "From Insight to Execution: Stay in Command" 만 보임)로 찾지 못했다. 오픈소스는 크립토 전략·로컬 리서치, 호스팅은 A주 리서치로 시장을 나눈 오픈 코어 구조로 보인다.
- 포크(★순 상위 10): 모두 ★1 의 개인 포크다. 의미 있는 파생은 없다. GitCode(`zhma12/ValueCell-ai`)·SourceForge 미러가 있다.
- 제3자 유료 서비스: 찾지 못했다(웹 검색 3회). 중국 기술 블로그(CSDN·知乎·腾讯云)에 "AI 炒股平台" 소개 글이 많아, 유입은 중국어권 개인 투자자 중심이다.

## 내 투자에 쓰려면

- 실행: 소스로는 `bash start.sh`(bun·uv 가 없으면 설치하고, `uv sync`, `playwright install chromium`, DB 초기화 후 프런트·백엔드를 띄움)를 실행하고 `http://localhost:1420` 으로 접속한다. `.env` 는 OS 앱 데이터 디렉터리(`~/Library/Application Support/ValueCell/.env`)에 둔다. 최소 구성은 OpenRouter 키 하나와 임베딩용 SiliconFlow(또는 Google) 키다. 이번 조사에서는 설치·실행하지 않았고 릴리스 바이너리도 받지 않았다.
- 주의
  - 한국 주식: 시세·공시가 모두 없다. yfinance 어댑터가 거래소 열거형에 묶여 있어 `.KS` 티커도 바로 쓰기 어렵다. 한국 주식 리서치 용도로는 맞지 않는다.
  - 실거래: 크립토 레버리지 선물 전용이다. 기본 최대 레버리지 10, `insane` 템플릿은 손절 없이 물타기를 한다. 실거래 전에 가상 모드로 충분히 돌려 보고, API 키는 출금 권한 없이 IP 화이트리스트를 걸어 쓴다.
  - LLM: 구조화 출력과 도구 호출을 함께 지원하지 않는 모델에서 파싱이 실패하거나(#184) 무한 루프로 과금될 수 있다. 호출 주기와 모델 단가를 먼저 계산한다.
  - 네트워크·유지보수: 원격 서버에 띄우려면 `API_HOST`·`frontend/.env`·에이전트 카드 URL 을 손봐야 하고, 인증이 없으니 외부 노출은 피한다. 사용 이벤트가 `backend.valuecell.ai` 로 나간다. 2026-02 이후 유지보수가 멈춘 것으로 보인다.

## 인디 관점 메모

- 공백
  1. 자체 호스팅 수요가 가장 반복되는데 공식 대응이 없다. Docker·NAS 원클릭 배포와 인증을 갖춘 "개인용 LLM 트레이딩 봇 호스팅"이 비어 있다. Apache-2.0 이라 상용 래핑에 라이선스 제약이 적다.
  2. LLM 트레이딩 성과를 검증 가능하게 보여 주는 층이 없다. 리더보드가 자기 보고 수익률이라 거래소 체결 대조, 가상/실거래 구분, 펀딩비·청산을 반영한 공개 포워드 기록을 제공하면 차별점이 된다(Alpha Arena 류 수요가 이슈에 보임).
  3. 한국 시장·한국어가 로드맵에만 있고 번역 PR 도 병합되지 않았다. 한국 주식(KIS·DART) 리서치 에이전트는 이 레포 생태계 밖의 몫이다.
- 차용
  - 데이터→피처→LLM 결정→가드레일→실행→다이제스트로 나눈 전략 파이프라인(`BaseStrategyAgent` 확장점)과 결정 주기별 `compose_id` 감사 추적.
  - 가상/실거래를 같은 인터페이스(`BaseExecutionGateway`)로 바꿔 끼우는 구조.
  - 규칙 기반 그리드에 LLM 은 파라미터 조언만 맡기는 비용 절감형 설계.
  - 전략 프롬프트 템플릿을 공유·복제하는 소셜 기능.
