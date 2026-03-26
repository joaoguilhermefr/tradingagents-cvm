from langchain_core.tools import tool
from typing import Annotated
from datetime import datetime, timedelta
from tradingagents.dataflows.local_sqlite import get_local_prices

@tool
def get_indicators(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[str, "The current trading date you are trading on, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"] = 30,
) -> str:
    """Fetches historical price data for a Brazilian company from the local prices database."""
    try:
        # Calcula a data de início com base no look_back_days que o agente pedir
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=look_back_days)
        start_date_str = start_dt.strftime("%Y-%m-%d")
        # !! 
        # ignoramos a internet e chamamos a nossa função local
        return get_local_prices(symbol, start_date_str, curr_date)
    except Exception as e:
        return f"Error fetching local technical indicators for {symbol}: {str(e)}"