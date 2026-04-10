import sqlite3
import pandas as pd
import os

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