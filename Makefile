.PHONY: test lint docs clean

test:
	./venv/bin/pytest

lint:
	./venv/bin/mypy src

docs:
	./venv/bin/mkdocs build

serve-docs:
	./venv/bin/mkdocs serve

clean:
	rm -rf htmlcov .coverage .pytest_cache .mypy_cache site dist build *.egg-info
