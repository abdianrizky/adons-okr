# Omniscient OKR Analytics

Automated OKR reporting and analytics for PR quality metrics from the Omniscient database.

## Overview

This tool collects PR quality data from your MySQL database, calculates comprehensive OKR metrics, and generates visualizations and reports to track code quality trends, contributor performance, and identify improvement areas.

## Features

- **Database Integration**: Direct MySQL connection to Omniscient database
- **Comprehensive Metrics**: PR quality trends, contributor performance, repository statistics
- **Rich Visualizations**: 6 interactive charts including trends, distributions, and heatmaps
- **Multiple Output Formats**: JSON, CSV, and Markdown reports
- **Flexible Date Ranges**: Filter data by custom date ranges
- **Top Performers Tracking**: Identify high-performing contributors and repositories
- **Improvement Insights**: Automatically identify areas needing attention

## Quick Start

### 1. Setup

Install dependencies:
```bash
cd omniscient
pip install -r requirements.txt
```

### 2. Configure Database

Copy the example environment file and fill in your MySQL credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=omniscient
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Optional: Date range
START_DATE=2025-01-01
END_DATE=2025-12-31
```

### 3. Run

#### Option A: Using Makefile (Recommended)
```bash
# Show all available commands
make help

# Generate full report
make run

# Quick daily report (JSON only, no charts)
make quick

# Test connection first
make test
```

#### Option B: Direct Python
```bash
# Generate full OKR report
python gather_okr_metrics.py
```

## Usage Examples

### Using Makefile (Recommended)

```bash
# Show all commands
make help

# First-time setup and run
make first-run

# Generate full report
make run

# Quick report (JSON only)
make quick

# Generate specific formats
make json
make csv
make markdown

# Date range reports
make ytd          # Year-to-date
make q1           # Q1 (Jan-Mar)
make q2           # Q2 (Apr-Jun)
make h1           # H1 (Jan-Jun)
make h2           # H2 (Jul-Dec)
make this-month   # Current month
make last-month   # Previous month

# View results
make view-report  # Open markdown report
make view-charts  # Open all charts
make view-json    # Display JSON metrics

# Workflows
make daily        # Quick daily check
make weekly       # Weekly full report
make monthly      # Monthly report

# Utilities
make test         # Test database connection
make clean        # Clean generated files
make info         # Show project info
```

### Using Python Directly

```bash
# Basic report generation
python gather_okr_metrics.py

# Custom date range
python gather_okr_metrics.py --start-date 2025-01-01 --end-date 2025-06-30

# JSON output only
python gather_okr_metrics.py --format json

# Skip chart generation
python gather_okr_metrics.py --no-charts

# Verbose output
python gather_okr_metrics.py -v
```

## Output Files

### Reports
- `reports/okr_report.md` - Comprehensive markdown report with insights and recommendations

### Data Exports
- `output/okr_metrics.json` - Complete metrics in JSON format
- `output/okr_pr_data.csv` - Raw PR data export

### Visualizations
- `output/pr_quality_trend.png` - Weekly quality trend with PR volume
- `output/score_distribution.png` - Overall score histogram
- `output/contributor_performance.png` - Top 10 contributors by PR count
- `output/category_heatmap.png` - Average scores across quality categories
- `output/decision_breakdown.png` - PR decision distribution pie chart
- `output/monthly_pr_volume.png` - Monthly PR volume and quality trends

## Metrics Tracked

### Summary Metrics
- Total PRs analyzed
- Active contributors
- Repositories tracked
- Average and median overall scores
- Quality grade (A-F scale)

### Quality Categories (1-5 scale)
- **Readability**: Code clarity and naming conventions
- **Function Usability**: Function design and reusability
- **Idiomaticity**: Language-specific best practices
- **Test Inclusion**: Test coverage and quality
- **Commit Size**: PR scope and focus
- **Complexity**: Code complexity and maintainability
- **Code Churn**: Change scope and stability
- **Clean Code Structure**: Architecture and separation of concerns

### Trend Analysis
- Weekly quality trends
- Monthly PR volume
- Contributor performance over time
- Category score evolution

### Performance Insights
- Top performers (contributors and repositories)
- Areas needing improvement
- Contributors who may need support

## Project Structure

```
omniscient/
├── README.md                       # This file
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── gather_okr_metrics.py           # Main CLI script
├── src/                            # Source modules
│   ├── __init__.py
│   ├── db_client.py                # MySQL database client
│   ├── metrics_calculator.py      # Metrics computation
│   ├── visualizer.py               # Chart generation
│   └── report_generator.py        # Report creation
├── output/                         # Generated charts and data
├── data/                           # Cached data (optional)
└── reports/                        # Generated reports
```

## Database Schema

The tool expects the following MySQL table structure:

```sql
CREATE TABLE `pr_scores` (
    `id` int NOT NULL AUTO_INCREMENT,
    `github_user_id` varchar(255) NOT NULL,
    `commit_hash` varchar(40) NOT NULL,
    `pr_number` int NOT NULL,
    `repository` varchar(255) NOT NULL,
    `tags` json NOT NULL,
    `readability` varchar(20) DEFAULT NULL,
    `function_usability` varchar(20) DEFAULT NULL,
    `idiomaticity` varchar(20) DEFAULT NULL,
    `test_inclusion` varchar(20) DEFAULT NULL,
    `commit_size` varchar(20) DEFAULT NULL,
    `complexity` varchar(20) DEFAULT NULL,
    `code_churn` varchar(20) DEFAULT NULL,
    `clean_code_structure` varchar(20) DEFAULT NULL,
    `overall_score` int DEFAULT NULL,
    `decision` varchar(20) DEFAULT NULL,
    `pr_comment` text,
    `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## Scoring System

### Overall Score (8-40 scale)
- **35-40**: A - Excellent (merge immediately)
- **28-34**: B - Good (approve with minor suggestions)
- **21-27**: C - Acceptable (request changes)
- **14-20**: D - Needs Work (significant improvements needed)
- **8-13**: F - Reject (major rework required)

### Category Scores (1-5 scale)
- **5**: Excellent/Minimal/Small/Stable
- **4**: Good/Well-Structured/Manageable/Low
- **3**: Acceptable/Functional/Medium/Moderate
- **2**: Poor/Confusing/Large/High
- **1**: Unreadable/Messy/Huge/Excessive

## Troubleshooting

### Connection Issues
If you get database connection errors:
1. Verify MySQL credentials in `.env`
2. Check MySQL server is running
3. Ensure network connectivity to database host
4. Verify database name exists

### Missing Data
If no data is returned:
1. Check date range filters
2. Verify data exists in `pr_scores` table
3. Run with `-v` flag for verbose output

### Import Errors
If you get module import errors:
1. Ensure you're in the `omniscient` directory
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check Python version (requires Python 3.8+)

## Contributing

This is part of the larger Adon's OKR & Sprint Analytics repository. See the main [README](../README.md) for more information.

## Links

- [Main OKR Repository](../)
- [Sprint Analytics](../sprint-analytics/)
- [SonarQube Analytics](../sonarqube-analytics/)
- [MTTR Reports](../MTTR/)
- [Paper Omniscient Source](/Users/adon/paperid/paper-omniscient)

---

*Last updated: 2026-01-26*
