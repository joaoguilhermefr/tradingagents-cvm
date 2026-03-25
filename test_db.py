import sys
import os

# 1. Este comando diz ao Python: "Ei, considere a pasta atual como parte do projeto!"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. Agora sim ele vai encontrar o arquivo local_sqlite.py que você criou
from tradingagents.dataflows.local_sqlite import get_local_prices, get_local_fundamentals

print("=== TESTANDO DADOS TÉCNICOS (PREÇOS) ===")
resultado_precos = get_local_prices(ticker="ENEV3", start_date="2024-01-01", end_date="2024-01-31")
print(resultado_precos)
print("\n" + "="*50 + "\n")

print("=== TESTANDO DADOS FUNDAMENTALISTAS (BALANÇO/DRE) ===")
resultado_fundamentos = get_local_fundamentals(ticker="ENEV3", target_date="2024-01-01")
print(resultado_fundamentos)