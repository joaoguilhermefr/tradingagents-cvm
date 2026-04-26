# LLM Proposal Report: Agent Data Sources & Indicator Computation Refactoring

**Status:** Completed during Phase 5: Documentation & Analysis  
**Date:** 2026-04-10  
**Refactoring Track:** agents-refactor_20260410

---

## Executive Summary

This refactoring improves the TradingAgents analyst suite by aligning data sources with Brazilian market availability and implementing explicit indicator computation. The sentiment analyst has been disabled due to lack of social media data, while news, technical, and fundamental analysts now have enhanced data sourcing and computation capabilities.

**Key Changes:**
- Disabled sentiment analyst (no social media data for target stocks)
- Implemented `_compute_indicators()` for Fundamental Analyst
- Implemented `_compute_technical_indicators()` for Market Analyst
- Enhanced News Analyst data sourcing patterns
- Generated specific recommendations for LLM prompt updates

---

## 1. Sentiment Analyst Removal Impact

### Changes Implemented
- **Removed** sentiment analyst from default `selected_analysts` in TradingAgentsGraph
- **Removed** sentiment analyst node from GraphSetup
- **Made** `sentiment_report` field optional in AgentState (can be None)
- **Commented** out `create_social_media_analyst` import for future re-enablement

### Data Loss
The system no longer receives:
- Social media sentiment analysis
- Public opinion indicators
- Social media discussion patterns
- Sentiment score trends

### LLM Prompt Updates REQUIRED

#### 1.1 Trader Agent Prompt
**Current Dependency:** May reference sentiment reports for decision-making  
**Required Change:** Remove or downgrade sentiment analysis in decision framework

```
REMOVE:
"Consider social media sentiment signals which indicate public opinion..."
"Strong positive sentiment suggests..."
"Negative sentiment trends warn of..."

REPLACE WITH:
"Rely on fundamental analysis, news context, and technical indicators for trading decisions."
"Note: Social media sentiment data is not available for this market."
```

**Rationale:** Trader needs clear guidance that sentiment signals are no longer available. This prevents the LLM from hallucinating or expecting sentiment data.

#### 1.2 Portfolio Manager Prompt
**Current Dependency:** May use sentiment for risk assessment  
**Required Change:** Remove sentiment from risk decision factors

```
REMOVE:
"If sentiment deteriorates significantly, reduce position size..."
"Monitor social media discussion for emerging risks..."

REPLACE WITH:
"Assess risk based on technical confirmation and fundamental deterioration.
Focus on hard data (price trends, financial metrics) rather than sentiment."
```

**Rationale:** Risk management decisions should be based on observable market data and financial metrics, not sentiment which is now unavailable.

#### 1.3 Research Manager Prompt
**Current Dependency:** May coordinate sentiment analyst contributions  
**Required Change:** Remove sentiment from analyst coordination

```
REMOVE:
"Coordinate between market, sentiment, news, and fundamental analysts..."
"Reconcile conflicting signals between sentiment and technical analysis..."

REPLACE WITH:
"Coordinate between market, news, and fundamental analysts...
Reconcile conflicting signals using technical and fundamental confirmation."
```

**Rationale:** Simplifies analyst coordination to use only available data sources.

---

## 2. News Analyst Enhancement Impact

### Changes Implemented
- **Pattern Source:** `/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/tools/material_facts.py`
- **Enhancement:** News analyst can now retrieve and structure material facts
- **Focus:** CVM disclosures, Brazilian market news agencies, relevant macroeconomic news

### Data Now Available
The system can now retrieve:
- CVM material facts (official disclosures)
- Company-specific news from Brazilian news agencies
- Structured news metadata (date, source, relevance)
- News summary and key facts
- Macroeconomic indicators relevant to markets
- Global news affecting Brazilian equities

### LLM Prompt Updates REQUIRED

#### 2.1 News Analyst Prompt
**Current Capability:** Uses `get_news()` and `get_global_news()` tools  
**Required Change:** Add guidance on material facts vs general news

```
ADD TO SYSTEM MESSAGE:
"You now have access to CVM material facts (official company disclosures) 
which represent formally announced information. Prioritize these over speculation.

Material Facts Structure:
- Official CVM announcements about corporate actions
- Material business developments
- Financial results announcements
- Corporate governance changes

Analyze both material facts and broader market news to provide context."
```

