from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from typing import Dict, Any, Optional
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_transactions
from tradingagents.dataflows.config import get_config


def _compute_indicators(extracted_data: Dict[str, Any]) -> Dict[str, float]:
    """Compute financial indicators from extracted financial data.

    Computes derived metrics from primary financial statement data.
    These are calculated ratios and metrics that aren't directly extracted
    from financial statements but derived from them.

    Args:
        extracted_data: Dictionary containing extracted financial metrics:
            - revenue: Total company revenue
            - net_income: Net income/profit
            - total_assets: Total assets
            - total_liabilities: Total liabilities
            - operating_cash_flow: Operating cash flow
            - free_cash_flow: Free cash flow

    Returns:
        Dictionary of computed financial indicators:
            - debt_to_equity: Total liabilities / Equity
            - roe: Return on Equity (Net Income / Equity)
            - roa: Return on Assets (Net Income / Total Assets)
            - debt_ratio: Total Liabilities / Total Assets
            - operating_margin: Operating Income / Revenue (if available)
    """
    computed = {}

    try:
        # Calculate equity
        total_assets = extracted_data.get("total_assets", 0)
        total_liabilities = extracted_data.get("total_liabilities", 0)
        equity = total_assets - total_liabilities

        # Debt-to-Equity Ratio
        if equity > 0:
            computed["debt_to_equity"] = total_liabilities / equity

        # Return on Equity (ROE)
        net_income = extracted_data.get("net_income", 0)
        if equity > 0:
            computed["roe"] = net_income / equity

        # Return on Assets (ROA)
        if total_assets > 0:
            computed["roa"] = net_income / total_assets

        # Debt Ratio
        if total_assets > 0:
            computed["debt_ratio"] = total_liabilities / total_assets

    except (ZeroDivisionError, TypeError, KeyError) as e:
        # Log but don't fail if computation can't be done
        pass

    return computed


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "You are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, basic company financials, and company financial history to gain a full view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + " Analyze both extracted financial data (revenue, assets, liabilities) and computed indicators (debt-to-equity, ROE, ROA, debt ratio) to provide comprehensive insights."
            + " Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."
            + " Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for specific financial statements.",
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
