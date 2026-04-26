# Development Workflow: TradingAgents

## Overview
This document defines the standard development workflow for TradingAgents. All work follows a structured, test-driven approach with clear quality gates and documentation requirements.

## 1. Development Methodology

### Test-Driven Development (TDD)
1. **Write tests first**: Define expected behavior in tests before implementing
2. **Make tests fail**: Verify that tests initially fail (Red phase)
3. **Implement minimum code**: Write just enough code to pass tests (Green phase)
4. **Refactor**: Improve code while keeping tests passing (Refactor phase)

### Code Coverage Requirement
- **Minimum**: >80% code coverage for all new/modified code
- **Target**: >85% project-wide coverage
- **Coverage Tool**: `pytest-cov`
- **Enforcement**: Coverage reports generated and reviewed before merge

```bash
# Check coverage before commit
pytest --cov=tradingagents --cov-report=term-missing tests/
```

## 2. Task Execution Flow

### Phase 1: Planning
- [ ] Read track specification (`spec.md`)
- [ ] Understand acceptance criteria
- [ ] Identify dependencies and risks
- [ ] Ask clarifying questions if needed

### Phase 2: Test Definition
- [ ] Write unit tests for core logic
- [ ] Write integration tests for agent interactions
- [ ] Write tests for edge cases and error conditions
- [ ] All tests should fail initially

```python
# Example test structure
class TestFundamentalAnalyst:
    def test_analyze_valid_data(self):
        """Test analyze with valid financial data."""
        ...
    
    def test_analyze_missing_fields(self):
        """Test error handling for missing required fields."""
        ...
    
    def test_analyze_concurrent_requests(self):
        """Test concurrent analysis requests."""
        ...
```

### Phase 3: Implementation
- [ ] Implement feature to pass all tests
- [ ] Follow Python Code Style Guide (see `code_styleguides/python.md`)
- [ ] Add type hints to all functions
- [ ] Write Google-style docstrings
- [ ] Add debug logging for traceability

### Phase 4: Integration Testing
- [ ] Run all tests: `pytest tests/`
- [ ] Verify coverage: `pytest --cov=tradingagents tests/`
- [ ] Test with real LLM if applicable (with mocks for CI)
- [ ] Test with multiple configurations (different LLM providers)
- [ ] Verify no regressions in existing functionality

### Phase 5: Code Quality & Review
- [ ] Format code with Black: `black tradingagents/`
- [ ] Sort imports with isort: `isort tradingagents/`
- [ ] Type check with mypy (optional): `mypy tradingagents/`
- [ ] Review against Code Style Guide
- [ ] Update documentation and examples

### Phase 6: Documentation
- [ ] Update README.md if user-facing changes
- [ ] Add/update docstrings
- [ ] Include code examples in docstrings
- [ ] Update CHANGELOG or release notes
- [ ] Document new configuration options

## 3. Commit Strategy

### Per-Task Commits
- **One commit per task** (atomic, focused changes)
- **No cherry-picking or squashing** unless explicitly requested
- **Each commit is independently buildable and testable**

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `test`: Test additions/updates
- `docs`: Documentation
- `ci`: CI/CD configuration
- `chore`: Build, dependencies, etc.

**Scope Examples:**
- `agent`: Changes to agent classes
- `graph`: Changes to multi-agent orchestration
- `config`: Configuration management
- `cli`: Command-line interface
- `backtest`: Backtesting functionality

**Examples:**
```
feat(agent): implement sentiment analyst

- Add SentimentAnalyst class that scores social media sentiment
- Integrate with news sources API
- Add 5 unit tests covering edge cases
- Ensure >80% coverage

Resolves #123
```

```
fix(config): validate llm_provider on initialization

- Check that llm_provider is in supported list
- Raise InvalidConfigError with helpful message
- Update validation tests

Closes #456
```

## 4. Code Review Checklist

### Before Committing
- [ ] All tests pass: `pytest tests/`
- [ ] Coverage >80%: `pytest --cov`
- [ ] Code formatted: `black tradingagents/`
- [ ] Imports sorted: `isort tradingagents/`
- [ ] Type hints on all functions
- [ ] Docstrings present (Google format)
- [ ] No debug print statements
- [ ] No hardcoded values (use config)
- [ ] Error handling for edge cases
- [ ] Logging statements for key operations
- [ ] Commit message follows format

### Code Quality Standards
- **Readability**: Code is self-explanatory with clear variable names
- **DRY**: No significant code duplication
- **SOLID**: Single responsibility, dependency injection
- **Testing**: Comprehensive unit and integration tests
- **Documentation**: Clear docstrings and comments where needed

## 5. Configuration Management

### Config Structure
Configurations should be:
- **Centralized**: Single source of truth in `default_config.py`
- **Validated**: Runtime validation of required fields
- **Documented**: Every option explained with examples
- **Flexible**: Support overrides without modifying core files

