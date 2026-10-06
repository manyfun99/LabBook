---
entity: github:virattt/ai-hedge-fund
gh_id: 896144595
judged: 2026-09-27  rubric: v1
t_deep: 4
tags: [llm-agent, persona-agent, backtest, point-in-time, tui, vendor-funnel, mit]
---
> 갱신 (2026-10-06): 2026-10-01 커밋 6ddac1e 로 페이퍼 트레이딩 모드가 생겼다. 세션마다 `~/.hedge-fund/paper/<name>/` 의 해시체인 원장에 쌓인다. 아래 "실매매·페이퍼 기능이 없다" 서술은 2026-09-28 기준이다.

## 무엇·어떻게

투자 대가 페르소나 LLM 에이전트와 퀀트 모델을 "펀드" 조직도(전략 pod → 포트폴리오 구성 → 리스크 → 체결 → 원장)로 엮은 교육용 AI 헤지펀드다. clone HEAD `5d2c7ca2d02c6501692a58bb363dfab1916890ba`, 패키지 `aihf` 2.4.1, MIT, ★63.7k·포크 1.1만. 2024-11 에 만들어졌고 마지막 push 는 2026-09-26 이다.

- 판 갈이: HEAD 는 v2 로 새로 짠 코드(`hedge_fund/`)만 남아 있다. LangGraph 기반 v1(`src/`·`app/` 웹앱·18개 에이전트·Ollama 지원)은 레포에서 빠졌다. 그런데 `hedge_fund/README.md` 에는 아직 "developed alongside the shipped v1 app (`src/`, `app/`)"라고 적혀 있어 문서가 낡았다. 웹 블로그와 옛 이슈(#606·#624 등)는 v1 기준이다.
- 구조: `pipeline/run_cycle.py` 한 경로를 백테스트·당일 실행 두 모드가 같이 쓴다(페이퍼·실매매는 계획). `signals/` 는 `AlphaModel.predict(ticker, date, data_client) -> Signal` 인터페이스다. 페르소나 5개(buffett·munger·graham·lynch·druckenmiller)는 시스템 프롬프트만 다르고 bullish/neutral/bearish 와 confidence 를 JSON 으로 낸다. 퀀트 모델은 PEAD 하나뿐이다. `strategies/*.yaml` 에 pod 4개(fundamental-ls·deep-value·inflections·earnings-drift)가 있고, mandate YAML 은 전략·가중치·리스크 한도·자본·리밸런스 주기·벤치마크만 담고 티커는 담지 않는다(티커는 실행할 때 `--tickers` 로 준다). UI 는 Textual TUI 다.
- "LLM 은 체결을 건드리지 않는다" 원칙: LLM 은 견해(conviction ∈ [-1,+1])와 논거만 내고, 비중 계산·주문·리스크 한도(종목당 25%, 총노출 1.0)는 결정론적 코드가 맡는다.
- 데이터 소스: Financial Datasets API 하나뿐이다(가격·재무지표·기업정보·실적). 저자가 이 API 의 제작자이고, yfinance 같은 대체 공급원은 일부러 넣지 않는다고 여러 번 밝혔다(#22·#61·#365·#593). 응답은 `~/.hedge-fund/cache/` 에 디스크 캐시한다.
- LLM: Anthropic·OpenAI·DeepSeek·Google·xAI·Kimi, 그리고 TypeSafe 의 "Jev"(전용 어댑터 `JevLLM`). 기본값은 `claude-opus-5-5` 다. v2 에는 아직 Ollama(무료 로컬 경로)가 없다(ROADMAP 에서 "next").
- 1회 실행 비용(코드 기준 추정, 실측 아님): LLM 호출은 페르소나 × 티커마다 1회다. 프롬프트 캐시가 스냅샷 해시를 키로 쓰기 때문에, 백테스트에서도 새 공시가 나와 스냅샷이 바뀔 때만 다시 부른다. 기본 백테스트 창(78주)이면 티커 하나 × 페르소나 5개로 대략 30회 정도라서 LLM 비용은 작다. 주된 비용은 데이터다. 이슈에 나온 Financial Datasets 가격은 월 $100(#22, 2024-12), 월 $199(#365, 2025-06)이고, 무료 티커(AAPL·NVDA·MSFT·GOOGL·TSLA)가 있었지만 2026-08 에는 무료 계정에서 402 "Insufficient credits" 가 났다(#706).

## 성과 주장의 신뢰도

1. 주장 목록
   - README·VISION·ROADMAP·`hedge_fund/README.md` 에는 수익률·샤프·적중률 수치가 없다. README 이미지(user-attachments `e3985623…`)는 시스템 구성도일 뿐 수익 곡선이 아니다(내려받아 확인). 저자 트위터 배지 말고는 블로그 링크가 없고, 웹 검색으로도 저자의 수익률 주장을 찾지 못했다.
   - 정성적 우위 주장: `strategies/fundamental-ls.yaml` 의 "Edge claimed: collective judgment ranks names better than the market prices them.", `deep-value.yaml` 의 "Edge claimed: mispriced quality with a margin of safety." 근거 없는 가설이지만 "시장보다 낫다"는 주장이다.
   - 목표 문장: VISION "an AI hedge fund that genuinely tries to **outperform the market**" — 성과 주장이 아니라 목표다.
   - 제3자: #115 "as we can see the performance and the reliability of all agents"는 사용자의 인상이다. #203 의 v1 백테스터 출력 "Return: +210.11% / Sharpe Ratio: 11.04"는 계산 버그였고 수정됐다. #287 "Anyone making money" 에 저자는 "Goal is not to make money with this project, but to learn!" 이라고 답했다.
2. 면책 문구: README "This project is for **educational** purposes only and is not intended for real trading or investment.", Disclaimer 절 "Past performance does not indicate future results". VISION·ROADMAP 첫머리에도 같은 문구가 있다. 1에 정성 주장이 있으므로 면책 문구만으로는 5점으로 보지 않는다.
3. 검증 수단
   - 백테스트 도구: 있다(`backtest_fund`). 기간은 기본 78주(약 18개월)이고 `--start` 로 바꾼다. 종목은 사용자가 고른다. 정해진 유니버스가 없어 선택·생존 편향은 사용자 몫이다. 공개된 백테스트 결과는 없다.
   - look-ahead 대책: 있다. 재무는 `report_period` 가 아니라 `filing_date` 로 거른다. 시가총액은 최신값(`company_facts`)이 아니라 공시된 지표 행에서 가져온다. 판단은 t일 종가 기준으로 하고 체결은 다음 세션 종가(`next_close`)로 한다. 업종·산업만 최신값을 쓰는데, 코드 주석에 근사라고 밝혀 두었다.
   - LLM 기억 누출 대책: 있다. 백테스트에서는 blind 모드가 켜져 티커·산업·날짜를 빼고 기간을 t-0, t-1… 로 붙인다(`features/snapshot.py`, `fund/spec.py`, TUI 도 같다). 계기는 2026-09-25 이슈 #720 이다. 제3자가 12개 모델의 기억 회상을 측정했는데, Opus 5.5 는 AUC 0.766, GPT-6 Astra 는 0.904 였다. PR #721 은 이틀 전에 들어간 아주 새 기능이다. README 스스로 "reduces the recall without removing it"라고 인정한다.
   - LLM 컷오프 이후 구간: 강제하지 않는다. README 는 컷오프 이후 창이 "cleanest read"라고 권할 뿐이다. 기본 모델(Opus 5.5)과 기본 창(최근 78주)이 모델의 학습 구간과 얼마나 겹치는지 검사하는 코드는 없다.
   - 수수료·슬리피지: 없다. `SimBroker` 는 기준가에 전량 체결하고 "Slippage/costs are a declared future addition"이라고 적어 두었다.
   - 과적합 검증(CPCV·PBO): 계획(⬜)이다.
   - 포워드·페이퍼 기록: 없다. 페이퍼 브로커는 ⬜이고, 원장 읽기가 아직 없어 실행마다 NAV 가 mandate 자본으로 초기화된다.
4. 판정: 수치 주장은 없고, look-ahead 와 기억 누출 대책을 코드로 공개한 점은 앵커 3을 넘는다. 다만 전략 YAML 이 우위를 정성적으로 주장하고, 컷오프 이후·넓은 종목군 평가나 비용 반영이 없어 앵커 5에는 못 미친다. 골드(T 5)와는 1 차이다.

심층 T 4 (판정 T 4) — 수치 성과 주장이 없고 PIT·blind 대책도 있지만, 전략 YAML 의 "Edge claimed"와 컷오프 이후·비용 반영 평가가 없는 점이 걸린다.

## 수요 신호

Discussions 는 꺼져 있다. 이슈 검색이 #1~#720 전 구간에서 반응·댓글순으로 잡혔다. 상위권은 v1 시절(2024-12~2025-05) 설치 오류와 에러 보고가 많아 버그는 뺐다. 넣은 신호 35개(demand 19·pain 13·gap 3):

- **데이터 API 비용·종속**(가장 두드러짐): #365 Financial Datasets 월 $199 가 비싸니 Yahoo 로 바꾸고 싶다(반응 3, 후속 댓글 "$199/month … out of reach"). 저자는 "AI hedge fund specific subscription pricing"을 곧 내겠다고 답했지만 2025-09 에 "Any update?"가 달린 뒤 소식이 없다. #22(월 $100), #119, #24(yfinance 대체), #469(무료 데이터 소스), #706(2026-08 무료 티어 402, "open source project to require a specific data subscription is weird"), #49 댓글("designed in order to sell the financial dataset")로 이어진다. 저자는 매번 자기 API 품질을 이유로 거절하고 포크를 권했다. 레포가 데이터 판매 퍼널 구실을 한다는 인식이 사용자 사이에 퍼져 있다.
- **LLM 비용**: #3·#13(OpenAI 호환·OpenRouter), #114(Azure 가 더 싸다), #153(Ollama), #124(base URL). v1 에서는 Ollama 로 풀렸지만 v2 에서는 다시 빠졌다.
- **다른 시장**: 중국 A주 #182(반응 12, 저자 "Q2 2025" 약속 뒤 미이행)·#294(반응 8·댓글 8, 홍콩 요청 포함)·#165, 인도 #525·#476, 외환 #43, 크립토 #15·#186, 금·지수 #268. **한국 시장 요청은 "korea"·"KOSPI" 검색 결과 0건이다.** 대만판 포크(KuolungCheng/ai-hedge-fund-tw, ★6)가 있다.
- **실매매·포워드 기록**: #115 데모 지갑으로 몇 주 돌려 수익을 보고 싶다(반응 11, 반응순 1위). #287 돈 번 사람 있나. #597 Zerodha 연동 방법. #507 UPI. 사용자는 백테스트보다 실시간 기록을 원한다.
- **설치·비개발자 마찰**: #29 튜토리얼 영상, #264 Win11 실행 설명서("The Readme's instruction is incorrect."), #9·#145 Docker, #221 `poetry install` 실패. v2 가 `pipx install aihf` 로 이 부분을 크게 줄였다.
- **호스팅·API**: #83 API 키와 종목만 넣으면 되는 Streamlit UI 배포, #186 웹페이지에서 부를 API 서버, #606 웹앱 Docker Compose.
- **신뢰도 표시**(gap): #624 결정이 강한 근거·약한 근거·누락·상충 중 무엇에 기댔는지 보여 달라. #720 모델 기억 누출 측정. README 는 컷오프 이후 창 선택을 사용자에게 맡긴다.

## 파생·상용화

- 본사: 저자(Virat Singh)가 Financial Datasets(financialdatasets.ai) 제작자다. 레포는 무료지만 데이터 API 가 유료이고 저자가 대체 공급원을 받지 않는 구조라, 사실상 데이터 판매의 유입 채널이다. README 는 TypeSafe 의 Jev 모델도 전용 예시로 소개한다(제휴로 보이지만 확인 못 함).
- 포크(★순 상위 10): hackingthemarkets(★24)·fuxiaoyi/ai-hedge-fund-plus(★15, 웹앱)·patchy631·All-About-AI-YouTube 등 강의·유튜브 채널 포크가 대부분이고 모두 ★24 이하다. 포크가 1.1만 개로 많아도 주목받는 파생은 없다. 이슈 댓글에 나온 파생 레포로는 51bitquant/ai-hedge-fund-crypto(크립토), KRSHH/ritadel(yfinance), mapicccy/ai-hedge-stock-futures(A주)가 있다.
- 유료 래퍼: 웹 검색 3회로 이 레포를 감싼 유료 호스팅 서비스는 찾지 못했다. SourceForge 미러와 AI 에이전트 디렉터리 등재, 소개 블로그만 나왔다.

## 내 투자에 쓰려면

- 실행: `pipx install aihf` → `aihf`(TUI). 처음 실행할 때 Financial Datasets 키와 LLM 키 하나를 물어 `~/.hedge-fund/.env` 에 저장한다. 비대화형은 `aihf <mandate.yaml> --tickers AAPL,MSFT [--backtest --start YYYY-MM-DD]` 이고 결과는 stdout 에 JSON 으로 나온다. 이번 조사에서는 설치·실행하지 않았다.
- 주의: (1) 한국 종목은 안 된다. 데이터가 Financial Datasets(미국 SEC 공시) 하나뿐이다. (2) 데이터 구독료가 주된 비용이다. (3) 백테스트 수익을 믿으려면 `--start` 를 쓰는 모델의 학습 컷오프 이후로 잡아야 한다. 수수료·슬리피지가 없으니 결과를 그만큼 깎아서 본다. (4) 페르소나는 재무지표 표 하나만 보고 판단한다(뉴스·가격 모멘텀 없음). (5) 공시가 4기보다 적으면 기권하는데, 대형주에서도 기권이 났다는 보고가 있다(#713). (6) 실매매·페이퍼 기능이 없다. 당일 실행 결과를 참고용 체크리스트로 쓰는 정도가 현실적이다.

## 인디 관점 메모

- 공백: (1) 한국판 — 요청은 0건이지만 A주·인도·대만 요청과 포크를 보면 "내 시장 데이터로 같은 페르소나 펀드"를 바라는 수요가 있다. DART·KRX 재무에 PIT(공시일 기준) 필터를 걸고 페르소나 프롬프트를 붙이면 된다. 데이터가 무료라 원본의 최대 불만(데이터 구독료)을 피할 수 있다. (2) 포워드 기록 — 사용자가 가장 원하는 것(#115·#287)은 백테스트가 아니라 "실제로 몇 주 돌린 결과"다. 페르소나별 공개 페이퍼 트랙레코드 대시보드가 비어 있다. (3) LLM 기억 누출 감사 — #720 같은 모델별 회상 측정과, 컷오프 이후 창을 자동으로 고르는 백테스트는 아무도 제품으로 내지 않았다. (4) 호스팅 — 키와 종목만 넣으면 되는 웹 버전 요청(#83·#186)이 있다.
- 차용: 페르소나 = 시스템 프롬프트 하나인 `LLMAgent` 구조와 bullish/neutral/bearish·confidence JSON 계약, 스냅샷 해시를 키로 쓰는 프롬프트 캐시(공시가 바뀔 때만 LLM 비용 발생), `filing_date` 기반 PIT 스냅샷과 blind 렌더링(티커·날짜 가림, t-0 라벨), "LLM 은 견해만 내고 체결은 결정론 코드" 원칙, 티커 없는 mandate YAML 로 전략과 대상을 분리하는 설계, 판단은 t일 종가·체결은 다음 세션 종가로 나눈 타이밍.
