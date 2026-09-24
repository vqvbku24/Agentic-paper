class BudgetExceeded(Exception):
    """Raised when the LLM budget is exceeded."""
    pass

class BudgetTracker:
    def __init__(self, limit_usd: float):
        self.limit_usd = limit_usd
        self.current_spend = 0.0

    def add_spend(self, amount: float):
        self.current_spend += amount
        if self.current_spend > self.limit_usd:
            raise BudgetExceeded(f"Budget exceeded! Spent: {self.current_spend:.4f}, Limit: {self.limit_usd:.4f}")
