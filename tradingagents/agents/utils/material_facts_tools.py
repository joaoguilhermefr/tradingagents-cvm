"""Tools for fetching and processing CVM material facts (Fatos Relevantes).

This module provides access to Brazilian Securities Commission (CVM) material facts
announcements for companies, fetching from the CVM IPE open-data portal and B3
plantão de notícias. PDFs are downloaded and converted to markdown via docling.

Pattern based on: workflow-vs-agent-fundamentals-br/src/tools/material_facts.py
"""

import base64
import calendar
import csv
import io
import json
import logging
import os
import re
import zipfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from tradingagents.dataflows.local_sqlite import CNPJ_MAPPING

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_FOLDER = "data/material_facts"
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

try:
    from finbr.b3 import plantao_noticias
    HAS_FINBR = True
except ImportError:
    HAS_FINBR = False
    plantao_noticias = None

try:
    from docling.document_converter import DocumentConverter
    HAS_DOCLING = True
except ImportError:
    HAS_DOCLING = False
    DocumentConverter = None


def _normalize_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


def _fetch_ipe_rows_for_cnpj(cnpj: str, year: int) -> List[Dict[str, str]]:
    """Download (and cache) the CVM IPE yearly ZIP and return all 'Fato Relevante' rows for cnpj."""
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


def _extract_cvm_id(cvm_url: str) -> Optional[str]:
    match = re.search(r"[?&]ID=(\d+)", cvm_url, re.IGNORECASE)
    return match.group(1) if match else None


def _download_pdf(cvm_url: str, pdf_path: str) -> bool:
    """Download a PDF from CVM via the ExibirPDF API and save to pdf_path.

    CVM serves the PDF as a base64-encoded JSON response from a POST endpoint.
    """
    cvm_id = _extract_cvm_id(cvm_url)
    if cvm_id is None:
        return False
    try:
        payload = json.dumps(
            {"codigoInstituicao": "2", "numeroProtocolo": cvm_id, "token": "", "versaoCaptcha": ""}
        )
        api_url = "https://www.rad.cvm.gov.br/ENET/frmExibirArquivoIPEExterno.aspx/ExibirPDF"
        r = requests.post(
            api_url,
            data=payload,
            headers={**_HEADERS, "Content-Type": "application/json; charset=utf-8"},
            verify=False,
            timeout=60,
        )
        r.raise_for_status()
        d = r.json().get("d", "")
        if not d or d.startswith(":ERRO:") or d == "V2":
            return False
        pdf_bytes = base64.b64decode(d)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        return True
    except Exception as e:
        logger.debug(f"PDF download failed for {cvm_url}: {e}")
        return False


def _pdf_to_markdown(pdf_path: str) -> str:
    """Convert a PDF file to markdown text using docling."""
    if not HAS_DOCLING:
        raise ImportError(
            "docling is required for PDF-to-markdown conversion. "
            "Install it with: pip install docling"
        )
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()


