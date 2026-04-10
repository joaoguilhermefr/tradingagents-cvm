"""Shared pytest fixtures and configuration."""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from tradingagents.agents.utils.agent_states import AgentState


@pytest.fixture
def mock_llm():
    """Provide a mock LLM for testing."""
    llm = Mock()
    llm.bind_tools = Mock(return_value=Mock())
    return llm


@pytest.fixture
def sample_agent_state():
    """Provide a sample AgentState for testing."""
    return {
        "company_of_interest": "PETR4",
        "trade_date": "2024-01-15",
        "messages": [],
        "sender": "market",
        "market_report": "",
        "sentiment_report": "",
        "news_report": "",
        "fundamentals_report": "",
        "investment_debate_state": None,
        "investment_plan": "",
        "trader_investment_plan": "",
        "risk_debate_state": None,
        "final_trade_decision": "",
    }


@pytest.fixture
def mock_news_data():
    """Sample news data for testing."""
    return [
        {
            "date": "2024-01-15",
            "title": "PETR4 reports strong Q4 earnings",
            "source": "Reuters",
            "summary": "Petrobras reported Q4 earnings beat consensus",
        },
        {
            "date": "2024-01-14",
            "title": "Oil prices surge amid supply concerns",
            "source": "Bloomberg",
            "summary": "Brent crude rises 3% on supply disruption fears",
        },
    ]


@pytest.fixture
def mock_price_data():
    """Sample price data for finbr."""
    return {
        "open": [97.50, 97.80, 98.20, 98.10, 98.50],
        "close": [97.80, 98.20, 98.10, 98.50, 99.00],
        "high": [98.00, 98.50, 98.30, 98.70, 99.20],
        "low": [97.40, 97.70, 97.95, 98.00, 98.40],
        "volume": [45000000, 42000000, 41000000, 43000000, 44000000],
    }


@pytest.fixture
def mock_fundamental_data():
    """Sample fundamental data for testing."""
    return {
        "revenue": 1.5e11,  # 150 billion
        "net_income": 2.5e10,  # 25 billion
        "total_assets": 4.0e11,  # 400 billion
        "total_liabilities": 2.0e11,  # 200 billion
        "operating_cash_flow": 5.0e10,  # 50 billion
        "free_cash_flow": 3.5e10,  # 35 billion
    }
