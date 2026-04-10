# Python Code Style Guide: TradingAgents

## 1. Code Formatting & Style

### PEP 8 Compliance
- Follow PEP 8 with pragmatic exceptions for readability
- Use **Black** formatter (line length: 88 characters)
- Run `black .` before committing code
- Use `isort` for consistent import ordering

### Import Organization
```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Optional, List

# Third-party libraries
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langgraph.graph import StateGraph

# Local imports
from tradingagents.agents import Agent
from tradingagents.config import DEFAULT_CONFIG
```

### Line Length & Wrapping
- Max line length: 88 characters (Black standard)
- Break long lines at logical points
- Align continuation lines for readability

```python
# Good
result = some_function(
    argument1=value1,
    argument2=value2,
    argument3=value3
)

# Avoid
result = some_function(argument1=value1, argument2=value2, argument3=value3)
```

## 2. Type Hints

### Universal Type Hints
- Use type hints on **all** function signatures
- Use Python 3.10+ union syntax (`X | None` instead of `Optional[X]`)
- Type complex return values with TypedDict or Pydantic models

```python
from typing import TypedDict

class TradingDecision(TypedDict):
    action: str  # "buy", "sell", "hold"
    confidence: float  # 0.0 to 1.0
    rationale: str

def analyze_market(ticker: str, date: str) -> TradingDecision:
    """Analyze market and return trading decision."""
    ...
```

### Generic Types
- Use `list[T]` instead of `List[T]` (Python 3.9+)
- Use `dict[K, V]` instead of `Dict[K, V]`
- Be specific: `list[Agent]` not `list`

```python
def process_agents(agents: list[Agent]) -> dict[str, float]:
    """Process multiple agents and return scores."""
    ...
```

## 3. Docstrings

### Style: Google Format
- Use Google-style docstrings for all public functions and classes
- Include Args, Returns, Raises sections
- Provide usage examples for complex functions

```python
def propagate(
    ticker: str,
    date: str,
    config: dict | None = None
) -> tuple[str, TradingDecision]:
    """
    Execute the multi-agent trading framework.
    
    Args:
        ticker: Stock ticker symbol (e.g., "NVDA")
        date: Analysis date in YYYY-MM-DD format
        config: Optional configuration override
    
    Returns:
        Tuple of (analysis_summary, trading_decision)
    
    Raises:
        ValueError: If ticker or date format is invalid
        APIError: If LLM API call fails
    
    Example:
        >>> summary, decision = propagate("NVDA", "2026-01-15")
        >>> print(decision["action"])
        "buy"
    """
    ...
```

### Class Docstrings
```python
class AnalystAgent(Agent):
    """
    Base analyst agent for multi-agent trading framework.
    
    Attributes:
        name: Agent name (e.g., "Fundamental Analyst")
        llm: Language model for analysis
        tools: Available tools for agent use
    """
```

### Private Methods
- Use single-line docstrings for private methods
- Skip Args/Returns if obvious from context

```python
def _extract_metrics(self, data: dict) -> dict:
    """Extract key financial metrics from raw data."""
    ...
```

## 4. Naming Conventions

### Functions & Variables
- Use `snake_case` for functions, methods, variables
- Use UPPERCASE for constants

```python
MAX_DEBATE_ROUNDS = 3
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

def calculate_portfolio_variance(weights: list[float]) -> float:
    pass

investment_amount = 10000
```

### Classes & Agents
- Use `PascalCase` for classes
- Agent classes should end with "Agent" suffix

```python
class FundamentalAnalyst(Agent):
    pass

class SentimentAnalyst(Agent):
    pass

class TradingGraph:
    pass
```

### Private Members
- Prefix with single underscore for internal use
- Use double underscore only for name mangling (rare)

```python
class Agent:
    def __init__(self):
        self._cache = {}  # Internal use
        self.__private_key = "..."  # Name mangling
```

## 5. Module Organization

### Structure
- **One class per module** when classes are complex agents
- **Related utilities** can share modules
- **Keep modules under 500 lines** when possible

```
tradingagents/
├── agents/
│   ├── base.py          # Agent base class
│   ├── analyst.py       # AnalystAgent class
│   ├── trader.py        # TraderAgent class
│   └── risk_manager.py  # RiskManagerAgent class
├── graph/
│   └── trading_graph.py # Multi-agent orchestration
├── config.py            # Configuration management
└── utils/
    └── market_data.py   # Data fetching utilities
```

### Imports at Module Level
- Import dependencies at the top
- Lazy imports only for heavy dependencies (e.g., ML models)

```python
# Good: Import at top
from langchain.chat_models import ChatOpenAI

# Acceptable: Lazy import for heavy dependency
def load_model():
    import torch  # Only import when needed
    return torch.load(...)
```

## 6. Error Handling

### Custom Exceptions
- Define custom exceptions for domain-specific errors
- Inherit from appropriate base class

```python
class TradingAgentError(Exception):
    """Base exception for TradingAgents."""
    pass

class MarketDataError(TradingAgentError):
    """Raised when market data cannot be retrieved."""
    pass

class InvalidConfigError(TradingAgentError):
    """Raised when configuration is invalid."""
    pass
```

### Error Handling Pattern
- Catch specific exceptions, not generic `Exception`
- Provide context in error messages
- Log before raising

