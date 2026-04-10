# Specification: Agent Data Sources & Indicator Computation Refactoring

## Overview
Refactor the TradingAgents analyst suite to align with Brazilian market data availability and improve indicator computation accuracy. This involves disabling the sentiment analyst, enhancing data sourcing for news and technical indicators, and standardizing fundamental indicator extraction and computation.

## Functional Requirements

### 1. Disable Social Media Analyst
- Remove or disable the Sentiment Analyst (Analista de Redes Sociais)
- Justification: No social media data available for the 5 target stocks in the Brazilian market
- Ensure trader and portfolio manager do not depend on sentiment data

### 2. Enhance News Analyst
- Implement news data retrieval using pattern from reference: `workflow-vs-agent-fundamentals-br/src/tools/material_facts.py`
- Extract relevant material facts and news for each analyzed stock
- Integrate news sources appropriate for Brazilian market (CVM disclosures, news agencies)
- Provide structured news data to the analyst for analysis

### 3. Improve Market/Technical Analyst
- Implement price data retrieval using `finbr` library (Brazilian market data source)
- Fetch opening and closing prices (similar to pattern in `mcp-tutorial/scripts/parse_prices.ipynb`)
- Calculate technical indicators (MACD, RSI, etc.) based on actual price data
- Ensure technical analysis is computed rather than assumed

### 4. Enhance Fundamental Analyst
- Follow indicator extraction pattern from `workflow-vs-agent-fundamentals-br/src/financial_agents/financial_analyst.py`
- Implement `_compute_indicators()` method for computed indicators
- Distinguish between extracted and computed financial indicators
- Ensure all required indicators are available for analysis

### 5. Generate LLM Proposal Report
- Create `llm_proposal.md` documenting required LLM prompt changes
- Identify which prompts need updates based on new data availability
- Provide recommendations but do not implement prompt changes yet

## Non-Functional Requirements
- No changes to LLM prompts in this phase (prompts unchanged, proposals documented)
- Maintain backward compatibility with existing agent interfaces
- Code coverage >80% for new/modified code
- All tests passing before PR creation

## Acceptance Criteria
- [ ] Sentiment Analyst is disabled and removed from agent flow
- [ ] News Analyst retrieves and structures material facts/news data
- [ ] Market Analyst uses finbr library and computes technical indicators
- [ ] Fundamental Analyst extracts and computes all indicators
- [ ] All tests pass with >80% coverage
- [ ] llm_proposal.md generated with recommendations
- [ ] Changes committed and PR created

## Out of Scope
- LLM prompt modifications (to be done in follow-up track)
- New analyst agent types
- Changes to portfolio management logic
- Integration with real-time trading (backtesting focus)
