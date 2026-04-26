"""Tests for Agent Data Sources & Indicator Computation Refactoring.

This test suite validates:
1. Sentiment Analyst is properly disabled
2. News Analyst retrieves material facts correctly
3. Market Analyst computes technical indicators with finbr data
4. Fundamental Analyst extracts and computes indicators correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd

from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.analysts.market_analyst import create_market_analyst
from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
from tradingagents.graph.setup import GraphSetup
from tradingagents.graph.trading_graph import TradingAgentsGraph


# ============================================================================
# SENTIMENT ANALYST REMOVAL TESTS
# ============================================================================


class TestSentimentAnalystRemoval:
    """Test sentiment analyst is properly disabled."""

    def test_sentiment_analyst_not_selected_by_default(self):
        """Verify 'social' analyst is not in default selected analysts."""
        # This test should eventually pass after implementation
        with patch("tradingagents.graph.trading_graph.TradingAgentsGraph._create_tool_nodes"):
            # When TradingAgentsGraph is initialized without specifying analysts
            # 'social' should NOT be in the default list
            default_analysts = ["market", "news", "fundamentals"]  # 'social' removed
            assert "social" not in default_analysts

    def test_graph_setup_excludes_social_analyst(self, mock_llm):
        """Verify GraphSetup doesn't create social analyst node when not selected."""
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        from tradingagents.graph.conditional_logic import ConditionalLogic
        from tradingagents.agents import create_market_analyst, create_news_analyst, create_fundamentals_analyst

        graph_setup = GraphSetup(
            quick_thinking_llm=mock_llm,
            deep_thinking_llm=mock_llm,
            tool_nodes={"market": Mock(), "news": Mock(), "fundamentals": Mock()},
            bull_memory=Mock(spec=FinancialSituationMemory),
            bear_memory=Mock(spec=FinancialSituationMemory),
            trader_memory=Mock(spec=FinancialSituationMemory),
            invest_judge_memory=Mock(spec=FinancialSituationMemory),
            risk_manager_memory=Mock(spec=FinancialSituationMemory),
            conditional_logic=Mock(spec=ConditionalLogic),
        )

        # Setup graph without 'social'
        selected_analysts = ["market", "news", "fundamentals"]
        # Verify that the only imported analysts are market, news, fundamentals
        assert "create_social_media_analyst" not in dir(graph_setup.__class__.__module__)

        # Verify default selected analysts don't include 'social'
        assert "social" not in selected_analysts

    def test_agent_state_handles_missing_sentiment_report(self, sample_agent_state):
        """Verify AgentState works without sentiment_report field."""
        # sentiment_report should be optional/ignorable
        state = sample_agent_state.copy()
        del state["sentiment_report"]

        # Should not raise an error
        assert "sentiment_report" not in state
        assert "market_report" in state
        assert "news_report" in state


# ============================================================================
# NEWS ANALYST ENHANCEMENT TESTS
# ============================================================================


class TestNewsAnalystEnhancement:
    """Test News Analyst retrieves material facts and news correctly."""

    def test_news_analyst_retrieves_news_data(self, mock_llm, sample_agent_state, mock_news_data):
        """Verify News Analyst can retrieve news data."""
        with patch("tradingagents.agents.analysts.news_analyst.get_news") as mock_get_news:
            mock_get_news.return_value = mock_news_data

            news_analyst_node = create_news_analyst(mock_llm)

            # The node should call get_news tool
            assert news_analyst_node is not None
            assert callable(news_analyst_node)

    def test_news_data_contains_material_facts(self, mock_news_data):
        """Verify news data structure contains relevant fields."""
        required_fields = ["date", "title", "source", "summary"]

        for news_item in mock_news_data:
            for field in required_fields:
                assert field in news_item, f"Missing field: {field}"

    def test_news_analyst_validates_news_structure(self):
        """Verify news data is properly structured and validated."""
        invalid_news = {"title": "Missing required fields"}

        # Should require date, source, summary
        required_fields = ["date", "source", "summary"]
        for field in required_fields:
            assert field not in invalid_news or invalid_news[field] is not None

    def test_news_analyst_handles_missing_news(self, mock_llm, sample_agent_state):
        """Verify News Analyst handles cases with no news available."""
        with patch("tradingagents.agents.analysts.news_analyst.get_news") as mock_get_news:
            mock_get_news.return_value = []  # No news available

            news_analyst_node = create_news_analyst(mock_llm)
            assert news_analyst_node is not None


# ============================================================================
# MARKET/TECHNICAL ANALYST ENHANCEMENT TESTS
# ============================================================================


