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

# Read-only checks, same as check-all but without auto-fixing (used by GitHub CI)
ci:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy pytest_bdd_property
    just specdrive

# Tag the current version and push the tag; GitHub publishes it to PyPI (see RELEASING.md)
release:
    #!/usr/bin/env bash
    set -euo pipefail
    version=$(uv version --short)
    tag="v${version}"
    [ "$(git branch --show-current)" = "main" ] || { echo "Release from main"; exit 1; }
    [ -z "$(git status --porcelain)" ] || { echo "Working tree not clean"; exit 1; }
    git fetch -q origin main --tags
    [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "main is not in sync with origin/main"; exit 1; }
    grep -q "__version__ = \"${version}\"" pytest_bdd_property/__init__.py || { echo "__init__.py __version__ != ${version}"; exit 1; }
    grep -q "^## \[${version}\]" CHANGELOG.md || { echo "CHANGELOG.md has no entry for ${version}"; exit 1; }
    ! git rev-parse -q --verify "refs/tags/${tag}" >/dev/null || { echo "Tag ${tag} already exists"; exit 1; }
    just ci
    git tag -a "${tag}" -m "${tag}"
    git push origin "${tag}"
    echo "Pushed ${tag}. Watch: gh run watch \$(gh run list --workflow release.yml --limit 1 --json databaseId -q '.[0].databaseId')"

# Remove generated files and artifacts
clean:
    rm -rf .venv __pycache__ .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info .ruff_cache test-results.xml
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
