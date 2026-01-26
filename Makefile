.PHONY: help all sprint-analytics omniscient sonarqube mttr clean clean-all view-all view-sprint view-omniscient view-sonarqube view-mttr info

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m # No Color

# Directories
SPRINT_DIR := sprint-analytics
OMNISCIENT_DIR := Omniscient
SONARQUBE_DIR := sonarqube-analytics
MTTR_DIR := MTTR

help: ## Show this help message
	@echo "$(BOLD)$(CYAN)Adon's OKR & Sprint Analytics - Master Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make all                  # Generate all automated reports"
	@echo "  make sprint-analytics     # Generate sprint analytics only"
	@echo "  make omniscient           # Generate Omniscient OKR reports"
	@echo "  make view-all             # Open all reports"
	@echo ""
	@echo "$(YELLOW)Note:$(NC)"
	@echo "  • SonarQube reports are generated manually via MCP"
	@echo "  • MTTR reports are exported from Metabase dashboard"
	@echo ""

all: ## Generate all automated reports (sprint-analytics + omniscient)
	@echo "$(BOLD)$(CYAN)Generating all reports...$(NC)"
	@echo ""
	@$(MAKE) sprint-analytics
	@echo ""
	@$(MAKE) omniscient
	@echo ""
	@echo "$(GREEN)✓ All reports generated successfully!$(NC)"
	@echo ""
	@$(MAKE) info

sprint-analytics: ## Generate sprint analytics reports
	@echo "$(CYAN)Generating Sprint Analytics...$(NC)"
	@cd $(SPRINT_DIR) && $(MAKE) run
	@echo "$(GREEN)✓ Sprint analytics complete$(NC)"

omniscient: ## Generate Omniscient OKR reports (adon-paper)
	@echo "$(CYAN)Generating Omniscient OKR reports...$(NC)"
	@cd $(OMNISCIENT_DIR) && $(MAKE) my-report
	@echo "$(GREEN)✓ Omniscient reports complete$(NC)"

omniscient-h2: ## Generate Omniscient H2 2025 report
	@echo "$(CYAN)Generating Omniscient H2 2025 report...$(NC)"
	@cd $(OMNISCIENT_DIR) && $(MAKE) my-h2
	@echo "$(GREEN)✓ Omniscient H2 report complete$(NC)"

omniscient-q4: ## Generate Omniscient Q4 2025 report
	@echo "$(CYAN)Generating Omniscient Q4 2025 report...$(NC)"
	@cd $(OMNISCIENT_DIR) && $(MAKE) my-q4
	@echo "$(GREEN)✓ Omniscient Q4 report complete$(NC)"

