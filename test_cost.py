import os
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from dotenv import load_dotenv

load_dotenv()

def test_single_run():
    print("=== TESTE DE CUSTO: GPT-4.1-NANO ===")
    
    # Inicializa o grafo com a config da OpenAI
    ta = TradingAgentsGraph(config=DEFAULT_CONFIG)
    
    ticker = "ALUP11"
    date = "2024-01-02" # Primeiro dia útil de Jan/2024
    
    print(f"Processando {ticker} em {date}...")
    
    try:
        # Executa a simulação completa (Debate + Decisão)
        state, decision = ta.propagate(ticker, date)
        
        print("\n" + "="*30)
        print(f"DECISÃO FINAL: {decision}")
        print("="*30)
        print("\nTeste concluído com sucesso!")
        print("Verifique o consumo de tokens no dashboard da OpenAI.")
        
    except Exception as e:
        print(f"Erro na execução: {e}")

if __name__ == "__main__":
    test_single_run()