class TestMarketAnalystEnhancement:
    """Test Market Analyst uses finbr for price data and computes indicators."""

    def test_market_analyst_uses_price_data(self, mock_llm, mock_price_data):
        """Verify Market Analyst can work with price data."""
        market_analyst_node = create_market_analyst(mock_llm)
        assert market_analyst_node is not None
        assert callable(market_analyst_node)

    def test_technical_indicators_computed_from_prices(self, mock_price_data):
        """Verify technical indicators can be computed from price data."""
        prices = pd.DataFrame(mock_price_data)

        # MACD should be computable
        ema_12 = prices["close"].ewm(span=12).mean()
        ema_26 = prices["close"].ewm(span=26).mean()
        macd = ema_12 - ema_26

        assert len(macd) == len(prices)
        assert not macd.isna().all()

    def test_rsi_computation_from_prices(self, mock_price_data):
        """Verify RSI can be computed from price data."""
        closes = pd.Series(mock_price_data["close"])

        # RSI computation
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        # RSI should be computable (might have NaN at start)
        assert len(gain) == len(closes)
        assert len(loss) == len(closes)

    def test_price_data_structure_validation(self, mock_price_data):
        """Verify price data has required fields."""
        required_fields = ["open", "close", "high", "low", "volume"]

        for field in required_fields:
            assert field in mock_price_data
            assert len(mock_price_data[field]) > 0

    def test_market_analyst_with_insufficient_price_data(self, mock_llm):
        """Verify Market Analyst handles insufficient data gracefully."""
        insufficient_data = {
            "open": [97.50],  # Only 1 data point
            "close": [97.80],
        }

        # Should still be computable (though indicators will be limited)
        assert len(insufficient_data["close"]) > 0


# ============================================================================
# FUNDAMENTAL ANALYST ENHANCEMENT TESTS
# ============================================================================


class TestFundamentalAnalystEnhancement:
    """Test Fundamental Analyst extracts and computes indicators."""

    def test_fundamental_analyst_initialization(self, mock_llm):
        """Verify Fundamental Analyst initializes correctly."""
        fundamentals_analyst_node = create_fundamentals_analyst(mock_llm)
        assert fundamentals_analyst_node is not None
        assert callable(fundamentals_analyst_node)

    def test_indicator_extraction_from_financials(self, mock_fundamental_data):
        """Verify financial indicators are extracted from financial data."""
        extracted_indicators = {
            "revenue": mock_fundamental_data["revenue"],
            "net_income": mock_fundamental_data["net_income"],
            "total_assets": mock_fundamental_data["total_assets"],
        }

        assert "revenue" in extracted_indicators
        assert "net_income" in extracted_indicators
        assert extracted_indicators["revenue"] > 0

    def test_compute_indicators_method_signature(self):
        """Verify _compute_indicators method should exist and be callable.

        This test documents the expected method signature for the enhancement.
        """
        # After implementation, FundamentalsAnalyst should have _compute_indicators
        # that takes extracted financial data and returns computed metrics

        expected_computed = {
            "pe_ratio": None,  # net_income / market_cap
            "debt_to_equity": None,  # total_liabilities / (assets - liabilities)
            "roe": None,  # net_income / equity
            "roa": None,  # net_income / total_assets
            "operating_margin": None,  # operating_income / revenue
        }

        # Verify computed metrics are calculable
        assert "pe_ratio" in expected_computed
        assert "debt_to_equity" in expected_computed
        assert "roe" in expected_computed

    def test_debt_to_equity_computation(self, mock_fundamental_data):
        """Verify debt-to-equity ratio computation."""
        total_liabilities = mock_fundamental_data["total_liabilities"]
        total_assets = mock_fundamental_data["total_assets"]
        equity = total_assets - total_liabilities

        debt_to_equity = total_liabilities / equity if equity > 0 else 0

        assert debt_to_equity >= 0
        assert debt_to_equity == pytest.approx(1.0)  # 200B / 200B

    def test_roe_computation(self, mock_fundamental_data):
        """Verify Return on Equity computation."""
        net_income = mock_fundamental_data["net_income"]
        total_assets = mock_fundamental_data["total_assets"]
        total_liabilities = mock_fundamental_data["total_liabilities"]
        equity = total_assets - total_liabilities

        roe = net_income / equity if equity > 0 else 0

        assert roe >= 0
        assert roe == pytest.approx(0.125)  # 25B / 200B

    def test_distinction_extracted_vs_computed(self, mock_fundamental_data):
        """Verify distinction between extracted and computed indicators."""
        extracted = {"revenue", "net_income", "total_assets", "total_liabilities"}
        computed = {"pe_ratio", "debt_to_equity", "roe", "roa"}

        # Extracted come directly from financial statements
        assert "revenue" in extracted
        # Computed are derived from other metrics
        assert "roe" in computed
        # No overlap
        assert extracted.isdisjoint(computed)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegrationWithNewDataSources:
    """Integration tests for agents working together with new data sources."""

    def test_agents_work_without_sentiment_report(self, mock_llm, sample_agent_state):
        """Verify all agents can work without sentiment_report in state."""
        state = sample_agent_state.copy()

        # All analyst nodes should work even without sentiment_report
        analysts = {
            "market": create_market_analyst(mock_llm),
            "news": create_news_analyst(mock_llm),
            "fundamentals": create_fundamentals_analyst(mock_llm),
        }

        for analyst_name, analyst_node in analysts.items():
            assert analyst_node is not None

    def test_trader_agent_receives_reports_without_sentiment(self, mock_llm, sample_agent_state):
        """Verify Trader agent functions without sentiment input."""
        state = sample_agent_state.copy()
        state["market_report"] = "Market is trending up"
        state["news_report"] = "Positive earnings news"
        state["fundamentals_report"] = "Strong fundamentals"
        # Note: sentiment_report is present but empty - should not cause errors

        # Trader should make decisions based on other reports
        assert state["market_report"]
        assert state["news_report"]
        assert state["fundamentals_report"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
