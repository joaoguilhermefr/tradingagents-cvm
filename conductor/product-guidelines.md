# Product Guidelines: TradingAgents

## 1. Writing & Communication Style

### Prose Style
- Use **clear, precise language** that balances technical accuracy with accessibility
- Target audience: researchers, ML engineers, and quantitative traders
- Avoid marketing jargon; focus on technical merit and research value
- Use active voice and concrete examples

### Documentation Standards
- Every feature must have:
  - Clear description of purpose
  - Code examples showing typical usage
  - Configuration options explained
  - Known limitations and caveats
- README remains the primary entry point; technical details in module docstrings

## 2. Code Style & Architecture

### Python Standards
- Follow PEP 8 with pragmatic exceptions for readability
- Use type hints throughout (Python 3.10+ native unions)
- Docstrings: Google-style, include parameter descriptions and return types
- Max line length: 88 characters (Black formatter standard)

### Modularity & Extensibility
- Agent roles are modular; new agents should follow established patterns
- Configuration-driven behavior (config files, not hardcoded magic numbers)
- Support multiple LLM providers without runtime dependencies on all
- Use dependency injection for flexibility in testing and configuration

### Error Handling
- Provide informative error messages with suggestions for resolution
- Log configuration details on startup for debugging
- Fail fast with clear stack traces rather than silent errors

## 3. Feature & API Design

### Principles
- **Flexibility First**: Support multiple LLM providers, debate configurations, and data sources
- **Transparency**: Users should understand what agents are reasoning about
- **Reproducibility**: Results should be deterministic given fixed seeds and models
- **Gradual Complexity**: Simple cases (CLI) work out of box; advanced cases (custom agents) require deeper understanding

### Configuration
- Configuration lives in Python dicts (not YAML/JSON) for code-as-config approach
- Defaults should work for 80% of use cases
- Configuration should be documented with examples

## 4. Community & Governance

### Open Source Values
- Prioritize research utility over commercial viability
- Welcome contributions; provide clear contribution guidelines
- Maintain active community engagement (Discord, GitHub discussions)
- Credit contributors and cite related research

### Version Compatibility
- Maintain backward compatibility within minor versions
- Document breaking changes clearly in release notes
- Support multiple Python versions (3.10+)

## 5. Quality Standards

### Testing
- Unit tests for agent logic and configuration handling
- Integration tests for multi-agent interactions
- Backtesting validation against historical data
- Mock LLM responses for deterministic testing

### Performance
- Document expected runtime for typical scenarios
- Identify performance bottlenecks and optimization opportunities
- Support async operations for I/O-bound tasks (API calls)

### Security
- Treat API keys securely (environment variables, not in code)
- Validate input data (market data, configurations)
- Document limitations of research framework (not for production use without auditing)
