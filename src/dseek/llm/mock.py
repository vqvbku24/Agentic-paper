from typing import Any, Dict, List, Optional
from dseek.llm.client import LLMClient, LLMResponse

class MockLLM(LLMClient):
    def __init__(self, responses: Optional[Dict[str, str]] = None, default_cost: float = 0.01):
        self.responses = responses or {}
        self.default_cost = default_cost

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        tools: Optional[List[Dict[str, Any]]] = None,
        seed: Optional[int] = None
    ) -> LLMResponse:
        last_message = messages[-1]["content"] if messages else ""
        content = self.responses.get(last_message, f"Mocked response for: {last_message}")

        return LLMResponse(
            content=content,
            tokens_in=len(last_message.split()),
            tokens_out=len(content.split()),
            estimated_cost=self.default_cost,
            model=model,
            metadata={"mock": True}
        )
