"""Tools for fetching and processing CVM material facts (Fatos Relevantes).

This module provides access to Brazilian Securities Commission (CVM) material facts
announcements for companies, fetching from the B3 plantão de notícias and CVM IPE.

Pattern based on: workflow-vs-agent-fundamentals-br/src/tools/material_facts.py
"""

import os
import re
import csv
import io
import zipfile
import calendar
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

# CVM data sources
_CVM_IPE_BASE_URL = (
    "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_{year}.zip"
)
_IPE_CACHE_FOLDER = "data/ipe_cache"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}

# Try to import optional finbr dependency
try:
    from finbr.b3 import plantao_noticias
    HAS_FINBR = True
except ImportError:
    HAS_FINBR = False
    plantao_noticias = None


def _normalize_cnpj(cnpj: str) -> str:
    """Remove non-numeric characters from CNPJ."""
    return re.sub(r"\D", "", cnpj)


def _fetch_ipe_rows_for_cnpj(cnpj: str, year: int) -> List[Dict[str, str]]:
    """Download (and cache) the CVM IPE yearly ZIP and return all 'Fato Relevante' rows for cnpj.

    Pattern from: workflow-vs-agent-fundamentals-br/src/tools/material_facts.py
    """
    os.makedirs(_IPE_CACHE_FOLDER, exist_ok=True)
    zip_path = os.path.join(_IPE_CACHE_FOLDER, f"ipe_cia_aberta_{year}.zip")

    if not os.path.exists(zip_path):
        url = _CVM_IPE_BASE_URL.format(year=year)
        try:
            r = requests.get(url, headers=_HEADERS, verify=False, timeout=120, stream=True)
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
        except Exception as e:
            logger.warning(f"Failed to download CVM IPE data for {year}: {e}")
            return []

    cnpj_norm = _normalize_cnpj(cnpj)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            csv_name = f"ipe_cia_aberta_{year}.csv"
            with zf.open(csv_name) as raw:
                reader = csv.DictReader(
                    io.TextIOWrapper(raw, encoding="latin-1"),
                    delimiter=";",
                )
                return [
                    row
                    for row in reader
                    if _normalize_cnpj(row.get("CNPJ_Companhia", "")) == cnpj_norm
                    and row.get("Categoria", "") == "Fato Relevante"
                ]
    except Exception as e:
        logger.warning(f"Failed to parse IPE data for {year}: {e}")
        return []


def fetch_material_facts_from_ipe(
    cnpj: str,
    ticker: str,
    year: int,
    month: int,
) -> List[Dict[str, Any]]:
    """Fetch 'Fato Relevante' announcements from CVM IPE data portal.

    Pattern from: workflow-vs-agent-fundamentals-br/src/tools/material_facts.py
    """
    try:
        rows = _fetch_ipe_rows_for_cnpj(cnpj, year)
        prefix = f"{year}-{month:02d}"

        results = []
        for row in rows:
            if not row.get("Data_Entrega", "").startswith(prefix):
                continue

            noticia_id = row.get("Protocolo_Entrega", "").strip()
            if not noticia_id:
                continue

            result_item = {
                "ticker": ticker,
                "titulo": row.get("Assunto", ""),
                "headline": row.get("Assunto", ""),
                "data_hora": row.get("Data_Entrega", ""),
                "conteudo": f"Material fact from CVM: {row.get('Assunto', '')}",
                "url": row.get("Link_Download", ""),
                "fonte": "CVM/IPE",
                "protocol": noticia_id,
            }
            results.append(result_item)

        return results
    except Exception as e:
        logger.error(f"Error fetching from IPE for {ticker}: {e}")
        return []


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
            - fonte: Source ('CVM/B3' or 'CVM/IPE')
    """
    results = []

    try:
        # Try finbr first if available
        if HAS_FINBR and plantao_noticias:
            try:
                current = datetime.strptime(trade_date, "%Y-%m-%d")
                start = current - timedelta(days=lookback_days)

                inicio = f"{start.year}-{start.month:02d}-{start.day:02d}"
                fim = f"{current.year}-{current.month:02d}-{current.day:02d}"

                noticias = plantao_noticias.get(inicio=inicio, fim=fim)

                if noticias:
                    ticker_root = ticker[:4]  # PETR4 -> PETR

                    for noticia in noticias:
                        noticia_ticker = getattr(noticia, 'ticker', '')
                        titulo = getattr(noticia, 'titulo', '')
                        headline = getattr(noticia, 'headline', '')

                        # Match ticker and filter for material facts
                        if noticia_ticker.startswith(ticker_root) and \
                           ("Fato Relevante" in titulo or "Fato Relevante" in headline):

                            result_item = {
                                "ticker": noticia_ticker,
                                "titulo": titulo,
                                "headline": headline,
                                "data_hora": getattr(noticia, 'data_hora', ''),
                                "conteudo": getattr(noticia, 'summary', '') or headline,
                                "url": getattr(noticia, 'url', ''),
                                "fonte": "CVM/B3",
                            }
                            results.append(result_item)
            except Exception as e:
                logger.warning(f"finbr fetch failed: {e}")
                # Fall through to IPE approach

        # If no results from finbr, try CVM IPE directly
        if not results:
            try:
                current = datetime.strptime(trade_date, "%Y-%m-%d")
                # Fetch from multiple months to ensure coverage
                for months_back in range(lookback_days // 30 + 1):
                    check_date = current - timedelta(days=months_back * 30)
                    year = check_date.year
                    month = check_date.month

                    # Try to get CNPJ mapping (simplified - use ticker root)
                    # In production, would need actual CNPJ for the ticker
                    ipe_results = fetch_material_facts_from_ipe(
                        cnpj="",  # Would need mapping
                        ticker=ticker,
                        year=year,
                        month=month,
                    )
                    results.extend(ipe_results)

            except Exception as e:
                logger.debug(f"IPE fetch also failed: {e}")

    except Exception as e:
        logger.error(f"Error fetching material facts for {ticker}: {e}")

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
