from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.local_sqlite import get_local_prices

@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve stock price data (OHLCV) from the local prices database."""
    try:
        # redirecionado para a base de dados local
        return get_local_prices(symbol, start_date, end_date)
    except Exception as e:
        return f"Error fetching local stock data for {symbol}: {str(e)}"