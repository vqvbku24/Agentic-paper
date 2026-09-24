"""Configuration for dseek."""

import os

class Config:
    def __init__(self):
        self.llm_budget_usd = float(os.getenv("LLM_BUDGET_USD", "50"))
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

config = Config()
