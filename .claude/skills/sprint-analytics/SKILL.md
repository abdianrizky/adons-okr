---
name: sprint-analytics
description: Analyze ClickUp sprint metrics for H2 2025 (Sprint 43-50). Generates charts, calculates KPIs, and detects carryover tasks. Use when analyzing sprint performance, creating reports, or reviewing team velocity.
argument-hint: "[run|dry-run|refresh|cache|clean|sprint N M...]"
disable-model-invocation: false
allowed-tools: Bash(make:*), Read
---

# Sprint Analytics

Analyze ClickUp sprint metrics with intelligent carryover detection and generate comprehensive reports and visualizations.

## What This Does

This skill runs the sprint analytics pipeline that:
1. Fetches task data from ClickUp API (or uses sample/cached data)
2. Detects carryover tasks between sprints
3. Calculates metrics (committed, delivered, burndown, delivery rate)
4. Generates 3 high-quality PNG charts (300 DPI)
5. Exports reports in JSON, CSV, and Markdown formats
6. Provides automated insights and statistics

## Command Mapping

Based on $ARGUMENTS, execute the appropriate command:

| User Input | Make Command | Description |
|------------|--------------|-------------|
| (empty) or "run" | `make run` | Run with real ClickUp data |
| "dry-run" | `make dry-run` | Test with sample data (no API) |
| "refresh" | `make refresh` | Force API refresh, ignore cache |
| "cache" | `make cache` | Use cached data only |
| "clean" | `make clean` | Clean generated files |
| "setup" | `make setup` | First-time setup |
| "help" | `make help` | Show all commands |
| "sprint N M..." | `make sprint SPRINTS="N M"` | Analyze specific sprints |

## Execution Steps

1. Change to the sprint-analytics directory:
   ```bash
   cd /Users/adon/paperid/adons-okr/sprint-analytics
   ```

2. Determine the command from $ARGUMENTS (default to "run" if empty)

3. Execute the appropriate make command

4. After execution, show the user:
   - Command output summary
   - List of generated files in `output/`
   - Key metrics (if available)

## Generated Output Files

All files are created in `sprint-analytics/output/`:

**Charts (PNG, 300 DPI)**:
- `sprint_velocity_chart.png` - Velocity bar chart (committed vs delivered vs carryover)
- `sprint_burndown_chart.png` - Burndown line chart with area fill
- `sprint_delivery_rate_chart.png` - Delivery rate percentage with target line

**Reports**:
- `sprint_metrics.json` - Complete data export with all task details
- `sprint_metrics.csv` - Summary table (Excel-compatible)
- `sprint_summary.md` - Markdown report with automated insights

## After Running

1. **Show output summary** from the make command
2. **List generated files**: Use `make show-output` or list the output directory
3. **Read key insights**: Open `output/sprint_summary.md` to extract:
   - Total points delivered / total work
   - Average delivery rate
   - Best and worst performing sprints
   - Trend analysis
4. **Present to user**: Summarize the results in a clear format

## Example Executions

### Example 1: No arguments (default run)
```bash
cd /Users/adon/paperid/adons-okr/sprint-analytics
make run
```

### Example 2: Dry-run mode
```bash
cd /Users/adon/paperid/adons-okr/sprint-analytics
make dry-run
```

### Example 3: Specific sprints
```bash
cd /Users/adon/paperid/adons-okr/sprint-analytics
make sprint SPRINTS="48 49 50"
```

## Metrics Reference

- **Points Committed**: Total story points assigned to sprint
- **Carryover In**: Points from tasks carried over from previous sprint
- **Total Work**: Committed + Carryover In
- **Points Delivered**: Points completed (status contains "deployed")
- **Carryover Out**: Points not completed
- **Burndown**: Total Work - Points Delivered
- **Delivery Rate**: (Points Delivered / Total Work) × 100%

## Prerequisites

- Virtual environment set up (run `make setup` if not)
- For non-dry-run modes: `CLICKUP_API_TOKEN` in `.env` file
- Working directory: `/Users/adon/paperid/adons-okr/sprint-analytics/`

## Troubleshooting

**"CLICKUP_API_TOKEN not found"**:
- Run: `cd /Users/adon/paperid/adons-okr/sprint-analytics && make setup`
- Edit `.env` file and add token

**"No module named 'yaml'"**:
- Run: `cd /Users/adon/paperid/adons-okr/sprint-analytics && make setup`

**No charts generated**:
- Check `output/` directory exists
- Verify matplotlib installed
- Run with dry-run first to test

## Additional Commands

- `make show-config` - Show current configuration
- `make show-output` - List generated files
- `make open-charts` - Open charts in default viewer
- `make open-report` - Open markdown report
- `make info` - Show project information

## Quick Start

First time using this skill:
```bash
cd /Users/adon/paperid/adons-okr/sprint-analytics
make setup
# Edit .env with CLICKUP_API_TOKEN
make dry-run  # Test
make run      # Real data
```