**Rationale:** LLM needs to understand the distinction between formal CVM disclosures (high reliability) and general news (medium reliability) to properly weight information.

#### 2.2 Trader Agent Prompt
**Current Dependency:** May expect sentiment signals for news interpretation  
**Required Change:** Add guidance on news-based decision-making

```
ADD SECTION:
"News-Based Signals:
- Material Facts: Official corporate announcements (high confidence)
- Company News: Company-specific developments from credible sources
- Market News: Macroeconomic and industry-wide information
- Global Context: International events affecting Brazilian markets

Weight material facts heavily in decision-making.
Use news as context modifier for technical/fundamental signals."
```

**Rationale:** Without sentiment data, news becomes more important for understanding market context. LLM should understand relative reliability of different news sources.

---

## 3. Market/Technical Analyst Enhancement Impact

### Changes Implemented
- **Pattern Source:** `/Users/thiagocastroferreira/Desktop/kubernetes/mcp-tutorial/scripts/parse_prices.ipynb`
- **Enhancement:** Technical indicators computed from actual price data via `_compute_technical_indicators()`
- **Data Source:** finbr library for Brazilian stock prices (opening/closing)
- **Indicators Computed:**
  - **Moving Averages:** SMA-50, SMA-200 (trend identification)
  - **Momentum:** RSI-14 (overbought/oversold conditions)
  - **MACD:** MACD line, signal line, histogram (trend changes and momentum)

### Data Now Available
The system now computes:
- Actual technical indicators from real price data
- Trend direction via moving average crossovers
- Momentum extremes via RSI
- Divergence signals via MACD
- Price momentum strength via MACD histogram
- Golden/death cross formations (50/200 MA)

### LLM Prompt Updates REQUIRED

#### 3.1 Market Analyst Prompt
**Current State:** Uses generic indicator descriptions  
**Required Change:** Provide specific computed indicator values and interpretation

```
REPLACE GENERIC SECTION with:
"The following technical indicators are COMPUTED from actual price data:

SMA-50 & SMA-200:
- If close > SMA-200: Long-term uptrend
- If close < SMA-200: Long-term downtrend
- If SMA-50 > SMA-200: Medium-term uptrend (bullish crossover)
- If SMA-50 < SMA-200: Medium-term downtrend (bearish crossover)

RSI (14-period):
- Above 70: Overbought (potential reversal down)
- Below 30: Oversold (potential reversal up)
- 40-60: Neutral zone
- Rising RSI: Increasing momentum
- Falling RSI: Decreasing momentum

MACD:
- MACD > Signal: Bullish momentum (uptrend likely)
- MACD < Signal: Bearish momentum (downtrend likely)
- Histogram increasing: Momentum strengthening
- Histogram decreasing: Momentum weakening"
```

**Rationale:** Specific indicator values help LLM provide more accurate analysis. Generic descriptions can lead to hallucination of indicator values.

#### 3.2 Trader Agent Prompt
**Current Dependency:** May not clearly understand indicator reliability  
**Required Change:** Add guidance on technical confirmation requirements

```
ADD SECTION:
"Technical Confirmation Criteria:
- Weak signal: Single indicator aligned
- Moderate signal: Two indicators aligned
- Strong signal: RSI + MACD + MA crossover all aligned
- Confirmation rule: Wait for technical confirmation before major moves
  
Entry Signals:
- Oversold (RSI<30) + Bullish MACD = Potential buy
- Overbought (RSI>70) + Bearish MACD = Potential sell
- Golden Cross (SMA-50 > SMA-200) = Uptrend confirmation"
```

**Rationale:** Clear signal interpretation rules improve decision consistency and reduce hallucination of indicator meanings.

---

## 4. Fundamental Analyst Enhancement Impact

### Changes Implemented
- **Pattern Source:** `/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/financial_agents/financial_analyst.py`
- **Enhancement:** Implemented `_compute_indicators()` method
- **Distinction:** Clear separation between extracted and computed indicators

### Data Now Available
**Extracted Indicators** (from financial statements):
- Revenue (total sales)
- Net Income (profit)
- Total Assets
- Total Liabilities
- Operating Cash Flow
- Free Cash Flow

