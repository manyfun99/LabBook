# 골드셋 비교 — rubric v1 (2026-09-27)

축별 ±1 이내 일치율: P 100% · I 100% · N 100% · T 89% · 전체 97%
판정 실패: shiyu-coder/Kronos (일치율 계산에서 뺌)

| 레포 | P (LLM/나) | I (LLM/나) | N (LLM/나) | T (LLM/나) | 내 메모 |
|---|---|---|---|---|---|
| virattt/ai-hedge-fund | 3/3 | 3/3 | 4/5 | 4/5 | 설치 쉬우나 Financial Datasets 키 필요·미국만. 대가 페르소나 에이전트는 GuruNote 에 바로 차용. 성과 주장 없고 백테스트 누출 완화 명시 |
| TauricResearch/TradingAgents | 4/3 | 3/3 | 5/4 | 4/2 ⚠ | 무료 데이터로 돌아가나 LLM 키·설정 필요. 역할 분담 토론 구조는 이미 흔해짐. 논문 성과가 재현 안 된다는 이슈, 누출 대책은 최근 추가 |
| HKUDS/Vibe-Trading | 4/4 | 3/3 | 5/4 | 4/4 | pip 설치·무료 데이터·KRX 백테스트 엔진·Web UI. 한국 증권사 커넥터 없음. 수익 주장 대신 검증 가능한 실행 기록을 내세움 |
| HKUDS/AI-Trader | 2/2 | 3/2 | 4/3 | 3/3 | 에이전트끼리 매매하는 호스팅 플랫폼이라 내 리서치 도구는 아님. SKILL.md 로 에이전트 가입시키는 방식은 참고. 라이브 리더보드는 있으나 백테스트·누출 근거 요구 이슈 |
| dragon1086/prism-insight | 4/3 | 2/3 | 5/5 | 4/5 | 한국 시장·텔레그램 리포트로 GuruNote 인접 경쟁자. 설정은 키가 많아 무거움. Stance 의 무소급 공개 기록·서버 봉인 판단 시각은 포워드 성적표 아이디어로 그대로 차용 가능 |
| Nunchi-trade/auto-researchtrading | 1/1 | 2/1 | 4/3 | 2/1 | 하이퍼리퀴드 무기한 선물이라 내 투자와 무관. autoresearch 루프 적용은 참고. Sharpe 21.4 주장에 look-ahead·표본 외 붕괴 이슈 |
| Y-Research-SBU/QuantHarness | 3/2 | 3/2 | 3/3 | 2/2 | 고빈도·단기 차트 분석이라 중장기와 안 맞음. 차트 이미지를 비전 LLM 으로 읽는 패턴 에이전트는 부분적 신기법. 독립 감사가 기여도 재현 실패 |
| 666ghj/MiroFish | 2/1 | 3/2 | 4/3 | 1/2 | 주식 전용이 아닌 범용 여론 시뮬레이션이고 Zep 비용 부담. 비개발자 설치 오류·비용 불만은 있으나 금융 수요는 아님. 예측 주장만 있고 평가 없음 |
| financial-datasets/mcp-server | 2/2 | 2/2 | 2/2 | 5/5 | 유료 API 키 필요·미국만. 흔한 MCP 래퍼. 데이터 도구라 성과 주장 없음 |
| FinanceData/FinanceDataReader | 5/5 | 3/3 | 3/3 | 5/5 | 무료로 한국·미국 가격·지수·재무를 CLI 로 바로 조회. KRX 변경으로 자주 깨지는 이슈는 안정적 한국 데이터 수요 신호. 데이터 도구 |
| koala73/worldmonitor | 3/3 | 3/4 | 4/4 | 5/5 | 호스팅 사이트로 거시·지정학 파악에 무료 사용 가능하나 종목 리서치는 아님. Pro 버전·대기자 요청 이슈로 호스팅 수요 확인, 한국어판 없음. AI 브리프·국가 불안정 지수 구성 차용 가능 |
| microsoft/qlib | 3/2 | 2/1 | 4/4 | 3/3 | 데이터 스크립트부터 깨지는 이슈가 많고 ML 퀀트 연구용. Alpha158 팩터·RD-Agent 팩터 발굴은 차용 가치. 표준 백테스트 벤치마크 공개 |
| ZhuLinsen/daily_stock_analysis | 4/4 | 3/4 | 4/5 | 4/2 ⚠ | 한국·미국 주식 포함, GitHub Actions 로 무료 매일 분석 후 텔레그램 푸시. 비개발자 대상 5분 배포 안내·65k★, 한국어판 없음. 결정 대시보드·무료 소스 폴백·Actions 스케줄은 GuruNote 에 직접 차용. 매매 시점 제시에 검증 근거 없음 |
| OpenBB-finance/OpenBB | 4/4 | 2/2 | 4/4 | 5/5 | pip 설치 후 무료 공급자로 미국 데이터 바로 조회(일부 공급자는 키 필요, 한국 없음). 분석가·개발자 대상. 한 번 연결해 Python·MCP·REST 로 내보내는 공급자 추상화 차용 가능 |
| Fincept-Corporation/FinceptTerminal | 3/2 | 3/3 | 3/2 | 5/5 | 설치 실패·데이터 없음 이슈가 상위이고 유료 판매 광고 위주. 비개발자 수요는 있으나 대체재 많음. 기능 묶음 이상의 설계는 약함. 성과 주장 없음 |
| freqtrade/freqtrade | 1/1 | 2/1 | 4/3 | 5/5 | 크립토 봇이라 내 투자와 무관, 개발자 대상 성숙 시장. 드라이런·하이퍼옵트·텔레그램 제어는 부분 참고. 도구라 성과 주장 없음 |
| myhhub/stock | 1/1 | 3/2 | 3/3 | 4/3 | A주 전용. 중국 비개발자의 배포 오류(빈 화면·Docker)는 호스팅 수요지만 한국과 무관. 200조건 스크리너·K선 형태 61종 구성은 부분 참고. 선택 검증 백테스트는 있으나 근거 수치 없음 |
| ccxt/ccxt | 1/1 | 2/1 | 4/4 | 5/5 | 크립토 거래소 API 라 내 투자와 무관, 개발자 전용. 100여 거래소를 하나의 API 로 정규화한 설계는 한국 증권사 통합 API 아이디어로 차용 가능. 성과 주장 없음 |
| nautechsystems/nautilus_trader | 2/1 | 2/1 | 4/4 | 5/5 | 프로덕션 매매 엔진이라 개인 리서치 용도 아님, 개발자 전용. 백테스트·라이브 동일 코드의 결정론적 이벤트 구조는 차용 가치. 인프라라 성과 주장 없음 |

