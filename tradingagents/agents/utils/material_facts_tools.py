"""Tools for fetching and processing CVM material facts (Fatos Relevantes).

This module provides access to Brazilian Securities Commission (CVM) material facts
announcements for companies, fetching from the B3 plantão de notícias and CVM IPE.

Pattern based on: workflow-vs-agent-fundamentals-br/src/tools/material_facts.py
"""

import os
import calendar
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from finbr.b3 import plantao_noticias
    HAS_FINBR = True
except ImportError:
    HAS_FINBR = False
    logger.warning("finbr library not installed - material facts fetching limited")


def _get_month_range(trade_date: str, lookback_days: int = 7) -> tuple[int, int, int, int]:
    """Calculate year, month range for fetching material facts.

    Args:
        trade_date: Date string in format YYYY-MM-DD
        lookback_days: Number of days to look back from trade_date

    Returns:
        Tuple of (start_year, start_month, end_year, end_month)
    """
    try:
        current = datetime.strptime(trade_date, "%Y-%m-%d")
        start = current - timedelta(days=lookback_days)
        return (start.year, start.month, current.year, current.month)
    except (ValueError, AttributeError):
        # Default to current month if date parsing fails
        now = datetime.now()
        return (now.year, now.month, now.year, now.month)


def fetch_material_facts(
    ticker: str,
    trade_date: str,
    lookback_days: int = 7,
) -> List[Dict[str, Any]]:
    """Fetch 'Fato Relevante' (material facts) announcements for a ticker.

    Retrieves official CVM material facts announcements from the B3 plantão de notícias
    for the specified ticker and date range.

    Args:
        ticker: Stock ticker (e.g., 'PETR4', 'VALE3')
        trade_date: Reference date in format YYYY-MM-DD
        lookback_days: Number of days to look back (default: 7 days)

    Returns:
        List of dicts with keys:
            - titulo: Title/subject of announcement
            - headline: Headline text
            - data_hora: Announcement date/time
            - conteudo: Full content (if available)
            - url: Link to announcement
            - fonte: Source (always 'CVM/B3')
    """
    if not HAS_FINBR:
        logger.warning("finbr not available - returning empty results")
        return []

    results = []

    try:
        # Calculate date range
        start_year, start_month, end_year, end_month = _get_month_range(trade_date, lookback_days)

        # Generate month boundaries
        inicio = f"{start_year}-{start_month:02d}-01"

        # Calculate last day of end month
        last_day = calendar.monthrange(end_year, end_month)[1]
        fim = f"{end_year}-{end_month:02d}-{last_day:02d}"

        # Fetch from B3 plantão de notícias
        try:
            noticias = plantao_noticias.get(inicio=inicio, fim=fim)
        except Exception as e:
            logger.warning(f"Failed to fetch from B3 plantão: {e}")
            return []

        if not noticias:
            return []

        # Filter for ticker and material facts
        ticker_root = ticker[:4]  # PETR4 -> PETR (covers all share classes)

        for noticia in noticias:
            # Match ticker (covers PETR4, PETR3, etc.)
            if not hasattr(noticia, 'ticker') or not noticia.ticker.startswith(ticker_root):
                continue

            # Filter for "Fato Relevante" announcements
            titulo = getattr(noticia, 'titulo', '')
            headline = getattr(noticia, 'headline', '')

            if "Fato Relevante" not in (titulo or "") and "Fato Relevante" not in (headline or ""):
                continue

            # Extract relevant fields
            result_item = {
                "ticker": noticia.ticker if hasattr(noticia, 'ticker') else ticker,
                "titulo": titulo,
                "headline": headline,
                "data_hora": getattr(noticia, 'data_hora', ''),
                "url": getattr(noticia, 'url', ''),
                "fonte": "CVM/B3",
                "conteudo": "",  # Content would require PDF parsing
            }

            # Add summary from available fields
            if hasattr(noticia, 'summary') and noticia.summary:
                result_item["conteudo"] = noticia.summary
            elif headline:
                result_item["conteudo"] = headline

            results.append(result_item)

    except Exception as e:
        logger.error(f"Error fetching material facts for {ticker}: {e}")
        return []

    return results


def fetch_recent_announcements(
    ticker: str,
    trade_date: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Fetch recent announcements for a ticker.

    Convenience wrapper for fetching recent material facts with a limit.

    Args:
        ticker: Stock ticker
        trade_date: Reference date
        limit: Maximum number of announcements to return

    Returns:
        List of material facts announcements (limited to 'limit' items)
    """
    material_facts = fetch_material_facts(ticker, trade_date, lookback_days=30)
    return material_facts[:limit]


def format_material_facts_for_llm(material_facts: List[Dict[str, Any]]) -> str:
    """Format material facts into readable text for LLM analysis.

    Args:
        material_facts: List of material facts dicts

    Returns:
        Formatted string for LLM consumption
    """
    if not material_facts:
        return "Nenhum fato relevante encontrado nos últimos 7 dias."

    formatted = "## Fatos Relevantes Recentes\n\n"

    for i, fact in enumerate(material_facts, 1):
        formatted += f"### {i}. {fact.get('titulo', 'Sem título')}\n"
        formatted += f"**Data:** {fact.get('data_hora', 'N/A')}\n"
        formatted += f"**Fonte:** {fact.get('fonte', 'N/A')}\n"

        if fact.get('conteudo'):
            formatted += f"\n{fact['conteudo']}\n"
        elif fact.get('headline'):
            formatted += f"\n{fact['headline']}\n"

        if fact.get('url'):
            formatted += f"[Link]({fact['url']})\n"

        formatted += "\n---\n\n"

    return formatted


# Langchain Tool definition for integration with agents
from langchain_core.tools import tool


@tool
def get_material_facts(ticker: str, trade_date: str, lookback_days: int = 7) -> str:
    """Fetch and analyze recent CVM material facts (Fatos Relevantes) for a Brazilian stock.

    Material facts are official announcements from companies to the CVM regarding
    events that may significantly affect the stock price or investor decisions.

    Args:
        ticker: Stock ticker symbol (e.g., 'PETR4', 'VALE3')
        trade_date: Reference date in format YYYY-MM-DD
        lookback_days: Number of days to look back (default: 7)

    Returns:
        Formatted string with material facts for analysis

    Example:
        get_material_facts('PETR4', '2026-04-10', lookback_days=7)
    """
    facts = fetch_material_facts(ticker, trade_date, lookback_days)
    return format_material_facts_for_llm(facts)


# For backward compatibility with existing agent_utils structure
__all__ = [
    'fetch_material_facts',
    'fetch_recent_announcements',
    'format_material_facts_for_llm',
    'get_material_facts',
]
