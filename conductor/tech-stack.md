# Technology Stack: TradingAgents

## Core Language & Runtime
- **Language**: Python 3.10+
- **Package Manager**: pip with pyproject.toml
- **Virtual Environment**: Conda/venv compatible

## Multi-Agent Framework
- **LangChain**: Chain-based LLM workflows and tool integration
- **LangGraph**: State machine for multi-agent orchestration
- **Chainlit**: Web UI framework for interactive agent monitoring

## LLM Providers (Pluggable)
TradingAgents supports multiple LLM backends without requiring all:
- **OpenAI**: GPT-5.x models (default)
- **Google**: Gemini 3.x models
- **Anthropic**: Claude 4.x models
- **xAI**: Grok 4.x models
- **OpenRouter**: Unified API for multiple providers
- **Ollama**: Local model support (Llama, Qwen, etc.)

## Market Data & Analysis
- **yfinance**: Stock price and financial data
- **Alpha Vantage**: Technical indicators and market data
- **Pandas**: Data manipulation and time-series analysis
- **stockstats**: Technical analysis indicators (MACD, RSI, etc.)
- **Numpy**: Numerical computations

## Backtesting & Trading Simulation
- **Backtrader**: Event-driven backtesting framework
- Supports historical data validation and performance metrics

## User Interfaces
- **CLI**: Typer (command-line argument parsing)
- **Terminal UI**: Rich (formatted tables, progress bars, styling)
- **Interactive Prompts**: Questionary (CLI user input)
- **Web Dashboard**: Chainlit (real-time agent monitoring)

## Asynchronous & Concurrency
- **asyncio**: Async/await for I/O-bound operations
- **aiohttp**: Async HTTP client for API calls
- **greenlet**: Lightweight concurrency

## State Management & Caching
- **Redis**: Session caching and state persistence
- **langsmith**: LLM observability and tracing

## Observability & Monitoring
- **OpenTelemetry**: Distributed tracing and metrics
- **Logging**: Python standard logging with structured records

## Data Parsing & Validation
- **Pydantic**: Data validation and schema definition
- **parsel**: HTML/CSS selector parsing (web scraping)
- **BeautifulSoup4**: HTML parsing
- **rank-bm25**: BM25 search/ranking for document retrieval

## Development & Deployment
- **setuptools**: Package distribution
- **pytz**: Timezone handling
- **python-dotenv**: Environment variable management
- **requests**: HTTP client

## Design Rationale

### Modularity
- Each layer (data, agents, trading, UI) is independently replaceable
- LLM providers are pluggable; users choose their preferred model

### Scalability
- Async operations for concurrent API calls
- Redis for distributed state management
- LangGraph for complex agent workflows

### Extensibility
- New agents can be added following established patterns
- Configuration-driven behavior reduces coupling
- Support for custom LLM backends via OpenRouter

### Research-First
- Backtesting built-in for reproducible research
- OpenTelemetry integration for detailed observability
- Both CLI and programmatic APIs for flexibility
