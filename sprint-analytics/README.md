# ClickUp Sprint Analytics

A Python-based system to collect ClickUp sprint metrics for H2 2025 (Sprint 43-50), calculate KPIs with intelligent carryover detection, and generate static PNG visualizations and comprehensive reports.

## Features

- **Automated Data Collection**: Fetches sprint data from ClickUp API with rate limiting and caching
- **Intelligent Carryover Detection**: Analyzes tasks across sprints to detect carryover patterns
- **Comprehensive Metrics**: Calculates points committed, delivered, carryover in/out, burndown, and delivery rate
- **High-Quality Visualizations**: Generates 300 DPI PNG charts using matplotlib
- **Multiple Report Formats**: Outputs JSON, CSV, and Markdown reports
- **Flexible CLI**: Supports dry-run, caching, refresh, and selective sprint processing

## Project Structure

```
sprint-analytics/
├── gather_sprint_metrics.py  # Main CLI entry point
├── config.yaml                # Sprint configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
├── src/
│   ├── __init__.py
│   ├── clickup_client.py      # ClickUp API wrapper with caching
│   ├── carryover_detector.py  # Cross-sprint task analysis
│   ├── metrics_calculator.py  # Metrics computation
│   ├── visualizer.py          # Matplotlib chart generation
│   ├── report_generator.py    # JSON/CSV/Markdown output
│   └── utils.py               # Logging, caching utilities
├── data/
│   ├── cache/                 # API response cache
│   └── sample_sprint.json     # Sample data for dry-run
└── output/                    # Generated reports and charts
```

## Installation

### Prerequisites