**Computed Indicators** (derived from above):
- **Debt-to-Equity Ratio** = Total Liabilities / Equity
  - Indicates financial leverage and capital structure
  - Higher = More debt funding
  
- **ROE (Return on Equity)** = Net Income / Equity
  - Measures how effectively company generates profits from shareholder capital
  - Higher is better (>15% considered strong)
  
- **ROA (Return on Assets)** = Net Income / Total Assets
  - Measures how effectively company uses assets to generate profits
  - Indicates operational efficiency
  
- **Debt Ratio** = Total Liabilities / Total Assets
  - Percentage of assets financed by debt
  - Higher = More financial risk

### LLM Prompt Updates REQUIRED

#### 4.1 Fundamental Analyst Prompt
**Current State:** Generic financial analysis  
**Required Change:** Add explicit guidance on indicator interpretation

```
ADD SECTION:
"Fundamental Indicators You Have Access To:

Extracted Metrics (from financial statements):
- Revenue: Company total sales
- Net Income: Bottom-line profit
- Assets: Company resources
- Liabilities: Company obligations
- Cash Flows: Actual cash generation

Computed Ratios (derived metrics):
- Debt-to-Equity: Financial leverage indicator
  * <1.0: Conservative leverage
  * 1.0-2.0: Moderate leverage
  * >2.0: High leverage/risk
  
- ROE: Profitability for shareholders
  * >15%: Strong
  * 10-15%: Adequate
  * <10%: Weak
  
- ROA: Operational efficiency
  * >5%: Efficient
  * 2-5%: Average
  * <2%: Inefficient
  
- Debt Ratio: Financial risk indicator
  * <30%: Conservative
  * 30-60%: Moderate
  * >60%: Aggressive

Always provide context on why these metrics matter for the company's financial health."
```

**Rationale:** Specific indicator thresholds and interpretations guide LLM analysis and reduce generic comments.

#### 4.2 Trader Agent Prompt
**Current Dependency:** May use fundamental signals vaguely  
**Required Change:** Add guidance on fundamental signal strength

```
ADD SECTION:
"Fundamental Signal Strength:

Strong Fundamental Buy Signal:
- High ROE (>15%) + Low Debt-to-Equity (<1.0)
- Increasing revenue + Positive net income
- Strong cash flows
- Low debt ratio (<40%)

Strong Fundamental Sell Signal:
- Declining ROE + Rising Debt-to-Equity
- Revenue/profit deterioration
- Negative cash flows
- High debt ratio (>60%)

Combine with technical signals for trading decisions."
```

**Rationale:** Provides clear fundamental buy/sell criteria for trader decision-making.

#### 4.3 Research Manager Prompt
**Current Dependency:** May not distinguish extracted vs computed data  
**Required Change:** Add guidance on data reliability hierarchy

```
ADD SECTION:
"Data Reliability Hierarchy:

Tier 1 (Highest Reliability):
- Extracted financial data from official statements
- Hard accounting numbers (revenue, assets, liabilities)

Tier 2 (Medium Reliability):
- Computed financial ratios (derived from Tier 1 data)
- Industry average comparisons

Tier 3 (Lower Reliability):
- Growth projections
- Analyst estimates
- Forward-looking statements

When conflicting signals appear:
- Trust Tier 1 data (extracted numbers)
- Explain Tier 2 computed ratios using Tier 1 data
- Use Tier 3 only for context"
```

**Rationale:** Helps LLM understand data quality hierarchy and make more reliable decisions.

---

## 5. Cross-Analyst Signal Alignment

### New Capabilities Enabled
With enhanced data sources, the system can now:
1. **Fundamental-Technical Alignment:** Check if fundamentals support technical trends
2. **News-Technical Confirmation:** Verify news events align with technical signals
3. **News-Fundamental Consistency:** Ensure news matches financial reality
4. **Risk Consensus:** Multiple perspectives on company risk

### LLM Prompt Updates RECOMMENDED

#### 5.1 Trader Agent Prompt
**Required Change:** Add signal alignment guidance

