import sqlite3
import pandas as pd
import os
from datetime import datetime

# Mapeamento completo de todos os 15 tickers para nomes de empresa
TICKER_MAPPING = {
    "ALUP11": "ALUPAR",
    "AURE3":  "AUREN",
    "CPLE3":  "PARANAENSE",
    "EGIE3":  "ENGIE",
    "ELET3":  "ELETROBRAS",
    "ENEV3":  "ENEVA",
    "ENGI3":  "ENERGISA",
    "EQTL3":  "EQUATORIAL",
    "ISAE3":  "ISA ENERGIA",
    "LIGT3":  "LIGHT",
    "NEOE3":  "NEOENERGIA",
    "RNEW11": "RENOVA",
    "SRNA3":  "SERENA",
    "RECV3":  "PETROREC",
    "VALE3":  "VALE",
}

# Configuração de caminhos dos bancos de dados via variáveis de ambiente com defaults
_DEFAULT_DATA_DIR = "/Users/thiagocastroferreira/Documents/workspace/workflow-vs-agent-fundamentals-br/data"
PRICES_DB_PATH = os.environ.get("PRICES_DB_PATH", os.path.join(_DEFAULT_DATA_DIR, "prices.db"))
CVM_DB_PATH = os.environ.get("CVM_DB_PATH", os.path.join(_DEFAULT_DATA_DIR, "cvm.db"))

def get_local_prices(ticker: str, start_date: str, end_date: str) -> str:
    """Extrai a série de preços do prices.db para o Technical Analyst."""
    try:
        conn = sqlite3.connect(PRICES_DB_PATH)
        # CORREÇÃO: PRECO_DE_ABERTURA
        query = f"""
            SELECT DATA_DO_PREGAO, PRECO_DE_ABERTURA, PRECO_MAXIMO, PRECO_MINIMO, PRECO_ULTIMO_NEGOCIO, VOLUME_TOTAL_NEGOCIADO
            FROM COTAHIST
            WHERE CODIGO_DE_NEGOCIACAO = '{ticker}'
            AND DATA_DO_PREGAO BETWEEN '{start_date}' AND '{end_date} 23:59:59'
            ORDER BY DATA_DO_PREGAO ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return f"Nenhum dado de preço encontrado para {ticker} no período fornecido."

        res = f"Histórico de Preços para {ticker} de {start_date} a {end_date}:\n"
        for _, row in df.iterrows():
            date_str = str(row['DATA_DO_PREGAO']).split()[0]
            # CORREÇÃO: Acessando PRECO_DE_ABERTURA
            res += f"- {date_str}: Abert R${row['PRECO_DE_ABERTURA']:.2f} | Máx R${row['PRECO_MAXIMO']:.2f} | Mín R${row['PRECO_MINIMO']:.2f} | Fech R${row['PRECO_ULTIMO_NEGOCIO']:.2f} | Vol: {row['VOLUME_TOTAL_NEGOCIADO']}\n"
        return res
    except Exception as e:
        return f"Erro ao acessar prices.db: {str(e)}"

def get_local_fundamentals(ticker: str, target_date: str) -> str:
    """Busca o demonstrativo completo (nível 3) mais recente no cvm.db."""
    company_name = TICKER_MAPPING.get(ticker)
    if not company_name:
        return f"Mapeamento de empresa não encontrado para o ticker {ticker}."

    try:
        conn = sqlite3.connect(CVM_DB_PATH)
        
        # 1. Isolar a data do relatório mais recente antes do momento da decisão
        # Usando LIKE com % de ambos os lados para garantir
        date_query = f"""
            SELECT MAX(REPORT_DATE) as last_report
            FROM DFP_ITR_CVM
            WHERE COMPANY_NAME LIKE '%{company_name}%'
            AND REPORT_DATE <= '{target_date} 23:59:59'
        """
        last_report_df = pd.read_sql_query(date_query, conn)
        last_report_date = last_report_df.iloc[0]['last_report']

        if not last_report_date:
            conn.close()
            return f"Nenhum relatório financeiro encontrado para {ticker} antes de {target_date}."

        # 2. Extrair o relatório completo dessa data base específica
        query = f"""
            SELECT ACCOUNT_NUMBER, ACCOUNT_NAME, ACCOUNT_VALUE
            FROM DFP_ITR_CVM
            WHERE COMPANY_NAME LIKE '%{company_name}%'
            AND REPORT_DATE = '{last_report_date}'
            ORDER BY ACCOUNT_NUMBER ASC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return f"Relatório encontrado em {last_report_date}, mas sem contas cadastradas."

        # 3. Formatar como um demonstrativo financeiro
        res = f"Demonstrações Financeiras (DFP/ITR) de {ticker} - Ref: {last_report_date}\n"
        res += "-" * 60 + "\n"
        for _, row in df.iterrows():
            res += f"[{row['ACCOUNT_NUMBER']}] {row['ACCOUNT_NAME']}: R$ {row['ACCOUNT_VALUE']:,.2f}\n"
        res += "-" * 60 + "\n"
        
        return res
    except Exception as e:
        return f"Erro ao acessar cvm.db: {str(e)}"

