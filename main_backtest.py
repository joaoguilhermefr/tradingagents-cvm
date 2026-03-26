import pandas as pd
import json
import os
from datetime import datetime
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

STOCKS = ["ALUP11", "AURE3", "CPLE3", "EQTL3", "ENEV3"]
START_DATE = "2024-01-01"
END_DATE = "2025-12-01"
OUTPUT_FILE = "tradingagents_vs_iclr_results.csv"

simulation_dates = pd.date_range(start=START_DATE, end=END_DATE, freq="BMS")

def run_backtest():
    print("Iniciando Backtest: TradingAgents vs Arquitetura ICLR")
    print(f"Período: {START_DATE} a {END_DATE}")
    print(f"Ativos: {', '.join(STOCKS)}\n")

    ta = TradingAgentsGraph(config=DEFAULT_CONFIG)

    if os.path.exists(OUTPUT_FILE):
        results_df = pd.read_csv(OUTPUT_FILE)
        results = results_df.to_dict('records')
        print(f"Arquivo de resultados encontrado. Retomando com {len(results)} registros já processados.")
    else:
        results = []

    # cria um set de combinações já processadas para evitar retrabalho
    processed_combos = {f"{r['stock']}_{r['date']}" for r in results}

    for stock in STOCKS:
        print(f"\n{'='*40}\nAnalisando Ativo: {stock}\n{'='*40}")
        
        for current_date in simulation_dates:
            date_str = current_date.strftime("%Y-%m-%d")
            combo_key = f"{stock}_{date_str}"
            
            if combo_key in processed_combos:
                print(f"[{date_str}] Pulando {stock} (Já processado)")
                continue
                
            print(f"[{date_str}] Executando comitê de agentes para {stock}...")
            
            try:
                # propagate dispara o debate e retorna o estado final e a decisão
                _, decision = ta.propagate(stock, date_str)
                
                # geralmente é um pydantic model ou dict...
                decision_str = str(decision)
                
                new_record = {
                    "stock": stock,
                    "date": date_str,
                    "raw_decision": decision_str
                }
                results.append(new_record)
                
                pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
                print(f"[{date_str}] Concluído. Resultado salvo.")
                
            except Exception as e:
                print(f"[{date_str}] ERRO ao processar {stock}: {str(e)}")
                
                results.append({
                    "stock": stock,
                    "date": date_str,
                    "raw_decision": f"ERROR: {str(e)}"
                })
                pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)

    print("\nBacktest concluído! Resultados salvos em", OUTPUT_FILE)

if __name__ == "__main__":
    run_backtest()