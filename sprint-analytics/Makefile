.PHONY: help setup install clean run dry-run refresh cache test lint format check-env venv

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python
MAIN_SCRIPT := gather_sprint_metrics.py

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

help: ## Show this help message
	@echo "$(COLOR_BOLD)Sprint Analytics Makefile$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)Available targets:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_BLUE)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_YELLOW)Examples:$(COLOR_RESET)"
	@echo "  make setup          # First-time setup"
	@echo "  make dry-run        # Test with sample data"
	@echo "  make run            # Run with real ClickUp data"
	@echo "  make refresh        # Force refresh from API"
	@echo "  make clean          # Clean generated files"

setup: venv install check-env ## Complete first-time setup (venv + install + check)
	@echo "$(COLOR_GREEN)✓ Setup complete!$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Next steps:$(COLOR_RESET)"
	@echo "  1. Edit .env and add your CLICKUP_API_TOKEN"
	@echo "  2. Run: make dry-run (test with sample data)"
	@echo "  3. Run: make run (fetch real data)"

venv: ## Create virtual environment
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(COLOR_BLUE)Creating virtual environment...$(COLOR_RESET)"; \
		$(PYTHON) -m venv $(VENV); \
		echo "$(COLOR_GREEN)✓ Virtual environment created$(COLOR_RESET)"; \
	else \
		echo "$(COLOR_YELLOW)Virtual environment already exists$(COLOR_RESET)"; \
	fi

install: venv ## Install Python dependencies
	@echo "$(COLOR_BLUE)Installing dependencies...$(COLOR_RESET)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "$(COLOR_GREEN)✓ Dependencies installed$(COLOR_RESET)"

check-env: ## Check if .env file exists and has API token
	@if [ ! -f .env ]; then \
		echo "$(COLOR_YELLOW)⚠ .env file not found$(COLOR_RESET)"; \
		echo "  Creating from .env.example..."; \
		cp .env.example .env; \
		echo "$(COLOR_YELLOW)  Please edit .env and add your CLICKUP_API_TOKEN$(COLOR_RESET)"; \
	else \
		if ! grep -q "CLICKUP_API_TOKEN=pk_" .env 2>/dev/null; then \
			echo "$(COLOR_YELLOW)⚠ CLICKUP_API_TOKEN not configured in .env$(COLOR_RESET)"; \
			echo "  Please edit .env and add your API token"; \
		else \
			echo "$(COLOR_GREEN)✓ .env file configured$(COLOR_RESET)"; \
		fi \
	fi

run: venv ## Run sprint analytics with real ClickUp data
	@echo "$(COLOR_BLUE)Running sprint analytics...$(COLOR_RESET)"
	@$(PYTHON_VENV) $(MAIN_SCRIPT) --verbose

dry-run: venv ## Test run with sample data (no API calls)
	@echo "$(COLOR_BLUE)Running dry-run with sample data...$(COLOR_RESET)"
	@$(PYTHON_VENV) $(MAIN_SCRIPT) --dry-run --verbose

refresh: venv ## Force refresh all data from ClickUp API (ignore cache)
	@echo "$(COLOR_BLUE)Refreshing data from API...$(COLOR_RESET)"
	@$(PYTHON_VENV) $(MAIN_SCRIPT) --refresh --verbose

cache: venv ## Use only cached data (no API calls)
	@echo "$(COLOR_BLUE)Running with cached data only...$(COLOR_RESET)"
	@$(PYTHON_VENV) $(MAIN_SCRIPT) --cache --verbose

sprint: venv ## Run specific sprints (usage: make sprint SPRINTS="43 44 45")
	@if [ -z "$(SPRINTS)" ]; then \
		echo "$(COLOR_YELLOW)Usage: make sprint SPRINTS=\"43 44 45\"$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_BLUE)Running sprints: $(SPRINTS)$(COLOR_RESET)"
	@$(PYTHON_VENV) $(MAIN_SCRIPT) --sprints $(SPRINTS) --verbose