sonarqube: ## Note: SonarQube reports are manual (via MCP)
	@echo "$(YELLOW)⚠️  SonarQube Analytics$(NC)"
	@echo ""
	@echo "SonarQube reports are generated manually using the MCP SonarQube integration."
	@echo ""
	@echo "$(CYAN)Current reports:$(NC)"
	@ls -lh $(SONARQUBE_DIR)/reports/*.md 2>/dev/null | awk '{print "  • " $$9 " (" $$5 ")"}' || echo "  (No reports found)"
	@echo ""
	@echo "$(CYAN)To regenerate manually:$(NC)"
	@echo "  1. Use Claude Code with SonarQube MCP"
	@echo "  2. Query projects: paper-payment-backend, paper-document"
	@echo "  3. Update reports in $(SONARQUBE_DIR)/reports/"
	@echo ""

mttr: ## Note: MTTR reports are from Metabase
	@echo "$(YELLOW)⚠️  MTTR Performance Reports$(NC)"
	@echo ""
	@echo "MTTR reports are exported from the Metabase dashboard."
	@echo ""
	@echo "$(CYAN)Current data:$(NC)"
	@if [ -f "$(MTTR_DIR)/mttr_metrics.csv" ]; then \
		wc -l $(MTTR_DIR)/mttr_metrics.csv | awk '{print "  • " $$2 ": " $$1 " lines"}'; \
	else \
		echo "  (No data found)"; \
	fi
	@echo ""
	@echo "$(CYAN)Dashboard:$(NC)"
	@echo "  https://paperspark.paper.id/dashboard/3541-bug-issue-monitoring-dwh-ver"
	@echo ""

clean: ## Clean generated reports (sprint-analytics + omniscient)
	@echo "$(CYAN)Cleaning generated reports...$(NC)"
	@cd $(SPRINT_DIR) && $(MAKE) clean
	@cd $(OMNISCIENT_DIR) && $(MAKE) clean
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: ## Clean all generated files including caches
	@echo "$(RED)⚠️  This will delete all generated reports and caches!$(NC)"
	@read -p "Are you sure? (y/N): " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(CYAN)Cleaning all...$(NC)"; \
		cd $(SPRINT_DIR) && $(MAKE) clean; \
		cd ../$(OMNISCIENT_DIR) && $(MAKE) clean; \
		echo "$(GREEN)✓ All cleaned$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

view-all: view-sprint view-omniscient ## Open all available reports
	@echo "$(GREEN)✓ Opened all reports$(NC)"

view-sprint: ## Open sprint analytics reports
	@echo "$(CYAN)Opening Sprint Analytics reports...$(NC)"
	@if [ -f "$(SPRINT_DIR)/output/sprint_summary.md" ]; then \
		open $(SPRINT_DIR)/output/sprint_summary.md || cat $(SPRINT_DIR)/output/sprint_summary.md; \
	else \
		echo "$(YELLOW)No sprint report found. Run: make sprint-analytics$(NC)"; \
	fi

view-omniscient: ## Open Omniscient OKR reports
	@echo "$(CYAN)Opening Omniscient reports...$(NC)"
	@REPORT=$$(find $(OMNISCIENT_DIR)/reports -name "okr_report.md" -type f | head -1); \
	if [ -n "$$REPORT" ]; then \
		open "$$REPORT" || cat "$$REPORT"; \
	else \
		echo "$(YELLOW)No Omniscient report found. Run: make omniscient$(NC)"; \
	fi

view-sonarqube: ## Open SonarQube reports
	@echo "$(CYAN)Opening SonarQube reports...$(NC)"
	@if [ -f "$(SONARQUBE_DIR)/reports/README.md" ]; then \
		open $(SONARQUBE_DIR)/reports/README.md || cat $(SONARQUBE_DIR)/reports/README.md; \
	else \
		echo "$(YELLOW)No SonarQube report found$(NC)"; \
	fi

view-mttr: ## Open MTTR reports
	@echo "$(CYAN)Opening MTTR reports...$(NC)"
	@if [ -f "$(MTTR_DIR)/README.md" ]; then \
		open $(MTTR_DIR)/README.md || cat $(MTTR_DIR)/README.md; \
	else \
		echo "$(YELLOW)No MTTR report found$(NC)"; \
	fi

view-charts: ## Open all generated charts
	@echo "$(CYAN)Opening all charts...$(NC)"
	@find $(SPRINT_DIR)/output -name "*.png" -exec open {} \; 2>/dev/null || true
	@find $(OMNISCIENT_DIR)/output -name "*.png" -exec open {} \; 2>/dev/null || true
	@echo "$(GREEN)✓ Charts opened$(NC)"

info: ## Show summary of all reports
	@echo ""
	@echo "$(BOLD)$(CYAN)Report Generation Summary$(NC)"
	@echo "$(CYAN)═══════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)📊 Sprint Analytics$(NC)"
	@if [ -f "$(SPRINT_DIR)/output/sprint_summary.md" ]; then \
		echo "  ✓ Report: $(SPRINT_DIR)/output/sprint_summary.md"; \
		echo "  ✓ Charts: $$(find $(SPRINT_DIR)/output -name "*.png" 2>/dev/null | wc -l | xargs) files"; \
		echo "  ✓ Data: $$(find $(SPRINT_DIR)/output -name "*.json" -o -name "*.csv" 2>/dev/null | wc -l | xargs) files"; \
	else \
		echo "  ⚠️  No reports found - run: make sprint-analytics"; \
	fi
	@echo ""
	@echo "$(GREEN)🎯 Omniscient OKR Analytics$(NC)"
	@if [ -d "$(OMNISCIENT_DIR)/reports" ] && [ -n "$$(find $(OMNISCIENT_DIR)/reports -name '*.md' 2>/dev/null)" ]; then \
		echo "  ✓ Reports: $$(find $(OMNISCIENT_DIR)/reports -name "*.md" 2>/dev/null | wc -l | xargs) files"; \
		echo "  ✓ Charts: $$(find $(OMNISCIENT_DIR)/output -name "*.png" 2>/dev/null | wc -l | xargs) files"; \
		echo "  ✓ Data: $$(find $(OMNISCIENT_DIR)/output -name "*.json" -o -name "*.csv" 2>/dev/null | wc -l | xargs) files"; \
	else \
		echo "  ⚠️  No reports found - run: make omniscient"; \
	fi
	@echo ""
	@echo "$(GREEN)🔍 SonarQube Analytics$(NC)"
	@if [ -f "$(SONARQUBE_DIR)/reports/README.md" ]; then \
		echo "  ✓ Report: $(SONARQUBE_DIR)/reports/README.md"; \
		echo "  ℹ️  Generated manually via MCP"; \
	else \
		echo "  ⚠️  No reports found"; \
	fi
	@echo ""
	@echo "$(GREEN)⏱️  MTTR Performance$(NC)"
	@if [ -f "$(MTTR_DIR)/README.md" ]; then \
		echo "  ✓ Report: $(MTTR_DIR)/README.md"; \
		echo "  ✓ Data: $(MTTR_DIR)/mttr_metrics.csv"; \
		echo "  ℹ️  Exported from Metabase"; \
	else \
		echo "  ⚠️  No reports found"; \
	fi
	@echo ""
	@echo "$(CYAN)═══════════════════════════════════════════════$(NC)"
	@echo "$(YELLOW)Quick Links:$(NC)"
	@echo "  • Sprint Summary:    ./$(SPRINT_DIR)/output/sprint_summary.md"
	@echo "  • OKR Report:        ./$(OMNISCIENT_DIR)/reports/*/okr_report.md"
	@echo "  • SonarQube Report:  ./$(SONARQUBE_DIR)/reports/README.md"
	@echo "  • MTTR Report:       ./$(MTTR_DIR)/README.md"
	@echo ""

