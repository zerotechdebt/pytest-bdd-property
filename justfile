set shell := ["bash", "-uc"]

# Show all available commands
default:
    @just --list

# Install dependencies and setup development environment
dev-install:
    uv sync --group dev

# Format code (auto-fix)
format:
    uv run ruff format .
    uv run ruff check --fix .

# Lint code (auto-fix, complexity threshold=10)
lint:
    uv run ruff check .

# Type check code
typecheck:
    uv run mypy pytest_bdd_property

# Run all tests
test:
    uv run pytest tests/ -v --durations=10

# Run tests in watch mode
test-watch:
    uv run pytest tests/ -v --tb=short -f

# Run tests with coverage threshold (96%)
coverage:
    uv run coverage run -m pytest tests/ --durations=10
    uv run coverage report --show-missing --fail-under=96

# Detailed complexity report for refactoring decisions
complexity:
    @uv run radon cc pytest_bdd_property/ -s -n B

# Show lines of code by file
loc:
    cloc pytest_bdd_property/ --by-file --quiet

# Show outdated packages
deps:
    uv pip list --outdated

# Check for security vulnerabilities
vulns:
    uv run pip-audit

# Analyze licenses
lic:
    @echo "Runtime dependencies:"
    @uv run pip-licenses --packages pytest pytest-bdd hypothesis --format=plain --order=license 2>/dev/null || echo "  (run 'just dev-install' first)"
    @echo ""
    @echo "All installed:"
    @uv run pip-licenses --format=plain --order=license --summary

# Generate software bill of materials
sbom:
    pnpm dlx @cyclonedx/cdxgen -o sbom.json

# Environment health check
doctor:
    @echo "Checking environment..."
    @python --version
    @uv --version
    @uv run ruff --version
    @uv run mypy --version
    @echo "All tools available."

# Build distribution
build:
    uv build

# Run tests, then verify specdrive gates (tests + audit + verify)
specdrive:
    uv run coverage run -m pytest tests/ -v --junitxml=test-results.xml --durations=10
    uv run coverage report --show-missing --fail-under=96
    pnpm exec specdrive audit
    pnpm exec specdrive verify test-results.xml

# Run all quality checks (format, lint, typecheck, specdrive - fastest first)
check-all: format lint typecheck specdrive
    @echo "All checks passed"

# Remove generated files and artifacts
clean:
    rm -rf .venv __pycache__ .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info .ruff_cache test-results.xml
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