```
ADD SECTION:
"Signal Alignment Analysis:

HIGH CONFIDENCE TRADING SIGNALS:
✓ Technical uptrend + Positive news + Strong fundamentals = BUY
✓ Technical downtrend + Negative news + Weak fundamentals = SELL
✓ Strong fundamentals + Bullish technical = Medium-term BUY

CAUTION SIGNALS:
⚠ Strong technical uptrend + Weakening fundamentals = Watch for reversal
⚠ Positive news + Deteriorating technicals = Short-term noise, watch for reversal
⚠ Weak fundamentals + Bullish technicals = Potential pump and dump risk

CONFLICTING SIGNALS RESOLUTION:
- If technical and fundamental disagree, trust fundamentals for medium-term
- If news contradicts technical, investigate root cause
- Use consensus (2+ signals aligned) for medium-term trades
- Use single strong signals only for short-term tactical trades"
```

**Rationale:** Provides decision framework when analyst signals conflict.

---

## 6. Overall Improvements Summary

### Before Refactoring
- **Sentiment Analyst:** Proposed social media analysis (no data source)
- **Market Analyst:** Used generic indicator framework
- **News Analyst:** Basic news retrieval
- **Fundamentals:** Direct financial statement analysis
- **Signal Reliability:** Unclear data quality hierarchy

### After Refactoring
- **Sentiment Analyst:** DISABLED (data unavailable)
- **Market Analyst:** Computes MACD, RSI, SMA from actual price data
- **News Analyst:** Retrieves structured CVM material facts
- **Fundamentals:** Computes debt-to-equity, ROE, ROA ratios
- **Signal Reliability:** Clear hierarchy and data sources documented

### Expected Improvements
1. **Decision Quality:** More grounded in actual market data vs speculation
2. **Consistency:** Explicit indicator calculations vs parameter tuning
3. **Transparency:** Clear data sources and computation methods
4. **Reliability:** Brazilian-specific data sources (finbr, CVM)
5. **Risk Management:** Better fundamental-technical signal alignment

---

## 7. Implementation Notes

### What Was NOT Changed
- **LLM Prompts:** Prompts remain UNCHANGED (per specification)
- **Agent Architecture:** No changes to agent types or roles
- **Trading Logic:** No changes to portfolio management
- **Risk Framework:** Risk assessment remains the same

### What Should Be Changed (Recommendations Only)
All recommendations above are for a follow-up track focused on prompt optimization.

### Phased Implementation Strategy for Follow-up Track
1. **Phase 1:** Update Market Analyst prompt with computed indicator guidance
2. **Phase 2:** Update Fundamental Analyst prompt with ratio interpretation
3. **Phase 3:** Update Trader Agent prompt with signal alignment rules
4. **Phase 4:** Test and validate improved decision quality
5. **Phase 5:** Document results and learned patterns

---

## 8. Appendix: Technical Details

### Fundamental Analyst `_compute_indicators()` Function
Located in: `tradingagents/agents/analysts/fundamentals_analyst.py`

Computes:
```
- debt_to_equity = total_liabilities / equity
- roe = net_income / equity
- roa = net_income / total_assets
- debt_ratio = total_liabilities / total_assets
```

Error handling: Returns empty dict if insufficient data

### Market Analyst `_compute_technical_indicators()` Function
Located in: `tradingagents/agents/analysts/market_analyst.py`

Computes:
```
- sma_50, sma_200 (if sufficient data)
- rsi (14-period)
- macd, macd_signal, macd_histogram (if sufficient data)
```

Error handling: Returns available indicators, skips ones requiring insufficient data

### News Analyst Enhancement Pattern
Source: `/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/src/tools/material_facts.py`

Provides structured access to:
- CVM official disclosures
- Material corporate events
- Relevant market news
- Metadata (date, source, relevance)

---

## 9. Conclusion

This refactoring significantly improves the TradingAgents framework by:
1. Aligning data sources with actual market availability
2. Implementing explicit indicator computation from real data
3. Removing non-functional sentiment analysis
4. Creating clear guidelines for LLM prompt enhancement

The recommendations in this document should guide the next phase of LLM prompt optimization to fully leverage the improved data sources and analytical capabilities.

**Next Steps:** Create follow-up track "LLM Prompt Optimization for Enhanced Data Sources" to implement these recommendations.
