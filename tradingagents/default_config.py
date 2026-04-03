import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    
    "llm_provider": "openai", 
    "deep_think_llm": "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4", 
    "quick_think_llm": "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4",
    "backend_url": "http://localhost:8000/v1", 
    
    "google_thinking_level": None,
    "openai_reasoning_effort": None,
    
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    
    "data_vendors": {
        "core_stock_apis": "yfinance",       
        "technical_indicators": "yfinance",  
        "fundamental_data": "yfinance",      
        "news_data": "yfinance",             
    },
    "tool_vendors": {},
}