# Product Guide: TradingAgents

## Initial Concept
TradingAgents is a multi-agent LLM financial trading framework designed for research purposes. It mirrors the dynamics of real-world trading firms by deploying specialized LLM-powered agents that collaboratively evaluate market conditions and inform trading decisions.

## Product Vision
Empower financial researchers, quantitative traders, and AI practitioners to experiment with multi-agent AI systems for financial markets. The framework enables exploration of how diverse specialized agents with different analytical perspectives can collectively make better trading decisions than individual models.

## Core Problem
Traditional quantitative trading relies on single-perspective algorithms or human discretion. TradingAgents addresses the need for:
- Integrating multiple analytical viewpoints (fundamental, technical, sentiment, news-based)
- Enabling dynamic discussion and debate among agents to reach consensus
- Supporting multi-LLM configurations for flexible experimentation
- Providing both research (backtesting) and real-time (CLI) trading environments

## Key Capabilities

### Analyst Team
- **Fundamentals Analyst**: Evaluates company financials and performance metrics
- **Sentiment Analyst**: Analyzes social media and public sentiment for market mood
- **News Analyst**: Monitors global news and macroeconomic indicators
- **Technical Analyst**: Detects trading patterns using indicators (MACD, RSI, etc.)

### Research Team
- Bullish and bearish researchers who critically assess analyst insights
- Structured debate mechanism to balance gains against risks

### Trading & Risk Management
- **Trader Agent**: Composes analyst reports into trading decisions
- **Risk Management**: Evaluates portfolio risk and adjusts strategies
- **Portfolio Manager**: Approves/rejects trades based on risk assessment

## Target Users
- Financial researchers exploring multi-agent AI architectures
- Quantitative traders experimenting with novel decision-making approaches
- AI/ML practitioners building financial applications
- Academic institutions studying agent-based modeling in finance

## Deployment Modes
1. **Python Package**: Import and use TradingAgents programmatically
2. **CLI Interface**: Interactive terminal UI for real-time trading simulation
3. **Backtesting**: Evaluate strategies against historical market data
4. **Multi-LLM Support**: Configure OpenAI, Google, Anthropic, xAI, OpenRouter, or local Ollama models

## Success Metrics
- Framework usability and extensibility for researchers
- Support for diverse LLM providers and configurations
- Backtesting accuracy and performance
- Community engagement and contributions
