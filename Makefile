.PHONY: install install-dev lint format test test-cov clean run setup-pre-commit

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt

# Run linting
lint:
	ruff check pattern_mcp_server.py tests/
	mypy pattern_mcp_server.py

# Format code
format:
	black pattern_mcp_server.py tests/
	ruff check --fix pattern_mcp_server.py tests/

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=pattern_mcp_server --cov-report=html --cov-report=term

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .pytest_cache .ruff_cache .mypy_cache
	rm -rf build dist *.egg-info

# Run the MCP server
run:
	python pattern_mcp_server.py

# Set up pre-commit hooks
setup-pre-commit:
	pre-commit install
	pre-commit run --all-files

# Create virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

# Full development setup
setup: venv
	. venv/bin/activate && pip install -r requirements-dev.txt
	. venv/bin/activate && pre-commit install
	@echo "Development environment ready!"