import hashlib
import json
import sqlite3
import os
from typing import Any, Dict, List, Optional
from dseek.llm.client import LLMResponse

class LLMCache:
    def __init__(self, db_path: str = "cache/llm_cache.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    response TEXT
                )
            ''')

    def _compute_key(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        tools: Optional[List[Dict[str, Any]]] = None,
        seed: Optional[int] = None
    ) -> str:
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": tools,
            "seed": seed
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def get(self, *args, **kwargs) -> Optional[LLMResponse]:
        key = self._compute_key(*args, **kwargs)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT response FROM cache WHERE key = ?", (key,))
            row = cur.fetchone()
            if row:
                data = json.loads(row[0])
                # Ensure the cache reports 0 cost/tokens to prevent double counting budgets
                data['tokens_in'] = 0
                data['tokens_out'] = 0
                data['estimated_cost'] = 0.0
                return LLMResponse(**data)
        return None

    def set(self, response: LLMResponse, *args, **kwargs):
        key = self._compute_key(*args, **kwargs)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, response) VALUES (?, ?)",
                (key, response.model_dump_json())
            )
