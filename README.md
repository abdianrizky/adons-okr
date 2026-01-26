# Adon's OKR & Sprint Analytics

This repository contains tools and reports for tracking OKRs and sprint performance metrics.

## 📑 Quick Links to Key Reports

- **[📈 View Latest Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)**
- **[🔍 View SonarQube Code Analysis Report](./sonarqube-analytics/reports/README.md)**
- **[⏱️ View MTTR Performance Report H2 2025](./MTTR/README.md)**
- **[🎯 View Omniscient Summary Report (adon-paper, 2025-06-23 to 2026-01-01)](./Omniscient/reports/adon-paper/2025_06_23_to_2026_01_01/okr_report.md)**

---

## 📊 Sprint Analytics

Automated sprint metrics analysis and reporting for Paper.id engineering teams.

**[📈 View Latest Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)**

### Quick Stats

- **Teams Tracked**: SMB Payment Team & Revenue & Growth Team
- **Total Sprints**: 12 sprints (Sprint 43-50 Payment, Sprint 1-4 RnG)
- **Average Delivery Rate**: 95.9%
- **Average Velocity**: 13.0 points/sprint

### Available Reports & Charts

- **[Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)** - Comprehensive markdown report with insights
- **[Sprint Metrics CSV](./sprint-analytics/output/sprint_metrics.csv)** - Exportable data for analysis
- **[Sprint Metrics JSON](./sprint-analytics/output/sprint_metrics.json)** - Complete structured data
- **Sprint Velocity Chart** - Points committed vs delivered (horizontal bar chart)
- **Sprint Burndown Chart** - Overall burndown trend across sprints
- **Sprint Delivery Rate Chart** - Delivery rate percentage trend

### Project Structure

```
adons-okr/
├── README.md                           # This file
└── sprint-analytics/                   # Sprint metrics analysis system
    ├── gather_sprint_metrics.py        # Main CLI tool
    ├── config.yaml                     # Sprint configurations
    ├── requirements.txt                # Python dependencies
    ├── src/                            # Source code modules
    │   ├── clickup_client.py           # ClickUp API integration
    │   ├── metrics_calculator.py       # Sprint metrics computation
    │   ├── carryover_detector.py       # Task carryover detection
    │   ├── visualizer.py               # Chart generation
    │   ├── report_generator.py         # Report generation
    │   └── utils.py                    # Utilities
    ├── data/
    │   └── cache/                      # API response cache
    └── output/                         # Generated reports & charts
        ├── sprint_summary.md           # Main summary report
        ├── sprint_metrics.csv          # CSV export
        ├── sprint_metrics.json         # JSON export
        ├── sprint_velocity_chart.png   # Velocity visualization
        ├── sprint_burndown_chart.png   # Burndown visualization
        └── sprint_delivery_rate_chart.png  # Delivery rate trend
```

## 🚀 Usage

### View Reports

Open the markdown report directly:
```bash
open sprint-analytics/output/sprint_summary.md
```

Or view charts:
```bash
open sprint-analytics/output/sprint_velocity_chart.png
open sprint-analytics/output/sprint_delivery_rate_chart.png
```

### Regenerate Reports

```bash
cd sprint-analytics
python3 gather_sprint_metrics.py
```

For more options:
```bash
python3 gather_sprint_metrics.py --help
```

## 📋 Features

- ✅ **Real-time Data**: Fetches sprint data from ClickUp API
- ✅ **History-Based Burndown**: Tracks actual task status changes day-by-day
- ✅ **Carryover Detection**: Identifies tasks carried between sprints
- ✅ **Multi-Team Support**: Tracks both SMB Payment and Revenue & Growth teams
- ✅ **Multiple Formats**: JSON, CSV, and Markdown reports
- ✅ **Visualizations**: High-quality PNG charts (300 DPI)
- ✅ **Caching**: Intelligent API caching to minimize rate limits
- ✅ **Sprint Reporting Links**: Direct links to ClickUp Sprint Reporting dashboards

