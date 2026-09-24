from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import abc

class LLMResponse(BaseModel):
    content: str
    tokens_in: int = 0
    tokens_out: int = 0
    estimated_cost: float = 0.0
    model: str
    metadata: Dict[str, Any] = {}

class LLMClient(abc.ABC):
    @abc.abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        tools: Optional[List[Dict[str, Any]]] = None,
        seed: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