def get_local_prices_df(ticker: str, start_date: str, end_date: str) -> pd.DataFrame | None:
    """Returns OHLCV DataFrame from prices.db, or None on failure.

    Args:
        ticker: Stock ticker (e.g., 'EGIE3')
        start_date: Start date in format YYYY-MM-DD
        end_date: End date in format YYYY-MM-DD

    Returns:
        DataFrame with columns [date, open, high, low, close, volume] or None
    """
    try:
        conn = sqlite3.connect(PRICES_DB_PATH)
        query = """
            SELECT DATA_DO_PREGAO as date,
                   PRECO_DE_ABERTURA as open,
                   PRECO_MAXIMO as high,
                   PRECO_MINIMO as low,
                   PRECO_ULTIMO_NEGOCIO as close,
                   VOLUME_TOTAL_NEGOCIADO as volume
            FROM COTAHIST
            WHERE CODIGO_DE_NEGOCIACAO = ?
              AND DATA_DO_PREGAO BETWEEN ? AND ?
            ORDER BY DATA_DO_PREGAO ASC
        """
        df = pd.read_sql_query(query, conn, params=(ticker, start_date, end_date + " 23:59:59"))
        conn.close()
        return None if df.empty else df
    except Exception:
        return None

CNPJ_MAPPING = {
    "ALUP11": "08.364.948/0001-38",
    "AURE3":  "28.594.234/0001-23",
    "CPLE3":  "76.483.817/0001-20",
    "EGIE3":  "02.474.103/0001-19",
    "ELET3":  "00.001.180/0001-26",
    "ENEV3":  "04.423.567/0001-21",
    "ENGI3":  "00.864.214/0001-06",
    "EQTL3":  "03.220.438/0001-73",
    "ISAE3":  "02.998.611/0001-04",
    "LIGT3":  "03.378.521/0001-75",
    "NEOE3":  "01.083.200/0001-18",
    "RNEW11": "08.534.605/0001-74",
    "SRNA3":  "42.500.384/0001-51",
    "RECV3":  "03.342.704/0001-30",
    "VALE3":  "33.592.510/0001-54",
}

SHARES_MULTIPLIER_MAPPING = {
    "ALUP11": 1 / 3,  # 1 ALUP11 unit = 3 individual CVM shares
}


def get_local_fundamentals_dict(ticker: str, target_date: str) -> dict:
    """Returns {ACCOUNT_NAME: ACCOUNT_VALUE} for the most recent report before target_date.

    Args:
        ticker: Stock ticker (e.g., 'EGIE3')
        target_date: Reference date in format YYYY-MM-DD

    Returns:
        Dictionary mapping CVM account names to values, or empty dict on failure
    """
    company_name = TICKER_MAPPING.get(ticker)
    if not company_name:
        return {}
    try:
        conn = sqlite3.connect(CVM_DB_PATH)
        date_query = """
            SELECT MAX(REPORT_DATE) as last_report FROM DFP_ITR_CVM
            WHERE COMPANY_NAME LIKE ? AND REPORT_DATE <= ?
        """
        last_report_df = pd.read_sql_query(
            date_query, conn, params=(f"%{company_name}%", target_date + " 23:59:59")
        )
        last_report_date = last_report_df.iloc[0]["last_report"]
        if not last_report_date:
            conn.close()
            return {}
        data_query = """
            SELECT ACCOUNT_NAME, ACCOUNT_VALUE FROM DFP_ITR_CVM
            WHERE COMPANY_NAME LIKE ? AND REPORT_DATE = ?
        """
        df = pd.read_sql_query(
            data_query, conn, params=(f"%{company_name}%", last_report_date)
        )
        conn.close()
        return dict(zip(df["ACCOUNT_NAME"], df["ACCOUNT_VALUE"]))
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Advanced CVM queries using CNPJ + account numbers (with proper TTM)
# Ported from workflow-vs-agent-fundamentals-br/src/experiments/fundamental_analysis/workflow.py
# ---------------------------------------------------------------------------

