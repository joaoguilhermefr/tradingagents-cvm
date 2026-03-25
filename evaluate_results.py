import pandas as pd
import sqlite3
import re

# Configurações
RESULTS_FILE = "tradingagents_vs_iclr_results.csv"
PRICES_DB_PATH = r"C:\projetos\workflow-vs-agent-fundamentals-br\data\prices.db"

def get_price_at_date(ticker, date_str):
    """Busca o preço de fecho real no banco de dados para a data da decisão."""
    try:
        conn = sqlite3.connect(PRICES_DB_PATH)
        query = f"""
            SELECT PRECO_ULTIMO_NEGOCIO 
            FROM COTAHIST 
            WHERE CODIGO_DE_NEGOCIACAO = '{ticker}' 
            AND DATA_DO_PREGAO LIKE '{date_str}%'
            LIMIT 1
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.iloc[0]['PRECO_ULTIMO_NEGOCIO'] if not df.empty else None
    except:
        return None

def parse_decision(raw_text):
    """Extrai a decisão final (Buy, Sell, Hold) do texto gerado pelo agente."""
    text = str(raw_text).upper()
    if "BUY" in text: return "BUY"
    if "SELL" in text: return "SELL"
    return "HOLD"

def calculate_metrics():
    df = pd.read_csv(RESULTS_FILE)
    df['decision'] = df['raw_decision'].apply(parse_decision)
    df = df.sort_values(by=['stock', 'date'])

    portfolio_returns = {}
    
    for stock in df['stock'].unique():
        stock_data = df[df['stock'] == stock]
        buy_prices = []
        stock_return = 0.0
        
        print(f"\n--- Avaliando {stock} ---")
        
        for _, row in stock_data.iterrows():
            price = get_price_at_date(stock, row['date'])
            if price is None: continue
            
            decision = row['decision']
            
            if decision == "BUY":
                buy_prices.append(price)
                print(f"[{row['date']}] Compra a R$ {price:.2f}")
            
            elif decision == "SELL" and buy_prices:
                avg_buy_price = sum(buy_prices) / len(buy_prices)
                # Fórmula R_total do Artigo ICLR: (P_sell - P_avg_buy) / P_avg_buy
                trade_return = (price - avg_buy_price) / avg_buy_price
                stock_return += trade_return
                print(f"[{row['date']}] Venda a R$ {price:.2f} | Retorno do Trade: {trade_return:.2%}")
                buy_prices = [] # Zera a posição após a venda (conforme simplificação do artigo)
                
        portfolio_returns[stock] = stock_return

    # Resultados Finais
    print("\n" + "="*40)
    print("RESULTADO FINAL (R_total por Ativo)")
    print("="*40)
    total_sum = 0
    for stock, ret in portfolio_returns.items():
        print(f"{stock}: {ret:.2%}")
        total_sum += ret
    
    print("-" * 40)
    print(f"SOMA TOTAL DOS RETORNOS: {total_sum:.2%}")
    print("="*40)

if __name__ == "__main__":
    calculate_metrics()