def _get_pdf_url_from_detail_page(detail_url: str) -> Optional[str]:
    """Fetch the B3 news detail page and return the CVM PDF link.

    The page content sits in <pre id="conteudoDetalhe"> and PDF URLs end with
    ?flnk or &flnk. JavaScript normally strips that suffix; we replicate that here.
    """
    try:
        r = requests.get(detail_url, headers=_HEADERS, verify=False, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        pre = soup.find("pre", id="conteudoDetalhe")
        if pre is None:
            return None
        text = pre.get_text()
        match = re.search(r"(https?://\S+?)(?:\?flnk|&flnk)", text)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None


def _extract_noticia_id(url: str) -> Optional[str]:
    match = re.search(r"idNoticia=(\d+)", url)
    return match.group(1) if match else None


def fetch_material_facts_from_ipe(
    ticker: str,
    year: int,
    month: int,
    output_folder: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch 'Fato Relevante' announcements from CVM IPE open-data portal.

    Downloads PDFs from CVM, converts them to markdown via docling, and caches
    results to disk. Skips files already present in output_folder.

    Returns a list of dicts with keys: titulo, headline, data_hora, conteudo, url.
    """
    cnpj = CNPJ_MAPPING.get(ticker, "")
    if not cnpj:
        logger.warning(f"No CNPJ mapping found for ticker {ticker}")
        return []

    ticker_root = ticker[:4]
    if output_folder is None:
        output_folder = os.path.join(DEFAULT_OUTPUT_FOLDER, ticker_root)
    os.makedirs(output_folder, exist_ok=True)

    rows = _fetch_ipe_rows_for_cnpj(cnpj, year)
    prefix = f"{year}-{month:02d}"

    results = []
    for row in rows:
        if not row.get("Data_Entrega", "").startswith(prefix):
            continue

        noticia_id = row.get("Protocolo_Entrega", "").strip()
        if not noticia_id:
            continue

        md_path = os.path.join(output_folder, f"{noticia_id}.md")
        pdf_path = os.path.join(output_folder, f"{noticia_id}.pdf")

        if os.path.exists(md_path):
            with open(md_path) as f:
                conteudo = f.read()
        else:
            link = row.get("Link_Download", "")
            num_match = re.search(r"[?&]numProtocolo=(\d+)", link, re.IGNORECASE)
            if not num_match:
                continue
            cvm_url = (
                "https://www.rad.cvm.gov.br/ENET/"
                f"frmExibirArquivoIPEExterno.aspx?ID={num_match.group(1)}"
            )
            if not os.path.exists(pdf_path):
                if not _download_pdf(cvm_url, pdf_path):
                    continue
            try:
                conteudo = _pdf_to_markdown(pdf_path)
            except Exception as e:
                logger.warning(f"PDF conversion failed for {noticia_id}: {e}")
                continue
            with open(md_path, "w") as f:
                f.write(conteudo)

        results.append(
            {
                "ticker": ticker,
                "titulo": row.get("Assunto", ""),
                "headline": row.get("Assunto", ""),
                "data_hora": row.get("Data_Entrega", ""),
                "conteudo": conteudo,
                "url": row.get("Link_Download", ""),
                "fonte": "CVM/IPE",
                "protocol": noticia_id,
            }
        )

    return results


def fetch_material_facts(
    ticker: str,
    year: int,
    month: int,
    output_folder: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch 'Fato Relevante' B3 announcements for a given ticker and month.

    Downloads PDFs from CVM via B3 plantão de notícias detail pages, converts them
    to markdown with docling, and caches results to disk.

    Returns a list of dicts with keys: titulo, headline, data_hora, conteudo, url.
    Returns [] on empty result or unrecoverable error.
    """
    if not HAS_FINBR or plantao_noticias is None:
        return []

    ticker_root = ticker[:4]
    if output_folder is None:
        output_folder = os.path.join(DEFAULT_OUTPUT_FOLDER, ticker_root)
    os.makedirs(output_folder, exist_ok=True)

    inicio = f"{year}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    fim = f"{year}-{month:02d}-{last_day:02d}"

    try:
        noticias = plantao_noticias.get(inicio=inicio, fim=fim)
    except Exception:
        return []

    results = []
    for n in noticias:
        if not n.ticker.startswith(ticker_root):
            continue
        if "Fato Relevante" not in (n.titulo or "") and "Fato Relevante" not in (n.headline or ""):
            continue

        noticia_id = _extract_noticia_id(n.url)
        if noticia_id is None:
            continue

        md_path = os.path.join(output_folder, f"{noticia_id}.md")
        pdf_path = os.path.join(output_folder, f"{noticia_id}.pdf")

        if os.path.exists(md_path):
            with open(md_path) as f:
                conteudo = f.read()
        else:
            pdf_url = _get_pdf_url_from_detail_page(n.url)
            if pdf_url is None:
                continue
            if not os.path.exists(pdf_path):
                if not _download_pdf(pdf_url, pdf_path):
                    continue
            try:
                conteudo = _pdf_to_markdown(pdf_path)
            except Exception as e:
                logger.warning(f"PDF conversion failed for {noticia_id}: {e}")
                continue
            with open(md_path, "w") as f:
                f.write(conteudo)

        results.append(
            {
                "ticker": ticker,
                "titulo": n.titulo,
                "headline": n.headline,
                "data_hora": n.data_hora,
                "conteudo": conteudo,
                "url": n.url,
                "fonte": "CVM/B3",
            }
        )

    return results


def _get_year_months_for_range(trade_date: str, lookback_days: int) -> List[tuple]:
    """Returns a deduplicated list of (year, month) tuples covered by the lookback window."""
    current = datetime.strptime(trade_date, "%Y-%m-%d")
    start = current - timedelta(days=lookback_days)
    months = set()
    cursor = start.replace(day=1)
    while cursor <= current:
        months.add((cursor.year, cursor.month))
        # advance to next month
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)
    return sorted(months)


def fetch_material_facts_for_tool(
    ticker: str,
    trade_date: str,
    lookback_days: int = 7,
) -> List[Dict[str, Any]]:
    """Fetch material facts for a ticker over a lookback window ending at trade_date.

    Tries CVM IPE first (requires CNPJ mapping), then falls back to B3 plantão de notícias.
    """
    year_months = _get_year_months_for_range(trade_date, lookback_days)
    results = []

    current = datetime.strptime(trade_date, "%Y-%m-%d")
    start = current - timedelta(days=lookback_days)

    for year, month in year_months:
        facts = fetch_material_facts_from_ipe(ticker, year, month)
        if not facts:
            facts = fetch_material_facts(ticker, year, month)

        # Filter to the actual date range (the month fetch may be broader)
        for fact in facts:
            try:
                fact_date = datetime.strptime(fact["data_hora"][:10], "%Y-%m-%d")
                if start <= fact_date <= current:
                    results.append(fact)
            except Exception:
                results.append(fact)

    return results


def format_material_facts_for_llm(material_facts: List[Dict[str, Any]]) -> str:
    """Format material facts into readable text for LLM analysis."""
    if not material_facts:
        return "Nenhum fato relevante encontrado nos últimos 7 dias."

    formatted = "## Fatos Relevantes Recentes\n\n"

    for i, fact in enumerate(material_facts, 1):
        formatted += f"### {i}. {fact.get('titulo', 'Sem título')}\n"
        formatted += f"**Data:** {fact.get('data_hora', 'N/A')}\n"
        formatted += f"**Fonte:** {fact.get('fonte', 'N/A')}\n"

        if fact.get("conteudo"):
            formatted += f"\n{fact['conteudo']}\n"
        elif fact.get("headline"):
            formatted += f"\n{fact['headline']}\n"

        if fact.get("url"):
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
    Full PDF content is retrieved and converted to markdown.

    Args:
        ticker: Stock ticker symbol (e.g., 'PETR4', 'VALE3')
        trade_date: Reference date in format YYYY-MM-DD
        lookback_days: Number of days to look back (default: 7)

    Returns:
        Formatted string with material facts content for analysis

    Example:
        get_material_facts('EGIE3', '2024-12-31', lookback_days=30)
    """
    facts = fetch_material_facts_for_tool(ticker, trade_date, lookback_days)
    return format_material_facts_for_llm(facts)


__all__ = [
    "fetch_material_facts",
    "fetch_material_facts_from_ipe",
    "fetch_material_facts_for_tool",
    "format_material_facts_for_llm",
    "get_material_facts",
]
