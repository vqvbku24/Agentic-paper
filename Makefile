.PHONY: test lint

test:
	pytest tests/

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/
