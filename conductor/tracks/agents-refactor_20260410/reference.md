# Reference Files & Patterns

This document lists all reference files and patterns that should be studied before implementation.

## 1. Fundamental Analyst Pattern

**Local Path:**
```
/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/financial_agents/financial_analyst.py
```

**What to Study:**
- `_compute_indicators()` method implementation
- How indicators are extracted from financial data
- How indicators are computed from existing data
- Distinction between extracted vs computed indicators
- Class structure and method patterns

**Why Important:**
This is the primary reference for implementing the enhanced Fundamental Analyst in this track. The implementation should follow the same patterns for computing financial indicators.

---

## 2. Material Facts / News Extraction Pattern

**GitHub Reference:**
```
https://github.com/AIDA-BR/workflow-vs-agent-fundamentals-br/blob/feat/manager-results/src/tools/material_facts.py
```

**What to Study:**
- How material facts are retrieved from CVM/news sources
- Data extraction and validation patterns
- News data structuring approach
- Integration with agent workflows

**Why Important:**
This reference shows how to implement news analyst data retrieval using material facts and relevant market news for the Brazilian market.

---

## 3. Price Data Parsing Pattern

**Local Path:**
```
/Users/thiagocastroferreira/Desktop/kubernetes/mcp-tutorial/scripts/parse_prices.ipynb
```

**What to Study:**
- How finbr library is used to fetch market prices
- Opening and closing price extraction
- Data parsing and structuring
- Handling edge cases (missing data, gaps, etc.)

**Why Important:**
This notebook demonstrates the exact pattern for fetching stock prices using finbr library, which is essential for implementing the Technical/Market Analyst enhancement.

---

## 4. Important Implementation Notes

### LLM Prompts
⚠️ **DO NOT MODIFY LLM PROMPTS IN THIS PHASE**

The prompts should remain unchanged. However, as you implement the new data sources and computations, you should:
1. Document what information is now available
2. Track what prompts might need updates
3. Generate `llm_proposal.md` with recommendations

This report will be used in a follow-up track for prompt optimization.

### Code Style & Integration
- Adapt reference patterns to TradingAgents architecture (LangGraph, async agents)
- Maintain consistency with existing code style
- Follow the TDD approach defined in workflow.md
- All implementations must have >80% test coverage

---

## 5. Reference File Access Checklist

Before starting implementation, verify access to all reference files:

- [ ] Can read `/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/financial_agents/financial_analyst.py`
- [ ] Can access GitHub: https://github.com/AIDA-BR/workflow-vs-agent-fundamentals-br/blob/feat/manager-results/src/tools/material_facts.py
- [ ] Can read `/Users/thiagocastroferreira/Desktop/kubernetes/mcp-tutorial/scripts/parse_prices.ipynb`
- [ ] Current TradingAgents agent implementations are understood
- [ ] LangGraph integration patterns are reviewed