- Python 3.8 or higher
- ClickUp API token ([Get one here](https://app.clickup.com/settings/apps))

### Setup

**Option 1: Using Makefile (Recommended)**

```bash
# Navigate to project directory
cd /Users/adon/paperid/adons-okr/sprint-analytics

# Complete setup (creates venv, installs dependencies, creates .env)
make setup

# Edit .env and add your CLICKUP_API_TOKEN
# Then test with sample data
make dry-run
```

**Option 2: Manual Setup**

1. **Navigate to the project directory:**
   ```bash
   cd /Users/adon/paperid/adons-okr/sprint-analytics
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ClickUp API token
   ```

5. **Verify configuration:**
   ```bash
   cat config.yaml
   # Ensure sprint list IDs and user ID are correct
   ```

## Usage

### Using Makefile (Recommended)

The Makefile provides convenient shortcuts for all operations:

```bash
# Run with real ClickUp data
make run

# Test with sample data (no API calls)
make dry-run

# Force refresh from API
make refresh

# Use cached data only
make cache

# Analyze specific sprints
make sprint SPRINTS="48 49 50"

# Clean generated files
make clean

# Show help
make help
```

Additional commands:
```bash
make show-config      # Show current configuration
make show-output      # List generated files
make open-charts      # Open charts in default viewer
make open-report      # Open markdown report
make info             # Show project information
```

### Using Claude Code Skill

If you're using Claude Code, you can invoke the analytics with a slash command:

```
/sprint-analytics              # Run with real data
/sprint-analytics dry-run      # Test with sample data
/sprint-analytics refresh      # Force API refresh
/sprint-analytics sprint 48 49 # Analyze specific sprints
/sprint-analytics clean        # Clean generated files
```

The skill is located at `../.claude/skills/sprint-analytics/SKILL.md`

### Using Python CLI Directly

```bash
# Activate virtual environment first
source venv/bin/activate

# Fetch data from ClickUp and generate all outputs
python gather_sprint_metrics.py

# Test with sample data (no API calls)
python gather_sprint_metrics.py --dry-run

# Use only cached data
python gather_sprint_metrics.py --cache

# Force refresh from API (ignore cache)
python gather_sprint_metrics.py --refresh

# Process specific sprints only
python gather_sprint_metrics.py --sprints 43 44 45

# Custom output directory
python gather_sprint_metrics.py --output-dir ./custom_output

# Enable verbose logging
python gather_sprint_metrics.py --verbose
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Test with sample data (no API calls) |
| `--cache` | Use only cached data (fail if not cached) |
| `--refresh` | Force refresh all data from API (ignore cache) |
| `--output-dir PATH` | Custom output directory (default: `./output`) |
| `--config PATH` | Path to config file (default: `config.yaml`) |
| `--sprints N [N ...]` | Process specific sprint numbers only |
| `--verbose` | Enable verbose logging |

## Output Files

### Charts (PNG, 300 DPI)

1. **sprint_velocity_chart.png** - Grouped bar chart showing:
   - Points Committed (blue)
   - Points Delivered (green)
   - Carryover Out (orange)

2. **sprint_burndown_chart.png** - Line chart with area fill showing:
   - Burndown trend over weeks
   - Points remaining per sprint

3. **sprint_delivery_rate_chart.png** - Line chart showing:
   - Delivery rate percentage
   - Target line at 100%
   - Color-coded performance zones

### Reports

1. **sprint_metrics.json** - Complete data dump with:
   - Overall statistics
   - Per-sprint metrics
   - All task details
   - Carryover information

2. **sprint_metrics.csv** - Summary table with:
   - Sprint number, name, week
   - All key metrics in tabular format
   - Importable to Excel/Google Sheets

3. **sprint_summary.md** - Markdown report with:
   - Executive summary
   - Overall statistics
   - Sprint-by-sprint breakdown
   - Task lists with clickable URLs
   - Auto-generated insights

## Configuration

### config.yaml

The main configuration file contains:

- **user_id**: ClickUp user ID (Adon: `81756915`)
- **sprints**: List of sprint definitions with:
  - `sprint_number`: Sprint identifier (43-50)
  - `name`: Sprint name
  - `week`: Week number
  - `list_id`: ClickUp list ID
  - `url`: Direct link to sprint in ClickUp
- **completion_status**: Keyword to match for completed tasks (default: `"deployed"`)
- **cache**: Cache settings (TTL, directory)
- **rate_limit**: API rate limiting configuration
- **retry**: Retry logic settings
- **output**: Output file names and DPI settings

### Environment Variables

Create a `.env` file with:

```bash
CLICKUP_API_TOKEN=your_clickup_api_token_here
```

Get your API token from: https://app.clickup.com/settings/apps

## Metrics Explained

### Core Metrics

- **Points Committed**: Total story points assigned to sprint
- **Carryover In**: Points from tasks carried over from previous sprint
- **Total Work**: Committed + Carryover In
- **Points Delivered**: Points completed (status contains "deployed")
- **Carryover Out**: Points not completed (moved to next sprint)
- **Burndown**: Total Work - Points Delivered
- **Delivery Rate**: (Points Delivered / Total Work) × 100

### Carryover Detection

The system uses a **multi-sprint task analysis** approach:

1. Fetches ALL tasks for ALL sprints
2. Builds a task_id → sprints_present mapping
3. For each task:
   - If task appears in Sprint N and Sprint N+1
   - AND was NOT completed in Sprint N
   - → Counted as **Carryover Out** from N
   - → Counted as **Carryover In** to N+1

**Limitation**: Only detects tasks still present in sprint lists. If a task is completely removed from a sprint (not just marked complete), it won't be detected.

### Completion Criteria

A task is considered **completed** if its status contains "deployed" (case-insensitive):

- ✅ Matches: "8.0 deployed", "Deployed", "DEPLOYED", "deployed to prod"
- ❌ Does NOT match: "done", "complete", "closed"

To change this, edit `completion_status.keyword` in `config.yaml`.

## Examples

### Example 1: First Run

```bash
# Set API token
export CLICKUP_API_TOKEN="pk_your_token_here"

# Fetch all sprint data
python gather_sprint_metrics.py --verbose
```

**Output:**
```
=== ClickUp Sprint Metrics Analysis ===
Loading configuration from config.yaml
Output directory: /Users/adon/paperid/adons-okr/sprint-analytics/output
Fetching data for 8 sprints...
Sprint 43: 15 tasks
Sprint 44: 18 tasks
...
Calculating sprint metrics...
Sprint 43: 42/55 points delivered (76.4% delivery rate)
...
Generating charts...
Generating reports...

============================================================
SPRINT METRICS SUMMARY
============================================================
Total Sprints: 8
Total Points Delivered: 345 / 425
Average Delivery Rate: 81.2%
Average Velocity: 43.1 points/sprint
Best Sprint: Sprint 46 (95.5%)
Worst Sprint: Sprint 43 (76.4%)
============================================================

Generated Charts:
  - velocity: output/sprint_velocity_chart.png
  - burndown: output/sprint_burndown_chart.png
  - delivery_rate: output/sprint_delivery_rate_chart.png

Generated Reports:
  - json: output/sprint_metrics.json
  - csv: output/sprint_metrics.csv
  - markdown: output/sprint_summary.md

=== Analysis Complete ===
```

### Example 2: Dry-Run Test

```bash
# Test without API calls
python gather_sprint_metrics.py --dry-run
```

Uses sample data from `data/sample_sprint.json` to test the entire pipeline.

### Example 3: Analyze Specific Sprints

```bash
# Only process Sprint 48, 49, 50
python gather_sprint_metrics.py --sprints 48 49 50
```

### Example 4: Use Cached Data

```bash
# First run: fetch and cache
python gather_sprint_metrics.py

# Second run: use cache (instant results)
python gather_sprint_metrics.py --cache
```

## Troubleshooting

### Issue: "CLICKUP_API_TOKEN not found"

**Solution:**
1. Create `.env` file: `cp .env.example .env`
2. Add your token: `CLICKUP_API_TOKEN=pk_your_token`
3. Verify: `cat .env`

### Issue: "Config file not found"

**Solution:**
```bash
# Verify you're in the correct directory
pwd
# Should be: /Users/adon/paperid/adons-okr/sprint-analytics

# Check if config exists
ls -la config.yaml
```

### Issue: API rate limit errors

**Solution:**
- Default rate limit is 80 req/min (conservative)
- Increase cache TTL in `config.yaml` to reduce API calls
- Use `--cache` flag for subsequent runs

### Issue: Carryover detection seems incorrect

**Possible causes:**
1. Task was removed from sprint list (not just marked complete)
2. Task status doesn't contain "deployed" keyword
3. Task appears in non-consecutive sprints

**Debug:**
1. Check `sprint_metrics.json` for task details
2. Verify task presence in ClickUp UI
3. Check task status matching keyword

### Issue: Points not showing up

**Possible causes:**
1. Points stored in non-standard field
2. Points field is empty

**Solution:**
- Verify points are in `task.points` OR custom field named "Points"
- Check `sprint_metrics.json` to see how points are extracted

## Advanced Usage

### Custom Points Field

If your ClickUp uses a different custom field name for points, modify `src/clickup_client.py`:

```python
@staticmethod
def extract_task_points(task: Dict) -> int:
    # Add your custom field name
    custom_fields = task.get('custom_fields', [])
    for field in custom_fields:
        if field.get('name', '').lower() in ['points', 'story points', 'your_field_name']:
            # ... rest of code
```

### Custom Completion Status

To match different completion statuses, edit `config.yaml`:

```yaml
completion_status:
  keyword: "done"  # or "complete", "closed", etc.
```

### Adding More Sprints

To add Sprint 51, edit `config.yaml`:

```yaml
sprints:
  # ... existing sprints
  - sprint_number: 51
    name: "Sprint 51"
    week: 44
    list_id: "your_list_id_here"
    url: "https://app.clickup.com/81756915/v/li/your_list_id_here"
```

## Performance

- **Initial run** (no cache): ~30-60 seconds for 8 sprints
- **Cached run**: <5 seconds
- **API calls**: 8 calls (one per sprint) + retry overhead
- **Memory**: ~50-100 MB for typical sprint data
- **Disk**: Cache files ~5-10 MB total

## Known Limitations

1. **Carryover Detection**: Only detects tasks still present in sprint lists. Tasks completely removed from sprints are not detected.

2. **Status Matching**: Relies on "deployed" substring. If status naming changes in ClickUp, configuration must be updated.

3. **Historical Data**: Can only analyze sprints that still exist in ClickUp. Archived/deleted sprints cannot be processed.

4. **Points Source**: Assumes points are in `task.points` or custom field named "Points". Other custom field names require code changes.

5. **Subtasks**: Subtasks are included but counted separately (not aggregated to parent).

## Future Enhancements

Potential improvements for future versions:

- [ ] Interactive HTML dashboards
- [ ] Trend forecasting for future sprints
- [ ] Team member breakdown
- [ ] Automated insights using ML
- [ ] Slack/email notifications
- [ ] Historical sprint archival
- [ ] Custom metric definitions

## Support

For issues or questions:

1. Check this README first
2. Review `sprint_summary.md` output for insights
3. Run with `--verbose` flag for detailed logs
4. Check `data/cache/` for cached API responses

## License

This is an internal tool for Paper.id sprint analytics.

---

**Generated by:** Claude Code (Anthropic)
**Version:** 1.0.0
**Last Updated:** 2026-01-25
