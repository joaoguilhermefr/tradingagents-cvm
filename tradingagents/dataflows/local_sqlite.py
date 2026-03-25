import sqlite3
import pandas as pd

# Mapeamento simplificado para evitar erros de "S.A." vs "S/A" no LIKE
TICKER_MAPPING = {
    "ENEV3": "ENEVA",
    "EQTL3": "EQUATORIAL",
    "ALUP11": "ALUPAR",
    "AURE3": "AUREN",
    "CPLE3": "PARANAENSE" # Pega "Cia Paranaense..." ou "Companhia Paranaense..."
}

# COLOQUE AQUI O CAMINHO ABSOLUTO DOS SEUS BANCOS (Como você fez no teste anterior)
PRICES_DB_PATH = r"C:\projetos\workflow-vs-agent-fundamentals-br\data\prices.db"
CVM_DB_PATH = r"C:\projetos\workflow-vs-agent-fundamentals-br\data\cvm.db"

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