from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.local_sqlite import get_local_fundamentals
# !!
# alteração aqui: vamos sequestrar TODAS as funções que o analista pode tentar chamar
# e forçar todas a retornarem o nosso balanço padronizado do cvm.db

@tool
def get_fundamentals(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
) -> str:
    """Retrieve comprehensive fundamental data from local CVM database."""
    return get_local_fundamentals(ticker, curr_date)

@tool
def get_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "reporting frequency: annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """Retrieve balance sheet data from local CVM database."""
    return get_local_fundamentals(ticker, curr_date)

@tool
def get_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "reporting frequency: annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """Retrieve cash flow statement data from local CVM database."""
    return get_local_fundamentals(ticker, curr_date)

@tool
def get_income_statement(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "reporting frequency: annual/quarterly"] = "quarterly",
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"] = None,
) -> str:
    """Retrieve income statement data from local CVM database."""
    return get_local_fundamentals(ticker, curr_date)