```python
DEFAULT_CONFIG = {
    # LLM Configuration
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4",
    "quick_think_llm": "gpt-4-mini",
    "temperature": 0.7,
    
    # Agent Configuration
    "max_debate_rounds": 2,
    "analyst_types": ["fundamental", "technical", "sentiment", "news"],
    
    # Trading Configuration
    "max_position_size": 0.1,  # 10% of portfolio
    "risk_threshold": 0.85,
}

def validate_config(config: dict) -> bool:
    """Validate configuration before use."""
    required = {"llm_provider", "deep_think_llm", "quick_think_llm"}
    if not required.issubset(config.keys()):
        raise InvalidConfigError(f"Missing required config keys")
    
    if config["llm_provider"] not in SUPPORTED_PROVIDERS:
        raise InvalidConfigError(
            f"Unsupported LLM provider: {config['llm_provider']}\n"
            f"Supported: {SUPPORTED_PROVIDERS}"
        )
    
    return True
```

## 6. Testing Standards

### Test Organization
```
tests/
├── agents/
│   ├── test_analyst.py
│   ├── test_trader.py
│   └── test_risk_manager.py
├── graph/
│   └── test_trading_graph.py
├── config/
│   └── test_config.py
└── integration/
    ├── test_full_workflow.py
    └── test_multi_agent_debate.py
```

### Test Coverage Requirements

| Category | Requirement |
|----------|-------------|
| Core logic | >90% coverage |
| Agents | >85% coverage |
| Integration | >80% coverage |
| Utilities | >80% coverage |
| **Total** | **>80% coverage** |

### Unit Test Pattern
```python
import pytest
from unittest.mock import Mock, patch
from tradingagents.agents import Agent

class TestAgentBase:
    @pytest.fixture
    def mock_llm(self):
        """Provide mock LLM for testing."""
        llm = Mock()
        llm.predict.return_value = "Mock response"
        return llm
    
    @pytest.fixture
    def agent(self, mock_llm):
        """Create agent instance for testing."""
        return Agent(name="Test", llm=mock_llm)
    
    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "Test"
        assert agent.llm is not None
    
    def test_error_handling(self, agent):
        """Test error handling for invalid input."""
        with pytest.raises(ValueError):
            agent.analyze(None)
```

### Integration Test Pattern
```python
class TestTradingGraph:
    @pytest.fixture
    def graph(self):
        """Create trading graph for integration testing."""
        from tradingagents.graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "mock"  # Use mock for testing
        return TradingAgentsGraph(debug=True, config=config)
    
    def test_full_trading_cycle(self, graph):
        """Test complete trading analysis workflow."""
        summary, decision = graph.propagate("TEST", "2026-01-15")
        
        assert isinstance(summary, str)
        assert isinstance(decision, dict)
        assert "action" in decision
        assert decision["action"] in ["buy", "sell", "hold"]
```

## 7. Phase Completion Verification and Checkpointing Protocol

After completing each major phase, verify progress and document:

### Phase Completion Checklist
- [ ] **Code**: All changes committed and pushed
- [ ] **Tests**: >80% coverage achieved
- [ ] **Documentation**: All docstrings, comments, and README updated
- [ ] **Quality**: Code formatted, no linting issues
- [ ] **Functionality**: Feature works as specified in `spec.md`

### Checkpointing
1. **Create test report**: Run full test suite and document coverage
   ```bash
   pytest --cov=tradingagents --cov-report=html tests/
   ```

2. **Review against spec**: Verify all acceptance criteria met
3. **Document limitations**: Note any known issues or future work
4. **Prepare for next phase**: Identify dependencies for next phase

## 8. Documentation Standards

### README Updates
- Update when user-facing functionality changes
- Include examples of new features
- Document any new CLI commands or Python API

### Docstring Requirements
- **All public functions**: Google-style docstrings
- **Module-level**: Brief description of module purpose
- **Classes**: Description of class purpose and key methods
- **Complex logic**: Explain non-obvious algorithms

### Code Comments
- Explain **why**, not what
- Reference research papers or external resources
- Mark TODOs with issue references

```python
def calculate_rsi(prices: list[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI is a momentum oscillator that measures speed/change of price movements.
    Values above 70 indicate overbought conditions; below 30 indicate oversold.
    
    Args:
        prices: Historical closing prices
        period: Number of periods for RSI calculation (default: 14)
    
    Returns:
        RSI value between 0 and 100
    
    References:
        - J. Welles Wilder Jr. "New Concepts in Technical Trading Systems"
    """
    # Implementation
```

## 9. Development Environment

### Local Setup
```bash
# Clone repository
git clone <repo>
cd tradingagents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Required Tools
- **Python**: 3.10 or later
- **pytest**: Testing framework
- **pytest-cov**: Coverage measurement
- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking (optional)

## 10. Release & Versioning

### Version Numbering
- Format: `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

### Release Checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG
- [ ] All tests passing
- [ ] Coverage >80%
- [ ] Documentation updated
- [ ] Tag commit: `git tag v0.2.0`
- [ ] Create release notes

## 11. Continuous Integration

### GitHub Actions / CI Requirements
- **Tests**: Must pass all tests on push/PR
- **Coverage**: Coverage report generated (must be >80%)
- **Linting**: Code must be formatted with Black
- **Type Check**: Python type hints validated
- **Security**: Dependency vulnerability scanning

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Configure (create .pre-commit-config.yaml)
# Runs before each commit:
# - Black formatter
# - isort for imports
# - Basic linting
```
