# LLM Proposal Report Template

This file serves as a template for documenting LLM prompt changes needed based on the refactoring.

**Status:** To be completed during Phase 5: Documentation & Analysis

---

## Executive Summary

Document here what changes were made to agent data sources and indicator computation, and why the LLM prompts should be updated to leverage these improvements.

---

## 1. Sentiment Analyst Removal Impact

### Change Made
- Sentiment Analyst (Analista de Redes Sociais) has been disabled
- Trader and Portfolio Manager no longer receive sentiment analysis inputs

### Prompt Changes Needed
- [ ] Remove references to sentiment analysis from trader decision-making prompts
- [ ] Update risk assessment prompt to account for missing sentiment signal
- [ ] Clarify portfolio manager prompt about available decision signals

### Rationale
[Document why the prompts need changes based on missing sentiment data]

---

## 2. News Analyst Enhancement Impact

### Change Made
- News Analyst now retrieves material facts and market-relevant news
- Structured news data available in analyst reports
- Reference: `/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/tools/material_facts.py`

### Data Now Available
- Material facts from CVM
- Relevant market news
- News publication dates and sources
- News relevance to analyzed stocks

### Prompt Changes Needed
- [ ] Update news analyst prompt to leverage material facts data
- [ ] Enhance trader prompt to consider news significance
- [ ] Add news-based risk assessment to portfolio manager prompt
- [ ] Include news impact on sector analysis

### Rationale
[Document how improved news data should inform LLM decision-making]

---

## 3. Technical/Market Analyst Enhancement Impact

### Change Made
- Market Analyst now uses finbr library for real price data
- Technical indicators (MACD, RSI, etc.) computed from actual prices
- Reference: `/Users/thiagocastroferreira/Desktop/kubernetes/mcp-tutorial/scripts/parse_prices.ipynb`

### Data Now Available
- Opening and closing prices from finbr
- Computed technical indicators:
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - Other technical indicators (specify)
- Historical price trends and patterns

### Prompt Changes Needed
- [ ] Update market analyst prompt to explain technical indicators explicitly
- [ ] Add instruction for interpreting indicator signals
- [ ] Enhance trader prompt to consider technical confirmation signals
- [ ] Add technical-fundamental consensus checks to portfolio manager

### Rationale
[Document why LLMs need explicit instruction on technical indicators]

---

## 4. Fundamental Analyst Enhancement Impact

### Change Made
- Fundamental Analyst now implements `_compute_indicators()` method
- Distinction between extracted and computed financial indicators
- Reference: `/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/financial_agents/financial_analyst.py`

### Data Now Available
- **Extracted Indicators:** Direct from financial statements
  - Revenue, profit, assets, liabilities, etc.
  - List specific indicators
  
- **Computed Indicators:** Derived from extracted data
  - P/E ratio, debt-to-equity, ROE, ROA, etc.
  - List specific computed indicators

### Prompt Changes Needed
- [ ] Update fundamental analyst prompt to explain available indicators
- [ ] Add instructions for interpreting computed vs extracted metrics
- [ ] Enhance trader prompt for fundamental signal interpretation
- [ ] Add quality/reliability notes for computed indicators

### Rationale
[Document why clear indicator definitions help LLM analysis]

---

## 5. Cross-Analyst Consensus Improvements

### New Capabilities
With all data sources enhanced, the system now enables:
- News + Fundamental alignment checks
- Technical + Fundamental confirmation
- Technical + News sentiment alignment
- Risk signals across multiple perspectives

### Prompt Changes Needed
- [ ] Update trader prompt for multi-signal consensus
- [ ] Enhance portfolio manager for signal conflict resolution
- [ ] Add confidence metrics based on signal alignment
- [ ] Implement tie-breaking rules for conflicting signals

### Rationale
[Document how multi-signal consensus should improve trading decisions]

---

## 6. Overall Improvements Summary

### Before Refactoring
[List what data sources and capabilities existed]

### After Refactoring
[List all new/improved capabilities]

### Expected Improvements
[Document expected decision quality improvements]

---

## 7. Next Steps (For Follow-up Track)

This proposal should be used in a follow-up track to:
1. Update LLM prompts with recommendations above
2. Test prompt effectiveness with new data
3. Optimize prompt wording based on agent performance
4. Document final prompt changes and rationale

---

## Notes for Implementation

- Fill this document progressively during Phase 5
- Update section headers with actual data available
- Provide specific examples of improvements
- Link to new data structures and computations
- Be specific about what each LLM should know

**DO NOT MODIFY PROMPTS IN THIS TRACK** — only document recommendations.
