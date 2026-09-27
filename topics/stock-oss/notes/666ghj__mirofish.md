---
entity: github:666ghj/mirofish
gh_id: 1104332987
judged: 2026-09-27  rubric: v1
t_deep: 1
tags: [llm-agent, social-simulation, graphrag, scenario-report, zep-dependency, hype-spike, agpl]
---
## 무엇·어떻게

시드 문서(뉴스·정책 초안·보고서·소설)로 지식 그래프를 만든다. 그 그래프의 엔티티를 페르소나 에이전트로 바꿔 가상 Twitter·Reddit 에서 서로 게시·댓글·좋아요를 주고받게 한 뒤, ReportAgent 가 그 로그를 읽고 "예측 리포트"(정성 Markdown)를 쓰는 사회 시뮬레이션 엔진이다. clone HEAD `39d849138ef254f6c737ab4c4705e5545dbe31d4`(2026-09-03), v0.1.2 가 마지막 릴리스이고, 라이선스는 AGPL-3.0 이다. ★75.0k·포크 1.15만·watchers 457 이다. 2025-11 에 만들어졌고 마지막 push 는 2026-09-16 이다. 샨다(盛大)그룹이 인큐베이팅한다.

- 5단계 파이프라인: ① 온톨로지 생성(LLM) → Zep Cloud 에 GraphRAG 구축 ② 엔티티를 OASIS 페르소나로 변환하고, LLM 이 시뮬레이션 설정(시간·활동도·피크 시간대)을 생성 ③ `camel-oasis==0.2.5` 로 Twitter·Reddit 두 플랫폼을 병렬 시뮬레이션하면서 행동 로그를 Zep 그래프에 계속 기록 ④ ReportAgent(ReAct, 도구 호출 최대 5회·반성 2회)가 Zep 그래프를 검색해 리포트 작성 ⑤ 개별 에이전트·ReportAgent 와 대화하거나 설문. 백엔드는 Flask, 프런트는 Vue 다.
- 데이터 소스: 사용자가 올린 PDF·MD·TXT 뿐이다(최대 50MB). 시세·재무 API, 웹 검색, CSV 입력은 없다. `insight_forge`·`panorama_search` 같은 도구 이름에 "search" 가 들어 있지만 실제로는 Zep 그래프만 검색한다(FAQ Q5).
- LLM: OpenAI SDK 호환이면 무엇이든 쓴다. 권장은 알리바바 `qwen-plus` 이고, 코드 기본값은 `gpt-4o-mini` 다. 병렬용 "boost" LLM 을 하나 더 붙일 수 있다. 기억·그래프 층은 **Zep Cloud 만** 공식 지원한다. 시작할 때 `ZEP_API_KEY` 를 검증하고, 자체 호스팅 URL(`ZEP_API_URL`)은 일부러 막아 둔다. 로컬 대체(Neo4j·Graphiti·OpenZep·SQLite)는 커뮤니티 PR(#634·#650 등)로만 있고, 모두 머지되지 않았다.
- 규모: README 는 "thousands of intelligent agents" 라고 하지만, 에이전트 수는 시드 문서에서 뽑힌 엔티티 수로 정해진다. 이슈에 나온 실제 사례는 수십~수백 개다(#322 "agent也有几百个", #183 링크 글 "161个agent").
- 1회 실행 비용(코드 기준 추정, 실측 아님): 기본 설정은 72 시뮬레이션 시간 × 라운드당 60분 = 72 라운드이고, 라운드마다 5~50개 에이전트가 활성화된다(피크 ×1.5). 두 플랫폼을 돌리므로 LLM 호출이 대략 수백~수천 회 나오고, 여기에 온톨로지·페르소나·설정·리포트 생성 호출이 더해진다. 동시 호출 상한은 30 이다. 토큰 집계 기능은 없다(#258·#394, FAQ Q22 "no fixed number"). `.env.example` 자체가 "注意消耗较大，可先进行小于40轮的模拟尝试"(소모가 크니 40라운드 미만으로 먼저 시도하라)라고 경고한다. Zep 무료 한도는 "基本跑一两个实验性的就没了"(실험 한두 번이면 끝, #60)라는 보고가 있다.
- 재현성: 같은 입력을 넣어도 실행마다 온톨로지·엔티티·페르소나 모집단이 새로 만들어진다. 같은 인터뷰 질문의 기권율이 9.5% 와 60.0% 로 갈린 측정이 있다(#751).
- 보안: FAQ Q16 에 따르면 기본값이 `0.0.0.0` 바인딩·CORS 와일드카드·인증 없음이다. 공개 서비스로 띄우면 안 된다.

## 성과 주장의 신뢰도

1. 주장 목록
   - README 개요: "You can inject variables dynamically from a "God's-eye view" to precisely deduce future trajectories — **rehearse the future in a digital sandbox, and win decisions after countless simulations**". 중국어판은 "精准推演未来走向"(미래 향방을 정밀하게 추론한다)이다. 표어는 "Predicting Anything"(预测万物)이다.
   - README Overview: 시드로 "financial signals"(金融信号)를 넣을 수 있다고 적었다. 그런데 "**Financial Prediction**, **Political News Prediction** and more examples coming soon..." 로 금융 예시는 없다.
   - 데모 두 개는 우한대 여론 추론과 『홍루몽』 잃어버린 결말 추론이다. 둘 다 사후에 맞았는지 확인할 수 없는 과제다. 온라인 데모는 LLM 이 붙지 않은 정적 페이지다(#83·#90·#96 에서 메인테이너가 확인). #90 "预测的很好！！！"(예측 잘한다)는 정적 템플릿을 본 사용자의 착각이다.
   - 수치 주장: 레포 안에는 수익률·적중률·브라이어 점수가 하나도 없다. 레포 밖에서는 웹 검색에 X 게시물이 잡혔다. Polymarket 봇에 MiroFish 를 붙여 "$4,266 profit over 338 trades"를 냈다는 제3자 주장인데, 방법·기록 공개가 없어 검증할 수 없다. 샨다가 3천만 위안을 투자했다는 보도(2026-03)도 "예측 엔진"이라는 서사를 키웠다.
2. 면책 문구: README 에는 면책 문구가 **없다**. 이슈 트래커의 메인테이너 답변(2026-07 이후 자동 triage 에이전트 명의)과 FAQ(#725·#726)에만 있다. #237 "The output should be treated as exploratory scenario simulation, not as statistically calibrated price prediction or investment advice.", #312 "A calibrated stock-price prediction product is not planned for the core repository.", FAQ Q25 "provides no calibrated confidence score". 2026-03 #158 에서 저자는 "At that time, we will verify the predictive effectiveness of MiroFish together!"(1.0 이 되면)라고 답해, 아직 검증하지 않았음을 스스로 인정했다. 1에 "precisely deduce future trajectories" 같은 주장이 있으므로, 면책 문구만으로는 5점이 되지 않는다.
3. 검증 수단
   - 백테스트: 없다. 과거 사건을 T0 시점 자료로 돌려 T1 결과와 맞춰 보는 커뮤니티 PR #813 "Historical backtesting framework"(2026-09-15)가 열려 있지만 머지되지 않았다. #433 "Claude/polymarket accuracy improvements" 도 열린 PR 이다.
   - 기간·종목 수·수수료·슬리피지: 해당 없다(가격 모델이 아니다).
   - look-ahead·기억 누출 대책: 없다. 시드 문서의 날짜를 고정하는 장치가 없고, 페르소나·리포트 LLM 이 학습 때 본 사후 지식이 그대로 섞인다.
   - 반복·앙상블: 공식 기능이 없다. 다중 시뮬레이션 합의를 요청한 #17 은 열린 상태다. 여기에 비결정성(#751)까지 겹쳐, 한 번 돌린 결과는 표본 하나에 불과하다.
   - 포워드·페이퍼 기록: 없다. 기계가 읽을 신호 계약(`p_yes`·`confidence` 등)도 없다고 FAQ Q25 가 밝힌다.
4. 판정: 레포는 "정밀한 미래 추론"을 표어로 내세우지만 검증 사례도 방법도 없다. 금융 예시는 9개월째 "coming soon" 이다. 방법이 불명인 주장만 있다는 앵커 1 그대로다. 이슈 트래커에서는 메인테이너가 이 주장을 사실상 철회했지만, README 는 고치지 않았다.

심층 T 1 (판정 T 1) — README 가 "precisely deduce future trajectories" 를 주장하지만 사후 검증·백테스트·반복 실험이 전혀 없고, 메인테이너도 이슈에서 "not calibrated"라고 인정한다.

## 수요 신호

이슈는 410개(PR 제외)이고 Discussions 는 켜져 있다(52개). ★ 75k 에 비해 반응이 극히 적다. 반응순 1위가 17(#117 영어 지원)이고, 10 이상은 두 건뿐이다. 댓글순 상위는 500 오류·무한 대기·Zep 한도 오류 같은 설치·실행 장애가 거의 전부라 버그는 뺐다. 넣은 신호 28개(demand 17·pain 8·gap 3):

- **Zep·토큰 비용**(가장 두드러짐): #23 "有没有开源替换zep，消耗太快了"(Zep 을 대체할 오픈소스는 없나, 너무 빨리 소진된다), #156 "zep免费额度轻松就用完了"(무료 한도가 금방 바닥나 4/5 단계에서 멈춘다), #60 댓글(무료 1000 크레딧이면 실험 한두 번), D669(Zep 키 요구를 없애 달라, 결제 수단도 없다), #183 댓글 "would be great if MiroFish had OpenZep out of the box". 토큰 쪽에서는 #238 댓글 "token花费比挣得钱都多。。。"(토큰비가 번 돈보다 많다. 퀀트 전략 모임 글에 달렸다), D193 "the token burn was too high", #424(무료 한도가 끝나면 다른 모델로 넘기기), #394·D7(토큰 계산 기준과 프런트 표시 요청), D193 본문(목표 합의 수준에 필요한 최소 에이전트 수 추정과 조기 종료).
- **긴 작업 실패와 이어하기**: #688 "每次失败都要耗费大量的时间和成本"(실패할 때마다 시간과 비용이 크게 든다), D349 세션 resume 요청. 메인테이너가 단계 간 이어하기는 미구현이라고 확인했다.
- **예측 검증 요구**: #158 "Are there any predictions that have been verified by subsequent events?", #17 다중 시뮬레이션 + 메타 리포트 합의로 신뢰도 높이기(반응 5, 열림), #751 비결정성 때문에 실행끼리 비교할 수 없음(gap), #813 백테스트 프레임워크 PR(gap), #472 페르소나가 배경과 무관하게 비슷하게 행동한다(보정 요구).
- **금융 예측 요구**: #312 "搞一个股票未来价格的预测吧，这种泛泛而谈的算命好像没什么用"(주가 예측을 해 달라, 이렇게 두루뭉술한 점술은 쓸모없다), D280·#279 주식·크립토 예측 가능 여부, #237 금융 예측 사례 요청, #277 트레이딩 파이프라인용 JSON 신호 스키마 요구. #434·#412·#458·#545·#566·#684·#777(인도·파키스탄·네팔 주식, 옵션 행사가, 크립토, 복권) 같은 "내일 오를까요" 글이 10건 넘게 달렸다. 모두 비개발자가 이슈 트래커를 예측 서비스로 착각해 쓴 것이다. 대표로 #434 한 건만 넣었다.
- **호스팅**: 공식 호스팅은 없다. 그 공백을 무단 유료 사이트(mirofish.us·.my·.homes·.co.in·.best·.work 등)가 메웠다. D473(USDT 로 50 크레딧 결제 후 미지급, 댓글 6)·D603·#704(스타터 플랜 구매자 "I’m not a programmer")·#639(유료 제품인데 리포트가 고정 템플릿) 등 피해 보고가 이어졌다. 비개발자 사이에 "돈 내고 쓸" 수요가 실제로 있다는 신호로 D473 을 demand 로 넣었다.
- **다국어**: #117(반응 17)·#182(반응 9) 영어·i18n 요청. PR #428 로 중/영 UI 가 들어갔다. **한국어는 이슈 요청이 0건이다.** 한국어 PR 3건(#112·#201·#214)은 모두 머지되지 않고 닫혔다. 비공식 한국어판 포크 ByeongkiJeong/MiroFish-Ko(★224, 2026-03 이후 멈춤)가 포크 ★순 1위다.
- **품질 불만**: #67 "生成内容过于离谱"(생성 내용이 너무 황당하다). 고풍 연애소설을 넣었더니 2049년 블록체인 혼약 리포트와 가짜 통계(94.2% 이행률 등)가 나왔다.

## 파생·상용화

- 본사: 공식 유료 상품은 없다(FAQ Q2 "does not sell, operate, or authorize any paid Starter Plan"). 샨다그룹 인큐베이션과 채용 공고가 README 에 있다. 홈페이지 mirofish.ai 를 등록해 두었지만, 공식 호스팅 계산 서비스는 없다고 밝혔다.
- 무단 상용 래퍼: mirofish.us·mirofish.my·mirofish.homes·mirofish.co.in 은 메인테이너가 비공식이라고 공지했다. 웹 검색에서는 mirofish.best·mirofish.work 도 "paid plans… hosted checkout" 을 내걸고 있었다. 크레딧·스타터 플랜을 USDT·카드로 판다. 일부는 결제 후 서비스를 주지 않았다는 보고가 있고, 리포트가 고정 템플릿이라는 보고(#639)도 있다. 이름값만으로 유료 호스팅이 팔리는 드문 사례다.
- 포크(★순 상위 10): MiroFish-Ko(★224, 한국어), JayFarei(★69, Claude 호환), tcsn-xy(★56, 장시간 자율 예측), MiroFish-EN·ES(번역), go-mirofish(★15). 포크가 1.15만 개인데 ★100 을 넘는 파생은 한국어판 하나다.
- 금융 파생: freenowill/stock-fish(★82, "巴菲特、查理芒格、量化大师…左右互博", 퀀트 팩터 선별 + 에이전트 토론 + MiroFish 군집 추론, 2026-07 이후 멈춤), vinayr1973-sudo/trading-ril(★1, CME 마이크로 선물 신호 검증), ama353-arch/mirofish-trading-strategy(★1). 여기에 FeedOracle(D310, 유료 MCP 데이터)·Infernex(D345, 저가 LLM)·agentpay-mcp(#399, 자동 결제) 같은 벤더가 이슈·토론을 홍보 채널로 쓴다.

## 내 투자에 쓰려면

- 실행: `cp .env.example .env` 에 LLM 키와 Zep Cloud 키를 넣고 `npm run setup:all && npm run dev` 한다(Node 18+, Python 3.11~3.12, uv). 또는 `docker compose up -d` 한 뒤 `localhost:3000` 으로 연다. 이번 조사에서는 설치·실행하지 않았다.
- 주의: (1) 가격·재무 데이터를 넣을 경로가 없다. 뉴스·리포트 문서를 넣어 "이 이벤트에 대중·기관이 어떻게 반응할까" 시나리오를 읽는 용도가 한계다. (2) 결과는 정성 Markdown 이고 실행마다 달라진다(#751). 매매 신호로 쓰면 안 된다(FAQ Q25). (3) 사후 지식이 섞인다. 과거 사건으로 "맞았는지" 볼 때 LLM 이 결과를 이미 알고 있을 수 있다. (4) 비용이 예측하기 어렵다. Zep 무료 한도는 한두 번이면 끝나고, 40라운드 미만으로 먼저 돌려 봐야 한다. (5) 한국어 UI·출력 설정이 없다. LLM 지시(`llmInstruction`)는 zh·en 등 7개 언어뿐이다. (6) 인증이 없으니 로컬에서만 띄운다.
- 현실적 용도: 실적 발표나 정책 뉴스가 나온 뒤 "투자자 커뮤니티 반응 시나리오"를 여러 번 돌려 보고, 공통으로 나오는 논점을 체크리스트로 쓰는 정도다.

## 인디 관점 메모

- 공백: (1) **검증된 여론 시뮬레이션**. #158·#17·#813 이 요구하는 것은 "사후에 맞았나"다. 과거 사건을 시점 고정(T0 자료만)으로 돌리고 브라이어 점수·방향 적중으로 공개 채점하는 트랙레코드 보드가 비어 있다. (2) **호스팅**. 비개발자가 무단 사이트에 USDT 를 낼 정도로 "설치 없이 한 번 돌려 보기" 수요가 있다. 공식도 정직한 유료 호스팅도 없다. 다만 1회 비용이 크고 들쭉날쭉해, 크레딧 단가를 정하기 어렵다. (3) **한국판**. 요청은 0건이지만, 한국어 포크가 파생 ★ 1위다. 종목 토론방·뉴스 댓글을 시드로 "공시 후 개인 투자자 반응 시뮬레이션"을 하는 한국 시장 특화판은 아무도 하지 않았다. (4) **비용 제어**. 필요 에이전트 수 추정·조기 종료(D193)와 토큰 집계(#394)가 없다.
- 차용: 문서 → 온톨로지 → 엔티티 → 페르소나로 이어지는 자동 캐스팅 파이프라인, 시간대별 활동도·피크 배수로 에이전트를 확률적으로 활성화하는 스케줄러(`get_active_agents_for_round`), 시뮬레이션이 끝난 뒤 에이전트를 인터뷰·설문하는 기능, "God's-eye view" 변수 주입이라는 UX 표현.
- 의심: ★ 급증은 2026-03 한 달에 약 4.2만(일 최대 +3.7k, 3/7 GitHub Trending 1위, 샨다 투자 보도와 겹침)에 몰렸다. 이후는 월 1~4k 로 가라앉았다. 현재 Δ30 3.4k 는 이 여진이다. watchers 457(★의 0.6%)과 이슈 반응 최대 17을 보면, 실제로 돌려 보는 사용자에 비해 스타가 훨씬 많다. 스타 조작보다는 미디어 화제성으로 몰린 것으로 보인다.
