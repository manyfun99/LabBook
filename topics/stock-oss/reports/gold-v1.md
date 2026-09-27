# 골드셋 비교 — rubric v1 (2026-09-27)

축별 ±1 이내 일치율: P 100% · I 100% · N 100% · T 100% · 전체 100%
판정 실패: TauricResearch/TradingAgents, dragon1086/prism-insight, Nunchi-trade/auto-researchtrading, shiyu-coder/Kronos, 666ghj/MiroFish, FinanceData/FinanceDataReader, koala73/worldmonitor, ZhuLinsen/daily_stock_analysis, Fincept-Corporation/FinceptTerminal, myhhub/stock (일치율 계산에서 뺌)

| 레포 | P (LLM/나) | I (LLM/나) | N (LLM/나) | T (LLM/나) | 내 메모 |
|---|---|---|---|---|---|
| virattt/ai-hedge-fund | 3/3 | 4/3 | 4/5 | 5/5 | 설치 쉬우나 Financial Datasets 키 필요·미국만. 대가 페르소나 에이전트는 GuruNote 에 바로 차용. 성과 주장 없고 백테스트 누출 완화 명시 |
| HKUDS/Vibe-Trading | 4/4 | 3/3 | 5/4 | 4/4 | pip 설치·무료 데이터·KRX 백테스트 엔진·Web UI. 한국 증권사 커넥터 없음. 수익 주장 대신 검증 가능한 실행 기록을 내세움 |
| HKUDS/AI-Trader | 2/2 | 3/2 | 4/3 | 3/3 | 에이전트끼리 매매하는 호스팅 플랫폼이라 내 리서치 도구는 아님. SKILL.md 로 에이전트 가입시키는 방식은 참고. 라이브 리더보드는 있으나 백테스트·누출 근거 요구 이슈 |
| Y-Research-SBU/QuantHarness | 2/2 | 3/2 | 3/3 | 2/2 | 고빈도·단기 차트 분석이라 중장기와 안 맞음. 차트 이미지를 비전 LLM 으로 읽는 패턴 에이전트는 부분적 신기법. 독립 감사가 기여도 재현 실패 |
| financial-datasets/mcp-server | 3/2 | 2/2 | 2/2 | 5/5 | 유료 API 키 필요·미국만. 흔한 MCP 래퍼. 데이터 도구라 성과 주장 없음 |
| microsoft/qlib | 2/2 | 2/1 | 4/4 | 3/3 | 데이터 스크립트부터 깨지는 이슈가 많고 ML 퀀트 연구용. Alpha158 팩터·RD-Agent 팩터 발굴은 차용 가치. 표준 백테스트 벤치마크 공개 |
| OpenBB-finance/OpenBB | 4/4 | 2/2 | 4/4 | 5/5 | pip 설치 후 무료 공급자로 미국 데이터 바로 조회(일부 공급자는 키 필요, 한국 없음). 분석가·개발자 대상. 한 번 연결해 Python·MCP·REST 로 내보내는 공급자 추상화 차용 가능 |
| freqtrade/freqtrade | 1/1 | 2/1 | 4/3 | 5/5 | 크립토 봇이라 내 투자와 무관, 개발자 대상 성숙 시장. 드라이런·하이퍼옵트·텔레그램 제어는 부분 참고. 도구라 성과 주장 없음 |
| ccxt/ccxt | 1/1 | 2/1 | 4/4 | 5/5 | 크립토 거래소 API 라 내 투자와 무관, 개발자 전용. 100여 거래소를 하나의 API 로 정규화한 설계는 한국 증권사 통합 API 아이디어로 차용 가능. 성과 주장 없음 |
| nautechsystems/nautilus_trader | 2/1 | 2/1 | 4/4 | 5/5 | 프로덕션 매매 엔진이라 개인 리서치 용도 아님, 개발자 전용. 백테스트·라이브 동일 코드의 결정론적 이벤트 구조는 차용 가치. 인프라라 성과 주장 없음 |

## LLM 근거

- **virattt/ai-hedge-fund** — P: A [Financial Datasets](https://financialdatasets.ai) API key, for prices, fundam / I: please make a tutorial video / N: So a backtest withholds the ticker, industry and calendar dates from the investo / T: This reduces the recall without removing it (distinctive numbers can still give 
- **HKUDS/Vibe-Trading** — P: **KIS** (한국투자증권; a genuine 모의투자 paper sandbox on its own host, plus read-only li / I: Improve UI usability and add Chinese localization for non-technical users / N: The model now declares what each figure is in a `figures` block the reader never / T: [Roadmap] Financial correctness hardening: live gates, backtest engines, shadow-
- **HKUDS/AI-Trader** — P: Copy `.env.example` to `.env` and choose **one** database backend: / I: Slow initial loading and unclear onboarding for international users / N: Any AI agent joins the **AI-Trader** platform in seconds -- Simply send this mes / T: [Bug] Future Information Leakage (Lookahead Bias) in `get_information` Tool Duri
- **Y-Research-SBU/QuantHarness** — P: QuantHarness: Price-Driven Multi-Agent LLMs for High-Frequency Trading / I: python web_interface.py跑不起来 / N: Our model requires an LLM that can take images as input, as our agents generate  / T: Request: ablation data, benchmark scoring code, and significance tests — indepen
- **financial-datasets/mcp-server** — P: FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key / I: Feature Make package installable via pip (not just a script) (댓글 2) / N: It allows Claude and other AI assistants to retrieve income statements, balance  / T: This is a Model Context Protocol (MCP) server that provides access to stock mark
- **microsoft/qlib** — P: ❗ Due to more restrict data security policy. The official dataset is disabled te / I: 一个很好的第三方编写的Qlib中文技术教程 / N: It contains the full ML pipeline of data processing, model training, back-testin / T: The performance of each model on the `Alpha158` and `Alpha360` datasets can be f
- **OpenBB-finance/OpenBB** — P: Get started with: `pip install openbb` / I: [Bug] Ubuntu docker shows white blank window instead of charts / N: ODP operates as the "connect once, consume everywhere" infrastructure layer that / T: Open Data Platform for analysts, quants and AI agents.
- **freqtrade/freqtrade** — P: Freqtrade is a free and open source crypto trading bot written in Python. It is  / I: We strongly recommend you to have coding and Python knowledge. / N: lookahead-analysis  Check for potential look ahead bias. / T: This software is for educational purposes only. Do not risk money which
you are 
- **ccxt/ccxt** — P: A crypto trading API with more than 100 exchanges and prediction markets in Java / I: It is intended to be used by **coders, developers, technically-skilled traders,  / N: optionally normalizes data for cross-exchange analytics and arbitrage / T: It provides quick access to market data for storage, analysis, visualization, in
- **nautechsystems/nautilus_trader** — P: The open-source project focuses on single-node backtesting and live trading for  / I: UI dashboards, distributed orchestration, and built-in AI/ML tooling are out of  / N: A Rust-native core provides a deterministic event-driven runtime for both resear / T: Live execution still introduces venue, transport, timing, persistence,
external-