setup: ## Setup all projects (install dependencies)
	@echo "$(BOLD)$(CYAN)Setting up all projects...$(NC)"
	@echo ""
	@echo "$(GREEN)Setting up Sprint Analytics...$(NC)"
	@cd $(SPRINT_DIR) && $(MAKE) setup
	@echo ""
	@echo "$(GREEN)Setting up Omniscient...$(NC)"
	@cd $(OMNISCIENT_DIR) && $(MAKE) setup
	@echo ""
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Configure $(SPRINT_DIR)/.env with CLICKUP_API_TOKEN"
	@echo "  2. Configure $(OMNISCIENT_DIR)/.env with MySQL credentials"
	@echo "  3. Run: make all"
	@echo ""

test: ## Test all project connections
	@echo "$(CYAN)Testing project connections...$(NC)"
	@echo ""
	@echo "$(GREEN)Testing Sprint Analytics...$(NC)"
	@cd $(SPRINT_DIR) && $(MAKE) check-env
	@echo ""
	@echo "$(GREEN)Testing Omniscient...$(NC)"
	@cd $(OMNISCIENT_DIR) && $(MAKE) test
	@echo ""

# Quick workflow targets
quick: sprint-analytics view-sprint ## Quick: Generate and view sprint analytics

full: all view-all ## Full: Generate all reports and open them

daily: sprint-analytics omniscient ## Daily workflow: Regenerate both main reports

weekly: all info ## Weekly workflow: Full regeneration with summary

# Individual project shortcuts
sprint: sprint-analytics ## Alias for sprint-analytics
okr: omniscient ## Alias for omniscient