# Keys used in db_fields dict returned by get_db_fields()
DB_ATIVO = "Ativo"
DB_DISPONIBILIDADES = "Disponibilidades"
DB_ATIVO_CIRCULANTE = "Ativo Circulante"
DB_PASSIVO_CIRCULANTE = "Passivo Circulante"
DB_DIVIDA_BRUTA = "Dív. Bruta"
DB_PATRIMONIO_LIQUIDO = "Patrim. Líq"
DB_FORNECEDORES = "Fornecedores"
DB_RECEITA_LIQUIDA_ANUAL = "Receita Líquida (12 meses)"
DB_LUCRO_BRUTO_ANUAL = "Lucro Bruto (12 meses)"
DB_EBIT_ANUAL = "EBIT (12 meses)"
DB_EBITDA_ANUAL = "EBITDA (12 meses)"
DB_LUCRO_LIQUIDO_ANUAL = "Lucro Líquido (12 meses)"
DB_RECEITA_LIQUIDA_TRIMESTRE = "Receita Líquida (3 meses)"
DB_EBIT_TRIMESTRE = "EBIT (3 meses)"
DB_LUCRO_LIQUIDO_TRIMESTRE = "Lucro Líquido (3 meses)"


def _db_account(
    cnpj: str,
    account: str,
    date: str,
    exerc_order: str = "ÚLTIMO",
    period: str = "any",
) -> float:
    """Returns ACCOUNT_VALUE for a single CVM account, or 0.0 if not found.

    period: 'any' (no filter), 'accumulated' (start month = Jan, for DRE ytd),
            'quarterly' (start month != Jan, for isolated quarter in ITRs).
    """
    period_filter = ""
    if period == "accumulated":
        period_filter = "AND strftime('%m', ANALYSIS_START_PERIOD_DATE) = '01'"
    elif period == "quarterly":
        period_filter = "AND strftime('%m', ANALYSIS_START_PERIOD_DATE) != '01'"

    query = f"""
    SELECT ACCOUNT_VALUE FROM DFP_ITR_CVM
    WHERE CNPJ = ? AND REPORT_DATE = ?
      AND ACCOUNT_NUMBER = ? AND EXERC_ORDER = ?
      {period_filter}
    ORDER BY CAST(VERSION AS INTEGER) DESC LIMIT 1;"""
    try:
        conn = sqlite3.connect(CVM_DB_PATH)
        df = pd.read_sql_query(query, conn, params=(cnpj, date, account, exerc_order))
        conn.close()
        if df.empty:
            return 0.0
        val = df.iloc[0]["ACCOUNT_VALUE"]
        return float(val) if val is not None else 0.0
    except Exception:
        return 0.0


def _db_account_name(cnpj: str, account: str, date: str, exerc_order: str = "ÚLTIMO") -> str:
    """Returns the ACCOUNT_NAME for a given account, or '' if not found."""
    query = """
    SELECT ACCOUNT_NAME FROM DFP_ITR_CVM
    WHERE CNPJ = ? AND REPORT_DATE = ?
      AND ACCOUNT_NUMBER = ? AND EXERC_ORDER = ?
    ORDER BY CAST(VERSION AS INTEGER) DESC LIMIT 1;"""
    try:
        conn = sqlite3.connect(CVM_DB_PATH)
        df = pd.read_sql_query(query, conn, params=(cnpj, date, account, exerc_order))
        conn.close()
        if df.empty:
            return ""
        return str(df.iloc[0]["ACCOUNT_NAME"] or "")
    except Exception:
        return ""


