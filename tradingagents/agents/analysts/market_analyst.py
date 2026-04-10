from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from typing import Dict, Any, List, Optional
import pandas as pd
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators
from tradingagents.dataflows.config import get_config


def _compute_technical_indicators(price_data: Dict[str, List[float]]) -> Dict[str, Any]:
    """Compute technical indicators from price data (OHLCV).

    Computes various technical indicators from price and volume data.
    This function serves as the foundation for technical analysis,
    computing indicators like MACD, RSI, Bollinger Bands from raw OHLCV data.

    Args:
        price_data: Dictionary with keys:
            - open: List of opening prices
            - high: List of high prices
            - low: List of low prices
            - close: List of closing prices
            - volume: List of volumes

    Returns:
        Dictionary of computed technical indicators with their values
    """
    indicators = {}

    try:
        df = pd.DataFrame(price_data)
        closes = df["close"]

        # Simple Moving Averages
        if len(closes) >= 50:
            indicators["sma_50"] = closes.rolling(window=50).mean().iloc[-1]
        if len(closes) >= 200:
            indicators["sma_200"] = closes.rolling(window=200).mean().iloc[-1]

        # RSI (Relative Strength Index)
        if len(closes) >= 14:
            delta = closes.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators["rsi"] = (100 - (100 / (1 + rs))).iloc[-1]

        # MACD
        if len(closes) >= 26:
            ema_12 = closes.ewm(span=12).mean()
            ema_26 = closes.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            indicators["macd"] = macd.iloc[-1]
            indicators["macd_signal"] = signal.iloc[-1]
            indicators["macd_histogram"] = (macd - signal).iloc[-1]

    except (KeyError, ValueError, IndexError) as e:
        # Log but don't fail if computation can't be done
        pass

    return indicators


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """You are a trading assistant tasked with analyzing financial markets using technical analysis. Your role is to analyze **computed technical indicators** derived from actual price and volume data to provide insights into market conditions and trading opportunities.

The following technical indicators are now computed from real OHLCV data:

Moving Averages (Computed):
- sma_50: 50-period Simple Moving Average for medium-term trend identification
- sma_200: 200-period Simple Moving Average for long-term trend confirmation

Momentum Indicators (Computed):
- rsi: Relative Strength Index (14-period) - Measures momentum and overbought/oversold conditions
  - Values above 70: Potentially overbought
  - Values below 30: Potentially oversold

MACD (Computed):
- macd: MACD line (difference of 12 and 26-period EMAs)
- macd_signal: Signal line (9-period EMA of MACD)
- macd_histogram: Difference between MACD and signal line

Instructions:
1. Analyze the computed indicators in the context of current market conditions
2. Identify trend direction using moving averages
3. Assess momentum using RSI and MACD
4. Look for divergences and crossovers as potential signals
5. Consider multiple indicators together for confirmation
6. Write a very detailed and nuanced report of the trends you observe. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."""
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
