# Makefile cho sap-abap-agent - shortcut cac task thuong gap.
# Make dam bao cross-platform (tested voi GNU Make 4.x).
# Trong Windows, dung Git Bash hoac WSL; native NMAKE khong support.

PYTHON ?= python
PIP    ?= pip
RUFF   ?= ruff
PYTEST ?= pytest

.PHONY: help install lint format test test-collect coverage security validate \
        build sync-index pre-commit pre-commit-install clean version-check

help:                ## Hien thi help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:            ## Cai dev dependencies (ruff, pytest, pytest-cov)
	$(PIP) install ruff pytest pytest-cov build

lint:               ## Chay ruff lint
	$(RUFF) check .

format:             ## Auto-format code
	$(RUFF) format .

test:               ## Chay pytest that (root tests + hooks/hook_tests)
	$(PYTEST) tests/ hooks/hook_tests/ -q --no-header

test-collect:       ## Chi collect, khong run (smoke test)
	$(PYTEST) tests/ hooks/hook_tests/ reference/mcp-server/tests/ \
	  --collect-only -q --no-header -p no:cacheprovider

coverage:           ## Test + coverage report
	$(PIP) install pytest-cov
	$(PYTEST) tests/ hooks/hook_tests/ \
	  --cov=reference/scripts --cov=hooks \
	  --cov-report=term-missing:skip-covered \
	  --cov-fail-under=60 \
	  -q --no-header -p no:cacheprovider

security:           ## Chay security scan (custom + bandit)
	$(PYTHON) reference/scripts/security_scan.py
	$(PYTHON) reference/scripts/scan_clear_text_logging.py || true
	$(PIP) install bandit
	bandit -r reference/mcp-server/sap_btp_agent hooks reference/scripts \
	  --skip B101 --exclude '*/tests/*,*/__pycache__/*,*/build/*'

validate:           ## Chay validate_plugin.py (10 check)
	$(PYTHON) reference/scripts/validate_plugin.py

sync-index:         ## Build lai index.html (chay local nhu sync-index.yml)
	$(PYTHON) reference/scripts/build_index.py

build:              ## Build wheel cho MCP server
	cd reference/mcp-server && $(PIP) install build && python -m build --wheel

pre-commit:         ## Copy git hook built-in + install framework
	cp reference/scripts/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	$(PIP) install pre-commit
	pre-commit install

pre-commit-install: ## Chi cai pre-commit framework (Python-only, khong copy hook shell)
	$(PIP) install pre-commit
	pre-commit install

clean:              ## Xoa cache + artifacts
	rm -rf .pytest_cache/ __pycache__/ */__pycache__/ */*/__pycache__/
	rm -f index.head.tmp index.tail.tmp translations.tmp
	rm -rf reference/mcp-server/build/ reference/mcp-server/dist/

version-check:      ## Check version drift (CHANGELOG vs plugin.json)
	$(PYTHON) -c "import json; d=json.load(open('.claude-plugin/plugin.json',encoding='utf-8-sig')); print('plugin.json:', d['version'])"
	@head -10 CHANGELOG.md | grep -oP 'v\d+\.\d+\.\d+' | head -1 | xargs -I{} echo "CHANGELOG: {}"