def _get_patrimonio_liquido(cnpj: str, date: str) -> float:
    """Returns Patrimônio Líquido (excluding minority interests) for any company structure.

    Standard companies report PL at account 2.03 (minorities at 2.03.09).
    Banks and financial institutions report PL at a higher account (e.g. 2.07),
    with minorities labelled 'Não Controladores' in a subaccount.
    """
    pl_name = _db_account_name(cnpj, "2.03", date)
    if "patrimônio" in pl_name.lower():
        return _db_account(cnpj, "2.03", date) - _db_account(cnpj, "2.03.09", date)

    for suffix in ("04", "05", "06", "07", "08", "09"):
        acc = f"2.{suffix}"
        name = _db_account_name(cnpj, acc, date)
        if "patrimônio" not in name.lower():
            continue
        pl_total = _db_account(cnpj, acc, date)
        minorities = 0.0
        for sub in ("01", "02", "03", "04", "05", "06", "07", "08", "09"):
            sub_acc = f"{acc}.{sub}"
            sub_name = _db_account_name(cnpj, sub_acc, date)
            if "não controlador" in sub_name.lower():
                minorities = _db_account(cnpj, sub_acc, date)
                break
        return pl_total - minorities

    return _db_account(cnpj, "2.03", date)


def get_total_shares(ticker: str, date: str) -> float:
    """Returns the number of outstanding shares from CVM_SHARE_COMPOSITION.

    Applies shares_multiplier from SHARES_MULTIPLIER_MAPPING for unit-based tickers
    (e.g. ALUP11: 1 unit = 3 CVM shares → multiplier = 1/3).
    Returns 0.0 if no CNPJ mapping or no data found.
    """
    cnpj = CNPJ_MAPPING.get(ticker)
    if not cnpj:
        return 0.0
    shares_multiplier = SHARES_MULTIPLIER_MAPPING.get(ticker, 1.0)
    query = """
    SELECT TOTAL_SHARES_ISSUED, TOTAL_SHARES_TREASURY
    FROM CVM_SHARE_COMPOSITION
    WHERE CNPJ = ? AND REPORT_DATE = ?;"""
    try:
        conn = sqlite3.connect(CVM_DB_PATH)
        df = pd.read_sql_query(query, conn, params=(cnpj, date))
        conn.close()
        if df.empty:
            return 0.0
        row = df.iloc[0]
        issued = float(row["TOTAL_SHARES_ISSUED"] or 0)
        treasury = float(row["TOTAL_SHARES_TREASURY"] or 0)
        return (issued - treasury) * shares_multiplier
    except Exception:
        return 0.0