## 📈 Key Metrics

- **Points Committed**: Total story points assigned to sprint
- **Points Delivered**: Story points completed (deployed status)
- **Carryover In/Out**: Points moved between sprints
- **Delivery Rate**: (Delivered / Total Work) × 100%
- **Velocity**: Average points delivered per sprint
- **Burndown**: Points remaining (Total Work - Delivered)

## 🔍 SonarQube Analytics

Comprehensive code quality and coverage tracking for Paper.id backend projects.

**[🔍 View SonarQube Code Analysis Report](./sonarqube-analytics/reports/README.md)**

### Quick Stats

- **Projects Monitored**: paper-payment-backend (302k LOC), paper-document (94k LOC)
- **Overall Quality Gate**: ❌ Failed (both projects)
- **Total Issues Tracked**: 4,541 issues
- **Coverage Reports**: Historical coverage tracking with interactive charts

### Key Findings

#### paper-payment-backend
- Coverage: 31.6% (target: 80%) ❌
- Duplications: 3.8% ✅
- Issues: 3,001 (65.7% critical severity)
- [View Dashboard](https://sonar.infra.paper.id/dashboard?id=paper-payment-backend&codeScope=overall)

#### paper-document
- Coverage: 10.0% 🔥 **CRITICAL**
- Duplications: 12.5% 🔥 **CRITICAL**
- Issues: 1,540 (21.7% critical severity)
- [View Dashboard](https://sonar.infra.paper.id/dashboard?id=paper-document&codeScope=overall)

### Available Reports

- **[Overall Code Analysis Report](./sonarqube-analytics/reports/README.md)** - Complete codebase metrics
- **Coverage History Charts** - Interactive HTML visualizations
- **Issue Tracking CSV/JSON** - Exportable data for analysis
- **Visual Proofs** - SonarQube dashboard screenshots

### Project Structure

```
sonarqube-analytics/
├── README.md                    # Main documentation
├── scripts/                     # Analysis scripts
│   ├── fetch-coverage-history.py
│   ├── visualize-coverage.py
│   └── generate-coverage-graph.sh
├── data/                        # Generated data files
│   ├── *.csv                    # Metrics & coverage data
│   ├── *.json                   # Raw API responses
│   └── *.html                   # Interactive charts
├── reports/                     # Analysis reports
│   ├── README.md                # Overall code summary
│   └── proofs/                  # Screenshot evidence
└── docs/                        # Documentation
```

## ⏱️ MTTR (Mean Time To Resolve)

Comprehensive performance tracking for bug/issue resolution metrics.

**[⏱️ View MTTR Performance Report H2 2025](./MTTR/README.md)**

### Quick Stats (H2 2025)

- **Reporting Period**: June 1 - December 31, 2025
- **Total Tasks**: 151 tasks
- **SLA Compliance**: 91.39% (138 out of 151 tasks)
- **Avg Resolution Time**: 20.31 hours
- **Avg Response Time**: 5.11 hours
- **Performance Grade**: A- (Exceeds 90% target)

### Key Highlights

- **Strong Q3 Performance**: 93.7% compliance with 18.7-hour avg resolution time
- **High Volume Capacity**: Successfully handled up to 14 tasks per week at 100% compliance
- **Fast Response**: Sub-6 hour average response time demonstrates excellent triage
- **Consistency**: 57.1% of weeks achieved 100% SLA compliance

### Available Reports

- **[Performance Report](./MTTR/README.md)** - Complete H2 2025 analysis with trends and recommendations
- **[Raw Metrics CSV](./MTTR/mttr_metrics.csv)** - Weekly data for all 28 weeks
- **[Live Dashboard](https://paperspark.paper.id/dashboard/3541-bug-issue-monitoring-dwh-ver)** - Real-time Metabase monitoring

### Project Structure

```
MTTR/
├── README.md                # Performance report & analysis
├── mttr_metrics.csv         # Weekly metrics data
└── proofs/                  # Dashboard screenshots
    ├── mttr-1.png
    └── mttr-2.png
```

## 🎯 Omniscient OKR Analytics

Comprehensive PR quality tracking and OKR reporting from the Omniscient database.

**[🎯 View Personal OKR Report (adon-paper)](./Omniscient/reports/adon-paper/2025_06_23_to_2026_01_01/okr_report.md)**

### Quick Stats (adon-paper, 2025-06-23 to 2026-01-01)

- **Total PRs**: 205 PRs across 14 repositories
- **Average Score**: 29.39/40 (Grade B - Good)
- **Performance**: 70% Good, 26% Acceptable, 4% Excellent
- **Top Strengths**: Idiomaticity (3.95), Readability (3.90), Code Churn (3.89)
- **Needs Improvement**: Test Inclusion (2.43)

### System Features

- **Data Source**: MySQL database with PR quality scores
- **Metrics Tracked**: 8 quality categories (readability, usability, idiomaticity, etc.)
- **Output Formats**: JSON, CSV, Markdown reports + 6 interactive charts
- **Key Features**: Contributor performance, quality trends, improvement insights

### Available Reports & Charts

- **[Personal OKR Report (adon-paper)](./Omniscient/reports/adon-paper/2025_06_23_to_2026_01_01/okr_report.md)** - Comprehensive PR quality analysis
- **[Metrics JSON](./Omniscient/output/adon-paper/2025_06_23_to_2026_01_01/okr_metrics.json)** - Complete structured data
- **[PR Data CSV](./Omniscient/output/adon-paper/2025_06_23_to_2026_01_01/pr_data.csv)** - Exportable PR records (205 PRs)
- **Quality Trend Chart** - Weekly PR quality trends with volume
- **Score Distribution Chart** - Overall score histogram with mean/median
- **Category Heatmap** - Average scores across quality categories (matches dashboard!)
- **Decision Breakdown Chart** - PR decision distribution
- **Monthly Volume Chart** - Monthly PR volume and quality trends

### Project Structure

```
omniscient/
├── README.md                       # Documentation
├── gather_okr_metrics.py           # Main CLI tool
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── src/                            # Source code modules
│   ├── db_client.py                # MySQL database client
│   ├── metrics_calculator.py      # Metrics computation
│   ├── visualizer.py               # Chart generation
│   └── report_generator.py        # Report creation
├── output/                         # Generated charts & data
└── reports/                        # Generated reports
```

### Usage

```bash
cd omniscient

# Setup environment (one-time)
make setup
# Edit .env with your MySQL credentials

# Generate YOUR report (default: adon-paper)
make my-report              # All data up to today

# Generate with specific date range
python generate_user_report.py --user adon-paper --start-date 2025-06-23 --end-date 2026-01-01

# Generate period reports
make my-h2                  # H2 2025
make my-q4                  # Q4 2025
make my-ytd                 # Year to date

# For different user
make my-report GITHUB_USER=mohamadfhatir

# View help
make help
```

## 🔗 Links

- [Sprint Analytics Documentation](./sprint-analytics/README.md)
- [Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)
- [SonarQube Analytics Documentation](./sonarqube-analytics/README.md)
- [SonarQube Code Analysis Report](./sonarqube-analytics/reports/README.md)
- [MTTR Performance Report H2 2025](./MTTR/README.md)
- [MTTR Metrics CSV](./MTTR/mttr_metrics.csv)
- [Omniscient OKR Analytics](./Omniscient/README.md)
- [Personal OKR Report (adon-paper, 2025-06-23 to 2026-01-01)](./Omniscient/reports/adon-paper/2025_06_23_to_2026_01_01/okr_report.md)
- [ClickUp Workspace](https://app.clickup.com/3708016/)
- [SonarQube Server](https://sonar.infra.paper.id)
- [Bug Monitoring Dashboard](https://paperspark.paper.id/dashboard/3541-bug-issue-monitoring-dwh-ver)

---

*Last updated: 2026-01-26*