## LLM 근거

- **virattt/ai-hedge-fund** — P: A [Financial Datasets](https://financialdatasets.ai) API key, for prices, fundam / I: please make a tutorial video / N: So a backtest withholds the ticker, industry and calendar dates from the investo / T: This reduces the recall without removing it (distinctive numbers can still give 
- **TauricResearch/TradingAgents** — P: TradingAgents works with any market Yahoo Finance covers, using the exchange-suf / I: 有没有大佬能改成使用deepseek的适用于A股的版本？ / N: A run dated in the past then reads the statements exactly as they stood that day / T: Treat the framework as a research scaffold for studying multi-agent analysis, no
- **HKUDS/Vibe-Trading** — P: **KIS** (한국투자증권; a genuine 모의투자 paper sandbox on its own host, plus read-only li / I: Improve UI usability and add Chinese localization for non-technical users / N: The model now declares what each figure is in a `figures` block the reader never / T: the gate reads only a number's shape and checks every declaration against the se
- **HKUDS/AI-Trader** — P: Start your trading journey with zero risk: / I: Slow initial loading and unclear onboarding for international users / N: Any AI agent joins the **AI-Trader** platform in seconds -- Simply send this mes / T: [Bug] Future Information Leakage (Lookahead Bias) in `get_information` Tool Duri
- **dragon1086/prism-insight** — P: PRISM-INSIGHT is a **completely open-source, free** AI-powered stock analysis sy / I: Currently serving 450+ users for free. / N: the server seals decision time and price, then calculates what happens next / T: 2025.09.30 ~ 2026.03.24
- **Nunchi-trade/auto-researchtrading** — P: Karpathy-style autoresearch for Hyperliquid perpetual futures — 103 experiments, / I: need docker image / N: An AI agent autonomously modifies a single file (`strategy.py`), backtests each  / T: Independent Out-of-Sample Validation: Sharpe collapses on longer history
- **Y-Research-SBU/QuantHarness** — P: Real-time market data from Yahoo Finance / I: python web_interface.py跑不起来 / N: Our model requires an LLM that can take images as input, as our agents generate  / T: independent audit of 4 vision LLMs on 40 verified signals could not reproduce Pa
- **666ghj/MiroFish** — P: **Financial Prediction**, **Political News Prediction** and more examples coming / I: 可以预测股票吗？ / N: Seed extraction & Individual/collective memory injection & GraphRAG construction / T: You can inject variables dynamically from a "God's-eye view" to precisely deduce
- **financial-datasets/mcp-server** — P: FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key / I: Feature Make package installable via pip (not just a script) / N: It allows Claude and other AI assistants to retrieve income statements, balance  / T: This is a Model Context Protocol (MCP) server that provides access to stock mark
- **FinanceData/FinanceDataReader** — P: pip install finance-datareader / I: ModuleNotFoundError: No module named 'FinanceDataReader' 가 발생합니다 / N: df = fdr.DataReader('KRX:000150', '2020-01-01') # 두산:KRX 종목 (한국거래소 데이터) / T: The FinanceDataReader is financial data reader(crawler) for finance.
- **koala73/worldmonitor** — P: The app runs with no environment variables. / I: Pro Version / N: World Monitor is built for agents and scripts as well as browsers: / T: Real-time global intelligence dashboard. AI-powered news aggregation, geopolitic
- **microsoft/qlib** — P: Due to more restrict data security policy. The official dataset is disabled temp / I: public access error when running get_data script / N: It contains the full ML pipeline of data processing, model training, back-testin / T: Though with *public data* and *simple models*, machine learning technologies **w
- **ZhuLinsen/daily_stock_analysis** — P: 项目默认内置 AkShare、Baostock、YFinance 等免费行情源，可零配置运行；免费源受上游限流、接口变动和网络波动影响，稳定性不保证。 / I: [Feature] 交流群 / N: 每日自动分析并推送「决策仪表盘」到企业微信/飞书/Telegram/Discord/Slack/邮箱 / T: 本项目仅供学习和研究使用，不构成任何投资建议。
- **OpenBB-finance/OpenBB** — P: Get started with: `pip install openbb` / I: Open Data Platform by OpenBB (ODP) is the open-source toolset that helps data en / N: ODP operates as the "connect once, consume everywhere" infrastructure layer that / T: The data contained in the Open Data Platform is not necessarily accurate.
- **Fincept-Corporation/FinceptTerminal** — P: 100+ connectors: FRED, IMF, World Bank, DBnomics, AkShare, Polygon, Kraken, Yaho / I: [BUG] Failed to set up on mac / N: 37 trader/investor, economic and geopolitics agents; bring your own key (OpenAI, / T: is a native C++20 desktop terminal for financial research — Qt6 UI, embedded Pyt
- **freqtrade/freqtrade** — P: Freqtrade is a free and open source crypto trading bot written in Python. / I: Running freqtrade on AWS EC2 (VPS) / N: lookahead-analysis  Check for potential look ahead bias. / T: This software is for educational purposes only.
- **myhhub/stock** — P: 抓取A股票每日数据，主要为一些关键数据，同时封装抓取方法，方便扩展系统获取个人关注的数据。 / I: 页面打开都是空白的看过来 / N: 筹码分布通过计算一定时间范围内股票的:最高价、最低价、成交数，输出对应价格成交数占整个流通盘比值的分布图形。 / T: 对指标、策略等选出的股票进行回测，验证策略的成功率，是否可用。
- **ccxt/ccxt** — P: The **CCXT** library is used to connect and trade with cryptocurrency exchanges  / I: New Exchange: Upbit / N: optionally normalizes data for cross-exchange analytics and arbitrage / T: implements public and private APIs, both REST and WebSocket
- **nautechsystems/nautilus_trader** — P: The open-source project focuses on single-node backtesting and live trading for  / I: UI dashboards, distributed orchestration, and built-in AI/ML tooling are out of  / N: A Rust-native core provides a deterministic event-driven runtime for both resear / T: Live execution still introduces venue, transport, timing, persistence,
