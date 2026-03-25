import openai # O Ollama usa a interface da OpenAI

client = openai.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# Simulando a definição da ferramenta de preço que você vai usar
tools = [{
    "type": "function",
    "function": {
        "name": "get_stock_price",
        "description": "Busca o preço de uma ação brasileira no prices.db",
        "parameters": {
            "type": "object",
            "properties": { "ticker": {"type": "string"} },
            "required": ["ticker"]
        }
    }
}]

response = client.chat.completions.create(
    model="llama3.1",
    messages=[{"role": "user", "content": "Qual o preço atual da ENEV3?"}],
    tools=tools
)

# Se o Llama 3.1 estiver funcionando, ele retornará uma chamada de ferramenta aqui
if response.choices[0].message.tool_calls:
    print("✅ Sucesso! O Llama 3.1 identificou a necessidade de consultar seu banco de dados.")
    print(f"Chamada detectada: {response.choices[0].message.tool_calls[0].function.name}")
else:
    print("❌ Falha: O modelo não tentou usar a ferramenta.")