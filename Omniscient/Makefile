.PHONY: help setup install test clean run report json csv markdown all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
VENV := venv
MAIN_SCRIPT := gather_okr_metrics.py
TEST_SCRIPT := test_connection.py

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(CYAN)Omniscient OKR Analytics - Makefile Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Initial setup (create .env, install dependencies)
	@echo "$(CYAN)Setting up Omniscient OKR Analytics...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from template...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file$(NC)"; \
		echo "$(RED)⚠️  IMPORTANT: Edit .env and add your MySQL credentials$(NC)"; \
	else \
		echo "$(GREEN)✓ .env file already exists$(NC)"; \
	fi
	@echo "$(CYAN)Installing dependencies...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env with your MySQL credentials"
	@echo "  2. Run: make test"
	@echo "  3. Run: make run"

install: ## Install Python dependencies
	@echo "$(CYAN)Installing dependencies...$(NC)"
	@$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

test: ## Test database connection
	@echo "$(CYAN)Testing database connection...$(NC)"
	@$(PYTHON) $(TEST_SCRIPT)

clean: ## Clean generated files and caches
	@echo "$(CYAN)Cleaning generated files...$(NC)"
	@rm -rf output/*.png output/*.json output/*.csv
	@rm -rf reports/*.md
	@rm -rf data/*.json data/*.csv
	@rm -rf __pycache__ src/__pycache__
	@rm -rf *.pyc src/*.pyc
	@rm -rf $(VENV)
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: ## Delete ALL reports and outputs (including subdirectories)
	@echo "$(RED)⚠️  This will delete ALL generated reports and outputs!$(NC)"
	@echo "$(YELLOW)Files to be deleted:$(NC)"
	@find output -type f 2>/dev/null | wc -l | xargs echo "  • output/   :" "files"
	@find reports -type f 2>/dev/null | wc -l | xargs echo "  • reports/  :" "files"
	@find data -type f 2>/dev/null | wc -l | xargs echo "  • data/     :" "files"
	@echo ""
	@read -p "Are you sure? (y/N): " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(CYAN)Deleting all files...$(NC)"; \
		rm -rf output/*; \
		rm -rf reports/*; \
		rm -rf data/*; \
		rm -rf __pycache__ src/__pycache__; \
		rm -rf *.pyc src/*.pyc; \
		echo "$(GREEN)✓ All reports and outputs deleted$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled - no files deleted$(NC)"; \
	fi

run: ## Run full OKR report generation (all formats + charts)
	@echo "$(CYAN)Generating OKR report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT)

report: run ## Alias for 'make run'

json: ## Generate JSON report only
	@echo "$(CYAN)Generating JSON report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --format json --no-charts

csv: ## Generate CSV report only
	@echo "$(CYAN)Generating CSV report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --format csv --no-charts

markdown: ## Generate Markdown report only
	@echo "$(CYAN)Generating Markdown report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --format markdown --no-charts

all: ## Generate all reports and charts
	@echo "$(CYAN)Generating all reports and charts...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --format all

quick: ## Quick report (JSON only, no charts)
	@echo "$(CYAN)Generating quick report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --format json --no-charts

# Date range targets
ytd: ## Generate Year-To-Date report
	@echo "$(CYAN)Generating Year-To-Date report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-01-01

q1: ## Generate Q1 report (Jan-Mar)
	@echo "$(CYAN)Generating Q1 report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-01-01 --end-date $$(date +%Y)-03-31

q2: ## Generate Q2 report (Apr-Jun)
	@echo "$(CYAN)Generating Q2 report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-04-01 --end-date $$(date +%Y)-06-30

q3: ## Generate Q3 report (Jul-Sep)
	@echo "$(CYAN)Generating Q3 report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-07-01 --end-date $$(date +%Y)-09-30

q4: ## Generate Q4 report (Oct-Dec)
	@echo "$(CYAN)Generating Q4 report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-10-01 --end-date $$(date +%Y)-12-31

h1: ## Generate H1 report (Jan-Jun)
	@echo "$(CYAN)Generating H1 report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-01-01 --end-date $$(date +%Y)-06-30

h2: ## Generate H2 report (Jul-Dec)
	@echo "$(CYAN)Generating H2 report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y)-07-01 --end-date $$(date +%Y)-12-31

last-month: ## Generate last month report
	@echo "$(CYAN)Generating last month report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date -v-1m +%Y-%m-01) --end-date $$(date -v-1m +%Y-%m-31)

this-month: ## Generate current month report
	@echo "$(CYAN)Generating current month report...$(NC)"
	@$(PYTHON) $(MAIN_SCRIPT) --start-date $$(date +%Y-%m-01)

# View targets
view-report: ## Open the generated Markdown report
	@if [ -f reports/okr_report.md ]; then \
		open reports/okr_report.md || cat reports/okr_report.md; \
	else \
		echo "$(RED)No report found. Run 'make run' first.$(NC)"; \
	fi

view-charts: ## Open all generated charts
	@if [ -f output/pr_quality_trend.png ]; then \
		open output/*.png 2>/dev/null || echo "$(YELLOW)Charts generated but could not open.$(NC)"; \
	else \
		echo "$(RED)No charts found. Run 'make run' first.$(NC)"; \
	fi

view-json: ## Display JSON metrics
	@if [ -f output/okr_metrics.json ]; then \
		cat output/okr_metrics.json | $(PYTHON) -m json.tool; \
	else \
		echo "$(RED)No JSON found. Run 'make json' first.$(NC)"; \
	fi

# Utility targets
check-env: ## Check if .env file exists and is configured
	@if [ ! -f .env ]; then \
		echo "$(RED)✗ .env file not found$(NC)"; \
		echo "$(YELLOW)Run 'make setup' to create it$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✓ .env file exists$(NC)"; \
		if grep -q "your_db_user" .env; then \
			echo "$(RED)⚠️  .env file needs to be configured$(NC)"; \
			echo "$(YELLOW)Edit .env and add your MySQL credentials$(NC)"; \
		else \
			echo "$(GREEN)✓ .env appears to be configured$(NC)"; \
		fi \
	fi

lint: ## Run Python linter (if available)
	@command -v pylint >/dev/null 2>&1 && pylint src/*.py $(MAIN_SCRIPT) $(TEST_SCRIPT) || echo "$(YELLOW)pylint not installed$(NC)"

format: ## Format Python code (if black is available)
	@command -v black >/dev/null 2>&1 && black src/ $(MAIN_SCRIPT) $(TEST_SCRIPT) || echo "$(YELLOW)black not installed$(NC)"

deps: ## Show dependency tree
	@$(PIP) list | grep -E "pymysql|pandas|matplotlib|seaborn|tabulate|python-dotenv"

info: ## Show project information
	@echo "$(CYAN)Project Information$(NC)"
	@echo "$(GREEN)==================$(NC)"
	@echo "Project: Omniscient OKR Analytics"
	@echo "Main Script: $(MAIN_SCRIPT)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo ""
	@echo "$(CYAN)Directory Structure:$(NC)"
	@tree -L 2 -I '__pycache__|*.pyc' || find . -maxdepth 2 -type d
	@echo ""
	@echo "$(CYAN)Generated Files:$(NC)"
	@ls -lh output/ 2>/dev/null | tail -n +2 || echo "No files in output/"
	@ls -lh reports/ 2>/dev/null | tail -n +2 || echo "No files in reports/"

venv: ## Create virtual environment
	@echo "$(CYAN)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"
	@echo ""
	@echo "To activate:"
	@echo "  source $(VENV)/bin/activate"

# Combined workflows
first-run: setup test run view-report ## Complete first-time setup and run
	@echo "$(GREEN)First run complete!$(NC)"

daily: test quick ## Quick daily report generation
	@echo "$(GREEN)Daily report generated!$(NC)"

weekly: test run view-report ## Weekly full report with charts
	@echo "$(GREEN)Weekly report generated!$(NC)"

monthly: test this-month run view-report ## Monthly report for current month
	@echo "$(GREEN)Monthly report generated!$(NC)"

# User-specific report (edit GITHUB_USER variable or use GITHUB_USER=name in command)
GITHUB_USER ?= adon-paper
END_DATE ?= $(shell date +%Y-%m-%d)

my-report: ## Generate report for GITHUB_USER (all data up to today)
	@echo "$(CYAN)Generating report for $(GITHUB_USER) (all data to $(END_DATE))...$(NC)"
	@$(PYTHON) generate_user_report.py --user $(GITHUB_USER) --end-date $(END_DATE)

my-h2: ## Generate H2 2025 report for GITHUB_USER
	@echo "$(CYAN)Generating H2 2025 report for $(GITHUB_USER)...$(NC)"
	@$(PYTHON) generate_user_report.py --user $(GITHUB_USER) --period H2-2025

my-q4: ## Generate Q4 2025 report for GITHUB_USER
	@echo "$(CYAN)Generating Q4 2025 report for $(GITHUB_USER)...$(NC)"
	@$(PYTHON) generate_user_report.py --user $(GITHUB_USER) --period Q4-2025

my-ytd: ## Generate YTD report for GITHUB_USER
	@echo "$(CYAN)Generating YTD report for $(GITHUB_USER)...$(NC)"
	@$(PYTHON) generate_user_report.py --user $(GITHUB_USER) --period YTD

# Legacy commands (kept for compatibility)
user-h2: my-h2 ## Alias for my-h2
user-q3: ## Generate Q3 2025 report for GITHUB_USER
	@echo "$(CYAN)Generating Q3 2025 report for $(GITHUB_USER)...$(NC)"
	@$(PYTHON) generate_user_report.py --user $(GITHUB_USER) --period Q3-2025

user-ytd: my-ytd ## Alias for my-ytd
