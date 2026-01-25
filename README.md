# Adon's OKR & Sprint Analytics

This repository contains tools and reports for tracking OKRs and sprint performance metrics.

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

## 🔗 Links

- [Sprint Analytics Documentation](./sprint-analytics/README.md)
- [Sprint Summary Report](./sprint-analytics/output/sprint_summary.md)
- [ClickUp Workspace](https://app.clickup.com/3708016/)

---

*Last updated: 2026-01-26*
