import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Carrega a API Key do arquivo .env
load_dotenv()

# 1. Parâmetros do Experimento
STOCKS = ["ALUP11", "AURE3", "CPLE3", "EQTL3", "ENEV3"]
DB_PRICES_PATH = r"C:\projetos\workflow-vs-agent-fundamentals-br\data\prices.db"

# 2. Mapeamento: Nome do Artigo -> String real da API da OpenAI
# IMPORTANTE: Ajuste as strings da direita para os modelos reais que você decidir usar 
# como equivalentes para os modelos da sua pesquisa.
MODEL_MAPPING = {
    "gpt-4.1-nano": "gpt-3.5-turbo",  # Proxy sugerido para o 4.1-nano
    "gpt-4.1-mini": "gpt-4-turbo",    # Proxy sugerido para o 4.1-mini
    "gpt-5-nano": "gpt-4o-mini",      # Proxy sugerido para o 5-nano
    "gpt-5-mini": "gpt-4o"            # Proxy sugerido para o 5-mini
}

def get_master_calendar_dates():
    """Busca as datas exatas sincronizadas no banco de dados (A mesma lógica do seu FinMem)."""
    print("Sincronizando Calendário Mestre com a base de preços...")
    conn = sqlite3.connect(DB_PRICES_PATH)
    
    ticker_list = "'" + "','".join(STOCKS) + "'"
    query = f"SELECT DISTINCT DATA_DO_PREGAO as date FROM COTAHIST WHERE CODIGO_DE_NEGOCIACAO IN ({ticker_list})"
    
    df_dates = pd.read_sql(query, conn)
    conn.close()
    
    df_dates['date'] = pd.to_datetime(df_dates['date'])
    df_dates['year_month'] = df_dates['date'].dt.to_period('M')
    
    # Agrupa pelo mês e pega o primeiro dia válido em que a B3 abriu para esses ativos
    master_cal = df_dates.groupby('year_month')['date'].min().sort_values()
    
    # Filtra apenas o período da simulação (Jan/2024 a Dez/2025)
    backtest_dates = master_cal[(master_cal >= "2024-01-01") & (master_cal <= "2025-12-31")]
    
    datas_str = backtest_dates.dt.strftime("%Y-%m-%d").tolist()
    print(f"Calendário alinhado! {len(datas_str)} meses identificados para o backtest.")
    return datas_str

def run_multi_model_backtest():
    # Pega o calendário mestre
    simulation_dates = get_master_calendar_dates()
    
    # Trava a configuração base para a OpenAI
    DEFAULT_CONFIG["llm_provider"] = "openai"
    DEFAULT_CONFIG["backend_url"] = "https://api.openai.com/v1"

    # Loop pelos 4 modelos
    for academic_name, api_model_name in MODEL_MAPPING.items():
        print(f"\n{'='*50}")
        print(f"INICIANDO BATERIA: {academic_name} (Via API: {api_model_name})")
        print(f"{'='*50}")
        
        output_file = f"tradingagents_results_{academic_name.replace('.', '_')}.csv"
        
        # Atualiza o modelo no "cérebro" do TradingAgents para a rodada atual
        DEFAULT_CONFIG["quick_think_llm"] = api_model_name
        DEFAULT_CONFIG["deep_think_llm"] = api_model_name
        
        # Instancia o framework com a configuração atualizada
        ta = TradingAgentsGraph(config=DEFAULT_CONFIG)
        
        # Sistema de Checkpoint individual por modelo
        if os.path.exists(output_file):
            results_df = pd.read_csv(output_file)
            results = results_df.to_dict('records')
            print(f"Retomando {academic_name} com {len(results)} registros já processados.")
        else:
            results = []
            
        processed_combos = {f"{r['stock']}_{r['date']}" for r in results}

        # Executa o comitê
        for stock in STOCKS:
            print(f"\n--- Analisando: {stock} com {academic_name} ---")
            for date_str in simulation_dates:
                combo_key = f"{stock}_{date_str}"
                
                if combo_key in processed_combos:
                    print(f"[{date_str}] Pulando (Já processado)")
                    continue
                    
                print(f"[{date_str}] Agentes debatendo...")
                
                try:
                    _, decision = ta.propagate(stock, date_str)
                    
                    new_record = {
                        "stock": stock,
                        "date": date_str,
                        "raw_decision": str(decision)
                    }
                    results.append(new_record)
                    
                    # Salva no CSV específico do modelo
                    pd.DataFrame(results).to_csv(output_file, index=False)
                    print(f"[{date_str}] Concluído.")
                    
                except Exception as e:
                    print(f"[{date_str}] ERRO: {str(e)}")
                    results.append({
                        "stock": stock,
                        "date": date_str,
                        "raw_decision": f"ERROR: {str(e)}"
                    })
                    pd.DataFrame(results).to_csv(output_file, index=False)

if __name__ == "__main__":
    run_multi_model_backtest()