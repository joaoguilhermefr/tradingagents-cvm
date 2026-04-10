from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from typing import Dict
from datetime import datetime, timedelta
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_transactions
from tradingagents.dataflows.config import get_config
from tradingagents.dataflows.local_sqlite import get_local_fundamentals_dict, get_local_prices_df


def _safe_div(numerator: float, denominator: float) -> float:
    """Safely divide two numbers, returning 0.0 on zero-division."""
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def _compute_indicators(db_fields: Dict[str, float], price: float, total_shares: float = 1.0) -> Dict[str, float]:
    """Compute all financial indicators from CVM database fields.

    Computes 32+ derived financial indicators from 15 base fields fetched from
    the CVM database. This follows the pattern from workflow-vs-agent-fundamentals-br.

    Args:
        db_fields: Dictionary with 15 base CVM fields:
            - Ativo (Total Assets)
            - Disponibilidades (Cash & Equivalents)
            - Ativo Circulante (Current Assets)
            - Passivo Circulante (Current Liabilities)
            - Dív. Bruta (Gross Debt)
            - Patrim. Líq (Equity)
            - Fornecedores (Accounts Payable)
            - Receita Líquida (12 meses) (Annual Revenue)
            - Lucro Bruto (12 meses) (Annual Gross Profit)
            - EBIT (12 meses) (Annual EBIT)
            - EBITDA (12 meses) (Annual EBITDA)
            - Lucro Líquido (12 meses) (Annual Net Income)
            - Receita Líquida (3 meses) (Quarterly Revenue)
            - EBIT (3 meses) (Quarterly EBIT)
            - Lucro Líquido (3 meses) (Quarterly Net Income)
        price: Stock price in BRL
        total_shares: Number of outstanding shares (default 1.0 for safety)

    Returns:
        Dictionary of 32+ indicator names to float values
    """
    # Extract 15 base fields from CVM database
    ativo = db_fields.get("Ativo", 0.0)
    disponibilidades = db_fields.get("Disponibilidades", 0.0)
    ativo_circulante = db_fields.get("Ativo Circulante", 0.0)
    passivo_circulante = db_fields.get("Passivo Circulante", 0.0)
    divida_bruta = db_fields.get("Dív. Bruta", 0.0)
    patrimonio_liquido = db_fields.get("Patrim. Líq", 0.0)
    fornecedores = db_fields.get("Fornecedores", 0.0)
    receita_liquida_anual = db_fields.get("Receita Líquida (12 meses)", 0.0)
    lucro_bruto_anual = db_fields.get("Lucro Bruto (12 meses)", 0.0)
    ebit_anual = db_fields.get("EBIT (12 meses)", 0.0)
    ebitda_anual = db_fields.get("EBITDA (12 meses)", 0.0)
    lucro_liquido_anual = db_fields.get("Lucro Líquido (12 meses)", 0.0)
    receita_liquida_trimestre = db_fields.get("Receita Líquida (3 meses)", 0.0)
    ebit_trimestre = db_fields.get("EBIT (3 meses)", 0.0)
    lucro_liquido_trimestre = db_fields.get("Lucro Líquido (3 meses)", 0.0)

    # Compute intermediary values
    divida_liquida = divida_bruta - disponibilidades
    market_cap = price * total_shares
    passivo_total = ativo - patrimonio_liquido
    ev = market_cap + divida_liquida
    lpa = _safe_div(lucro_liquido_anual, total_shares)
    vpa = _safe_div(patrimonio_liquido, total_shares)
    capital_giro = ativo_circulante - passivo_circulante
    ativ_circ_liq = ativo_circulante - passivo_total
    roic_base = ativo - fornecedores - disponibilidades

    # Build indicators dictionary (32+ indicators)
    indicators = {
        # 15 Extracted base fields
        "Ativo": ativo,
        "Disponibilidades": disponibilidades,
        "Ativo Circulante": ativo_circulante,
        "Dív. Bruta": divida_bruta,
        "Dív. Líquida": divida_liquida,
        "Patrim. Líq": patrimonio_liquido,
        "Receita Líquida (12 meses)": receita_liquida_anual,
        "EBIT (12 meses)": ebit_anual,
        "Lucro Líquido (12 meses)": lucro_liquido_anual,
        "Receita Líquida (3 meses)": receita_liquida_trimestre,
        "EBIT (3 meses)": ebit_trimestre,
        "Lucro Líquido (3 meses)": lucro_liquido_trimestre,
        # Per-share metrics
        "LPA": lpa,
        "VPA": vpa,
        # Valuation ratios
        "P/L": _safe_div(price, lpa),
        "P/VP": _safe_div(price, vpa),
        "P/EBIT": _safe_div(market_cap, ebit_anual),
        "PSR": _safe_div(market_cap, receita_liquida_anual),
        "P/Ativos": _safe_div(market_cap, ativo),
        "P/Cap. Giro": _safe_div(market_cap, capital_giro),
        "P/Ativ Circ Liq": _safe_div(market_cap, ativ_circ_liq),
        "EV/EBITDA": _safe_div(ev, ebitda_anual),
        "EV/EBIT": _safe_div(ev, ebit_anual),
        # Profitability margins (as percentages)
        "Marg. Bruta": _safe_div(lucro_bruto_anual, receita_liquida_anual) * 100,
        "Marg. EBIT": _safe_div(ebit_anual, receita_liquida_anual) * 100,
        "Marg. Líquida": _safe_div(lucro_liquido_anual, receita_liquida_anual) * 100,
        "EBIT/Ativo": _safe_div(ebit_anual, ativo) * 100,
        # Return metrics (as percentages)
        "ROIC": _safe_div(ebit_anual, roic_base) * 100,
        "ROE": _safe_div(lucro_liquido_anual, patrimonio_liquido) * 100,
        # Liquidity & leverage metrics
        "Liquidez Corr": _safe_div(ativo_circulante, passivo_circulante),
        "Div Br/Patrim": _safe_div(divida_bruta, patrimonio_liquido),
        "Giro Ativos": _safe_div(receita_liquida_anual, ativo),
    }

    return indicators


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Pre-compute financial indicators from local data
        db_fields = get_local_fundamentals_dict(ticker, current_date)
        prices_df = get_local_prices_df(ticker, start_date="2020-01-01", end_date=current_date)

        price = 0.0
        total_shares = 1.0
        if prices_df is not None and not prices_df.empty:
            price = float(prices_df["close"].iloc[-1])

        computed_indicators = _compute_indicators(db_fields, price, total_shares) if db_fields else {}

        # Format computed indicators for inclusion in system message
        indicators_block = ""
        if computed_indicators:
            lines = "\n".join(
                f"  {k}: {v:.4f}" for k, v in sorted(computed_indicators.items())
            )
            indicators_block = f"\n\nIndicadores Financeiros Pré-Computados para {ticker}:\n{lines}"

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
            + " Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for specific financial statements."
            + indicators_block
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
