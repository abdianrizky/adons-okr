# Adon's OKR & Sprint Analytics

This repository contains tools and reports for tracking OKRs and sprint performance metrics.

## 📑 Quick Links to Key Reports

- **[📈 View Latest Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)**
- **[🔍 View SonarQube Code Analysis Report](./sonarqube-analytics/reports/README.md)**

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

## 🔗 Links

- [Sprint Analytics Documentation](./sprint-analytics/README.md)
- [Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)
- [SonarQube Analytics Documentation](./sonarqube-analytics/README.md)
- [SonarQube Code Analysis Report](./sonarqube-analytics/reports/README.md)
- [ClickUp Workspace](https://app.clickup.com/3708016/)
- [SonarQube Server](https://sonar.infra.paper.id)

---

*Last updated: 2026-01-26*