clean: ## Clean generated files and cache
	@echo "$(COLOR_BLUE)Cleaning generated files...$(COLOR_RESET)"
	@rm -rf output/*.png output/*.json output/*.csv output/*.md
	@rm -rf data/cache/*.json
	@echo "$(COLOR_GREEN)✓ Cleaned output and cache files$(COLOR_RESET)"

clean-all: clean ## Clean everything including venv
	@echo "$(COLOR_BLUE)Cleaning virtual environment...$(COLOR_RESET)"
	@rm -rf $(VENV)
	@rm -rf __pycache__ src/__pycache__
	@rm -rf *.pyc src/*.pyc
	@echo "$(COLOR_GREEN)✓ Cleaned everything$(COLOR_RESET)"

lint: venv ## Run code linting (requires flake8)
	@if $(PIP) show flake8 > /dev/null 2>&1; then \
		echo "$(COLOR_BLUE)Running linter...$(COLOR_RESET)"; \
		$(VENV_BIN)/flake8 src/ $(MAIN_SCRIPT) --max-line-length=100 --ignore=E501,W503; \
	else \
		echo "$(COLOR_YELLOW)flake8 not installed. Run: make install-dev$(COLOR_RESET)"; \
	fi

format: venv ## Format code with black (requires black)
	@if $(PIP) show black > /dev/null 2>&1; then \
		echo "$(COLOR_BLUE)Formatting code...$(COLOR_RESET)"; \
		$(VENV_BIN)/black src/ $(MAIN_SCRIPT) --line-length=100; \
	else \
		echo "$(COLOR_YELLOW)black not installed. Run: make install-dev$(COLOR_RESET)"; \
	fi

install-dev: venv ## Install development dependencies
	@echo "$(COLOR_BLUE)Installing dev dependencies...$(COLOR_RESET)"
	@$(PIP) install black flake8 pytest
	@echo "$(COLOR_GREEN)✓ Dev dependencies installed$(COLOR_RESET)"

test: venv ## Run tests (requires pytest)
	@if $(PIP) show pytest > /dev/null 2>&1; then \
		echo "$(COLOR_BLUE)Running tests...$(COLOR_RESET)"; \
		$(VENV_BIN)/pytest tests/ -v; \
	else \
		echo "$(COLOR_YELLOW)pytest not installed. Run: make install-dev$(COLOR_RESET)"; \
	fi

show-config: ## Show current configuration
	@echo "$(COLOR_BOLD)Sprint Analytics Configuration$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BLUE)Environment:$(COLOR_RESET)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Venv: $(VENV)"
	@echo "  API Token: $(shell grep CLICKUP_API_TOKEN .env 2>/dev/null | sed 's/CLICKUP_API_TOKEN=pk_[^_]*/CLICKUP_API_TOKEN=pk_***/' || echo 'Not configured')"
	@echo ""
	@echo "$(COLOR_BLUE)Configured Sprints:$(COLOR_RESET)"
	@$(PYTHON_VENV) -c "import yaml; config = yaml.safe_load(open('config.yaml')); [print(f\"  Sprint {s['sprint_number']}: {s['name']} (Week {s['week']})\") for s in config['sprints']]" 2>/dev/null || echo "  (config.yaml not readable)"

show-output: ## Show generated output files
	@echo "$(COLOR_BOLD)Generated Output Files$(COLOR_RESET)"
	@echo ""
	@ls -lh output/*.png output/*.json output/*.csv output/*.md 2>/dev/null | awk '{print "  " $$9 " (" $$5 ")"}' || echo "  No output files found. Run: make dry-run"

open-charts: ## Open generated charts in default viewer
	@if [ -f output/sprint_velocity_chart.png ]; then \
		echo "$(COLOR_BLUE)Opening charts...$(COLOR_RESET)"; \
		open output/sprint_velocity_chart.png; \
		open output/sprint_burndown_chart.png; \
		open output/sprint_delivery_rate_chart.png; \
	else \
		echo "$(COLOR_YELLOW)No charts found. Run: make dry-run or make run$(COLOR_RESET)"; \
	fi

open-report: ## Open markdown report in default viewer
	@if [ -f output/sprint_summary.md ]; then \
		echo "$(COLOR_BLUE)Opening report...$(COLOR_RESET)"; \
		open output/sprint_summary.md; \
	else \
		echo "$(COLOR_YELLOW)No report found. Run: make dry-run or make run$(COLOR_RESET)"; \
	fi

shell: venv ## Activate virtual environment shell
	@echo "$(COLOR_BLUE)Activating virtual environment...$(COLOR_RESET)"
	@echo "Run: source $(VENV_BIN)/activate"
	@$(SHELL) -c "source $(VENV_BIN)/activate && exec $(SHELL)"

info: ## Show project information
	@echo "$(COLOR_BOLD)Sprint Analytics Project$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BLUE)Description:$(COLOR_RESET)"
	@echo "  ClickUp sprint metrics analysis for H2 2025 (Sprint 43-50)"
	@echo ""
	@echo "$(COLOR_BLUE)Features:$(COLOR_RESET)"
	@echo "  • Automated data collection from ClickUp API"
	@echo "  • Intelligent carryover detection"
	@echo "  • High-quality PNG charts (300 DPI)"
	@echo "  • JSON, CSV, and Markdown reports"
	@echo "  • Caching and rate limiting"
	@echo ""
	@echo "$(COLOR_BLUE)Documentation:$(COLOR_RESET)"
	@echo "  • README.md - Complete documentation"
	@echo "  • config.yaml - Sprint configuration"
	@echo "  • .env - Environment variables"
	@echo ""
	@echo "$(COLOR_BLUE)Quick Start:$(COLOR_RESET)"
	@echo "  1. make setup"
	@echo "  2. Edit .env with your CLICKUP_API_TOKEN"
	@echo "  3. make dry-run"
	@echo "  4. make run"