```python
import logging

logger = logging.getLogger(__name__)

def fetch_market_data(ticker: str) -> dict:
    try:
        data = yfinance.download(ticker)
        return data
    except Exception as e:
        logger.error(f"Failed to fetch data for {ticker}: {e}")
        raise MarketDataError(f"Cannot fetch data for {ticker}") from e
```

## 7. Configuration Management

### Config-Driven Code
- Configuration stored in Python dicts, not scattered in code
- Provide sensible defaults
- Validate configuration on startup

```python
DEFAULT_CONFIG = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4",
    "quick_think_llm": "gpt-4-mini",
    "max_debate_rounds": 2,
    "temperature": 0.7,
}

def validate_config(config: dict) -> bool:
    """Validate configuration and return True if valid."""
    required_keys = {"llm_provider", "deep_think_llm"}
    if not required_keys.issubset(config.keys()):
        raise InvalidConfigError(f"Missing required config keys")
    return True
```

## 8. Agent Development Pattern

### Creating New Agents
Follow this pattern for consistency:

```python
from tradingagents.agents.base import Agent
from langchain.chat_models.base import BaseChatModel

class CustomAgent(Agent):
    """
    Specialized agent for [purpose].
    
    Attributes:
        name: Agent identifier
        llm: Language model instance
        tools: Available tools
    """
    
    def __init__(self, name: str, llm: BaseChatModel, tools: list | None = None):
        super().__init__(name=name, llm=llm, tools=tools or [])
    
    def analyze(self, data: dict) -> str:
        """
        Analyze input and return insights.
        
        Args:
            data: Input data for analysis
        
        Returns:
            Analysis as structured text
        """
        # Implementation
        pass
    
    def _format_prompt(self, data: dict) -> str:
        """Format input data into prompt."""
        # Private helper
        pass
```

## 9. Testing Conventions

### Test File Organization
- Test files mirror source structure: `tests/test_agents.py` for `tradingagents/agents.py`
- Use `pytest` as testing framework
- Aim for >80% code coverage

```python
# tests/agents/test_analyst.py
import pytest
from tradingagents.agents import FundamentalAnalyst
from tradingagents.exceptions import MarketDataError

class TestFundamentalAnalyst:
    @pytest.fixture
    def analyst(self):
        """Create analyst instance for testing."""
        return FundamentalAnalyst(name="Test", llm=MockLLM())
    
    def test_analyze_returns_string(self, analyst):
        """Test that analyze returns a string."""
        result = analyst.analyze({"ticker": "NVDA"})
        assert isinstance(result, str)
    
    def test_analyze_raises_on_invalid_data(self, analyst):
        """Test error handling for invalid data."""
        with pytest.raises(ValueError):
            analyst.analyze({})  # Missing required field
```

### Mocking LLMs
- Use mock LLMs for deterministic testing
- Don't make real API calls in tests

```python
class MockLLM(BaseChatModel):
    """Mock LLM for testing."""
    def _call(self, messages, **kwargs) -> str:
        return "Mocked response"
    
    @property
    def _llm_type(self) -> str:
        return "mock"
```

## 10. Logging Standards

### Logger Setup
- One logger per module: `logger = logging.getLogger(__name__)`
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR

```python
import logging

logger = logging.getLogger(__name__)

def process_trade(decision: dict) -> bool:
    logger.info(f"Processing trade: {decision['action']}")
    try:
        # Process trade
        logger.debug("Trade processed successfully")
        return True
    except Exception as e:
        logger.error(f"Trade processing failed: {e}")
        raise
```

### Log Levels
- **DEBUG**: Detailed diagnostic information (config values, intermediate steps)
- **INFO**: Confirmations of successful operations
- **WARNING**: Something unexpected happened (retry, fallback behavior)
- **ERROR**: A serious problem (operation failed, cannot recover)

## 11. Code Comments

### When to Comment
- Explain **why**, not what (code shows what)
- Document non-obvious logic or heuristics
- Add references to research papers or external resources

```python
# Good comment: explains reasoning
# Use exponential backoff to avoid overwhelming the API during rate limits
for attempt in range(max_retries):
    delay = base_delay * (2 ** attempt)
    time.sleep(delay)

# Bad comment: just restates code
# Increment counter
count += 1
```

## 12. Performance Considerations

### Async/Await Pattern
- Use async for I/O-bound operations (API calls, file I/O)
- Mark async functions with `async def`

```python
async def fetch_multiple_stocks(tickers: list[str]) -> dict[str, dict]:
    """Fetch data for multiple stocks concurrently."""
    tasks = [fetch_data(ticker) for ticker in tickers]
    return await asyncio.gather(*tasks)
```

### Avoid Premature Optimization
- Profile before optimizing
- Prioritize readability over micro-optimizations
- Document performance-critical sections

## 13. Git & Commit Standards

### Commit Messages
- Format: `type(scope): description`
- Examples:
  - `feat(agent): add sentiment analyzer`
  - `fix(config): validate llm_provider on init`
  - `refactor(graph): simplify debate loop`
  - `docs: update README with multi-LLM example`

### Code Review Checklist
- [ ] Type hints on all functions
- [ ] Docstrings for public APIs
- [ ] Tests added/updated
- [ ] No hardcoded values (use config)
- [ ] Error handling for edge cases
- [ ] Logging for debugging
