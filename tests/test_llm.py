import os
import pytest
import tempfile
from dseek.llm.mock import MockLLM
from dseek.llm.budget import BudgetTracker, BudgetExceeded
from dseek.llm.cache import LLMCache
from dseek.llm.client import LLMResponse

def test_mock_llm():
    mock_llm = MockLLM(responses={"Hello": "Hi there!"}, default_cost=0.01)
    response = mock_llm.complete(messages=[{"role": "user", "content": "Hello"}], model="test-model")

    assert response.content == "Hi there!"
    assert response.estimated_cost == 0.01
    assert response.metadata.get("mock") is True

def test_budget_guard():
    tracker = BudgetTracker(limit_usd=1.0)
    tracker.add_spend(0.5)
    assert tracker.current_spend == 0.5

    with pytest.raises(BudgetExceeded):
        tracker.add_spend(0.6)

def test_llm_cache():
    with tempfile.TemporaryDirectory() as tmpdirname:
        db_path = os.path.join(tmpdirname, "test_cache.db")
        cache = LLMCache(db_path=db_path)

        messages = [{"role": "user", "content": "Test prompt"}]
        model = "test-model"

        # Initial fetch should be None
        cached_resp = cache.get(messages=messages, model=model, temperature=0.0, max_tokens=100)
        assert cached_resp is None

        # Set a response in the cache
        original_response = LLMResponse(
            content="Generated answer",
            tokens_in=10,
            tokens_out=20,
            estimated_cost=0.05,
            model=model,
            metadata={"source": "api"}
        )
        cache.set(original_response, messages=messages, model=model, temperature=0.0, max_tokens=100)

        # Second fetch should return the cached response, with 0 cost and tokens
        cached_resp = cache.get(messages=messages, model=model, temperature=0.0, max_tokens=100)
        assert cached_resp is not None
        assert cached_resp.content == "Generated answer"
        assert cached_resp.estimated_cost == 0.0
        assert cached_resp.tokens_in == 0
        assert cached_resp.tokens_out == 0
        assert cached_resp.metadata.get("source") == "api"
