import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "ollama", # Mudamos de openai para ollama
    "deep_think_llm": "llama3:70b", # Nome exato que vamos puxar amanhã
    "quick_think_llm": "llama3:70b",
    "backend_url": "http://localhost:11434", # Porta padrão onde o Ollama roda no servidor
    
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Nossas ferramentas locais sequestram isso
        "technical_indicators": "yfinance",  # Nossas ferramentas locais sequestram isso
        "fundamental_data": "yfinance",      # Nossas ferramentas locais sequestram isso
        "news_data": "yfinance",             # Nossas ferramentas locais sequestram isso
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
}