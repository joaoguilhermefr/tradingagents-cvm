import pandas as pd
import yfinance as yf
import numpy as np

df = pd.read_csv('tradingagents_vs_iclr_results.csv')

df['ticker_yf'] = df['stock'] + '.SA'
tickers = df['ticker_yf'].unique().tolist()

print("Baixando preços da B3...")
# Alteração aqui: de 'Adj Close' para 'Close'
data = yf.download(tickers, start=df['date'].min(), end="2026-01-01", interval="1mo")['Close']

# roi
initial_capital = 100000.0
portfolio_value = initial_capital
num_stocks = len(tickers)
capital_per_stock = initial_capital / num_stocks

# dicionário para rastrear o saldo de cada "caixinha" de ação
positions = {ticker: capital_per_stock for ticker in tickers}

dates = sorted(df['date'].unique())

for i in range(len(dates) - 1):
    current_date = dates[i]
    next_date = dates[i+1]
    
    for ticker in tickers:
        #  decisão do modelo p este ticker nesta data
        row = df[(df['date'] == current_date) & (df['ticker_yf'] == ticker)]
        if row.empty: continue
        decision = row['raw_decision'].values[0].upper()
        
        # preços
        try:
            p_start = data.loc[current_date, ticker]
            p_end = data.loc[next_date, ticker]
            monthly_return = (p_end - p_start) / p_start
        except:
            continue
            
        # só ganha/perde se a decisão for BUY ou se estiver em HOLD após um BUY
        # (se a decisão for SELL, o dinheiro fica parado rendendo 0%)
        if "BUY" in decision or "HOLD" in decision:
            positions[ticker] *= (1 + monthly_return)
        elif "SELL" in decision:
            # dinheiro fica parado no valor atual (saiu da ação)
            pass

total_final = sum(positions.values())
roi_total = (total_final - initial_capital) / initial_capital * 100

print("-" * 30)
print(f"ROI Final (Qwen 3.5 35B): {roi_total:.2f}%")
print(f"Capital Final: R$ {total_final:,.2f}")
print("-" * 30)