def get_db_fields(ticker: str, date: str) -> dict:
    """Fetches all 15 base financial fields from the CVM database with proper TTM computation.

    Uses CNPJ + account numbers for deterministic queries. Handles both DFP (annual)
    and ITR (quarterly) reports, computing Trailing Twelve Months for income statement items.

    Account mapping:
      Ativo                    → 1
      Disponibilidades         → 1.01.01 + 1.01.02
      Ativo Circulante         → 1.01
      Passivo Circulante       → 2.01
      Dív. Bruta               → 2.01.04 + 2.02.01
      Patrim. Líq              → _get_patrimonio_liquido() (handles banks: 2.07 instead of 2.03)
      Fornecedores             → 2.01.02
      Receita Líquida (12m)    → TTM of 3.01
      Lucro Bruto (12m)        → TTM of 3.03
      EBIT (12m)               → TTM of (3.03 + 3.04.01 + 3.04.02)
      EBITDA (12m)             → TTM EBIT + abs(TTM 7.04.01)
      Lucro Líquido (12m)      → TTM of 3.11.01 (controladores; fallback 3.11)
      Receita Líquida (3m)     → isolated quarter of 3.01
      EBIT (3m)                → isolated quarter of (3.03 + 3.04.01 + 3.04.02)
      Lucro Líquido (3m)       → isolated quarter of 3.11.01 (fallback 3.11)

    Returns empty dict if no CNPJ mapping exists for the ticker.
    """
    cnpj = CNPJ_MAPPING.get(ticker)
    if not cnpj:
        return {}

    date_dt = datetime.fromisoformat(date) if isinstance(date, str) else date
    year, month = date_dt.year, date_dt.month
    is_annual = month == 12

    if month <= 3:
        prev_quarter = f"{year - 1}-12-31"
    elif month <= 6:
        prev_quarter = f"{year}-03-31"
    elif month <= 9:
        prev_quarter = f"{year}-06-30"
    else:
        prev_quarter = f"{year}-09-30"

    fy_prev = f"{year - 1}-12-31"
    ytd_prev = f"{year - 1}-{month:02d}-{date_dt.day:02d}"

    def _ttm(account: str) -> float:
        ytd_current = _db_account(cnpj, account, date, period="accumulated")
        if is_annual:
            return ytd_current
        return (
            ytd_current
            + _db_account(cnpj, account, fy_prev)
            - _db_account(cnpj, account, ytd_prev, period="accumulated")
        )

    def _ttm_controlling(account_ctrl: str, account_total: str) -> float:
        if is_annual:
            ctrl_val = _db_account(cnpj, account_ctrl, date, period="accumulated")
            return ctrl_val if ctrl_val != 0.0 else _ttm(account_total)
        ctrl_ytd = _db_account(cnpj, account_ctrl, date, period="accumulated")
        ctrl_fy_prev = _db_account(cnpj, account_ctrl, fy_prev)
        ctrl_ytd_prev = _db_account(cnpj, account_ctrl, ytd_prev, period="accumulated")
        if ctrl_ytd != 0.0 and ctrl_fy_prev != 0.0 and ctrl_ytd_prev != 0.0:
            return ctrl_ytd + ctrl_fy_prev - ctrl_ytd_prev
        return _ttm(account_total)

    def _ttm_sum(*accounts: str) -> float:
        return sum(_ttm(acc) for acc in accounts)

    def _quarter(account: str) -> float:
        if month <= 3:
            return _db_account(cnpj, account, date, period="accumulated")
        return _db_account(cnpj, account, date, period="accumulated") - _db_account(
            cnpj, account, prev_quarter, period="accumulated"
        )

    def _quarter_sum(*accounts: str) -> float:
        return sum(_quarter(acc) for acc in accounts)

    ativo = _db_account(cnpj, "1", date)
    disponibilidades = _db_account(cnpj, "1.01.01", date) + _db_account(cnpj, "1.01.02", date)
    ativo_circulante = _db_account(cnpj, "1.01", date)
    passivo_circulante = _db_account(cnpj, "2.01", date)
    divida_bruta = _db_account(cnpj, "2.01.04", date) + _db_account(cnpj, "2.02.01", date)
    patrimonio_liquido = _get_patrimonio_liquido(cnpj, date)
    fornecedores = _db_account(cnpj, "2.01.02", date)

    receita_liquida_anual = _ttm("3.01")
    lucro_bruto_anual = _ttm("3.03")
    ebit_anual = _ttm_sum("3.03", "3.04.01", "3.04.02")
    ebitda_anual = ebit_anual + abs(_ttm("7.04.01"))
    lucro_liquido_anual = _ttm_controlling("3.11.01", "3.11")

    receita_liquida_trimestre = _quarter("3.01")
    ebit_trimestre = _quarter_sum("3.03", "3.04.01", "3.04.02")

    curr_quarter_ctrl = _db_account(cnpj, "3.11.01", date, period="accumulated")
    if month <= 3:
        lucro_liquido_trimestre = (
            curr_quarter_ctrl if curr_quarter_ctrl != 0.0 else _quarter("3.11")
        )
    else:
        prev_quarter_ctrl = _db_account(cnpj, "3.11.01", prev_quarter, period="accumulated")
        if curr_quarter_ctrl != 0.0 and prev_quarter_ctrl != 0.0:
            lucro_liquido_trimestre = curr_quarter_ctrl - prev_quarter_ctrl
        else:
            lucro_liquido_trimestre = _quarter("3.11")

    return {
        DB_ATIVO: ativo,
        DB_DISPONIBILIDADES: disponibilidades,
        DB_ATIVO_CIRCULANTE: ativo_circulante,
        DB_PASSIVO_CIRCULANTE: passivo_circulante,
        DB_DIVIDA_BRUTA: divida_bruta,
        DB_PATRIMONIO_LIQUIDO: patrimonio_liquido,
        DB_FORNECEDORES: fornecedores,
        DB_RECEITA_LIQUIDA_ANUAL: receita_liquida_anual,
        DB_LUCRO_BRUTO_ANUAL: lucro_bruto_anual,
        DB_EBIT_ANUAL: ebit_anual,
        DB_EBITDA_ANUAL: ebitda_anual,
        DB_LUCRO_LIQUIDO_ANUAL: lucro_liquido_anual,
        DB_RECEITA_LIQUIDA_TRIMESTRE: receita_liquida_trimestre,
        DB_EBIT_TRIMESTRE: ebit_trimestre,
        DB_LUCRO_LIQUIDO_TRIMESTRE: lucro_liquido_trimestre,
    }