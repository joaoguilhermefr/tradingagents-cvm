from langchain_core.tools import tool
from typing import Annotated

@tool
def get_news(
    ticker: Annotated[str, "Ticker symbol"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve news data for a given ticker symbol."""
    return f"Nenhuma notícia específica disponível para {ticker} nesta simulação de backtest. O analista deve basear a sua decisão estritamente nos relatórios fundamentais (DFP/ITR) e técnicos."

@tool
def get_global_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    limit: Annotated[int, "Maximum number of articles to return"] = 5,
) -> str:
    """Retrieve global news data."""
    return "Nenhuma notícia macroeconômica global disponível nesta simulação. Foque a sua análise apenas nos dados numéricos fornecidos."

@tool
def get_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
) -> str:
    """Retrieve insider transaction information about a company."""
    return f"Nenhum dado de transação interna (insider) disponível para {ticker}."