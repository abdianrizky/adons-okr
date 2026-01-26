# SonarQube Analytics

Comprehensive SonarQube analysis and coverage tracking for paper-payment-backend and paper-document projects.

## 📁 Project Structure

```
sonarqube-analytics/
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
├── scripts/              # Executable scripts
│   ├── fetch-coverage-history.py    # Fetch coverage data from SonarQube API
│   ├── visualize-coverage.py        # Generate coverage visualizations
│   └── generate-coverage-graph.sh   # Main wrapper script
│
├── data/                 # Generated data files
│   ├── *.csv             # Coverage and metrics data
│   ├── *.json            # Raw API responses
│   └── *.html            # Interactive visualizations
│
├── reports/              # Markdown reports
│   ├── OVERALL-CODE-SUMMARY.md      # Complete codebase analysis
│   ├── SUMMARY.md                   # New code quality report
│   └── PROJECT-LINKS.md             # Quick access links
│
└── docs/                 # Documentation
    ├── README.md                     # Usage guide
    ├── COVERAGE-GRAPH-README.md      # Coverage graph documentation
    ├── QUICKSTART-COVERAGE-GRAPH.md  # Quick start guide
    ├── MCP-FINDINGS.md               # MCP analysis
    ├── TEST-RESULTS.md               # Test results
    └── INDEX.md                      # Complete file index
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your SonarQube token
# Get token from: https://sonar.infra.paper.id → My Account → Security
vim .env
```

### 2. Generate Coverage Graph

```bash
# Run the main script
./scripts/generate-coverage-graph.sh paper-payment-backend

# Or with custom date range
./scripts/generate-coverage-graph.sh paper-payment-backend 2025-07-01 2025-12-31

# For paper-document
./scripts/generate-coverage-graph.sh paper-document
```

### 3. View Results

```bash
# Open the interactive HTML chart
open data/paper-payment-backend-coverage-history.html

# View CSV data
cat data/paper-payment-backend-coverage-history.csv

# View reports
cat reports/OVERALL-CODE-SUMMARY.md
```

## 📊 What's Included

### Reports

#### Overall Code Analysis
- **Location:** `reports/OVERALL-CODE-SUMMARY.md`
- **Scope:** Entire codebase (302k LOC for backend, 94k for document)
- **Metrics:** Coverage, duplications, bugs, vulnerabilities, code smells
- **Use:** Strategic planning, executive reporting

#### New Code Quality
- **Location:** `reports/SUMMARY.md`
- **Scope:** Recent changes only
- **Metrics:** Quality gate conditions, trends
- **Use:** Sprint reviews, developer feedback

#### Project Links
- **Location:** `reports/PROJECT-LINKS.md`
- **Content:** Direct links to SonarQube dashboards
- **Use:** Quick access

### Data Files

All generated data is stored in `data/`:
- **CSV Files:** Coverage history, metrics, trends, issues
- **JSON Files:** Raw API responses
- **HTML Files:** Interactive charts with Chart.js

### Scripts

#### Main Script
```bash
./scripts/generate-coverage-graph.sh <project> [from-date] [to-date]
```

#### Python Scripts
- `fetch-coverage-history.py` - Fetch historical coverage data
- `visualize-coverage.py` - Generate ASCII, markdown, and HTML visualizations

## 🔧 Configuration

### Environment Variables (.env)

```bash
# SonarQube Server
SONAR_URL=https://sonar.infra.paper.id

# Authentication (REQUIRED)
SONAR_TOKEN=your-sonarqube-token-here

# Project Keys
PROJECT_PAYMENT_BACKEND=paper-payment-backend
PROJECT_DOCUMENT=paper-document

# Default Date Range
DATE_FROM=2025-07-01
DATE_TO=2025-12-31
```

### Getting a SonarQube Token

1. Go to https://sonar.infra.paper.id
2. Click profile → **My Account** → **Security**
3. Generate a new token
4. Copy token to `.env` file

## 📖 Documentation

Detailed documentation is available in `docs/`:

- **README.md** - Full usage guide with examples
- **COVERAGE-GRAPH-README.md** - Coverage graph documentation
- **QUICKSTART-COVERAGE-GRAPH.md** - Quick start guide
- **MCP-FINDINGS.md** - Analysis of SonarQube MCP limitations
- **TEST-RESULTS.md** - Script test results
- **INDEX.md** - Complete file listing

## 🎯 Key Metrics

### paper-payment-backend (302k LOC)
- Coverage: 31.6% (target: 80%)
- Duplications: 3.8% (threshold: 3%)
- Bugs: 1 (C rating)
- Vulnerabilities: 0 (A rating)
- Total Issues: 3,001

**Visual Proof:**
![paper-payment-backend Overview](reports/proofs/paper-payment-backend-overview.png)
![paper-payment-backend Issues](reports/proofs/paper-payment-backend-issues.png)

### paper-document (94k LOC)
- Coverage: 10.0% 🔥 **CRITICAL**
- Duplications: 12.5% 🔥 **CRITICAL**
- Bugs: 1 (C rating)
- Vulnerabilities: 0 (A rating)
- Total Issues: 1,540

**Visual Proof:**
![paper-document Overview](reports/proofs/paper-document-overview.png)
![paper-document Issues](reports/proofs/paper-document-issues.png)

## ⚠️ Important Notes

### MCP Limitation
The SonarQube MCP **does not have** the `/api/measures/search_history` endpoint. The scripts in this project directly call the SonarQube API using your authentication token.

### Requirements
- Python 3.x
- `requests` library (auto-installed by script)
- SonarQube authentication token
- Internet access to SonarQube server

## 🔗 Links

- **SonarQube Server:** https://sonar.infra.paper.id
- **paper-payment-backend:** https://sonar.infra.paper.id/dashboard?id=paper-payment-backend&codeScope=overall
- **paper-document:** https://sonar.infra.paper.id/dashboard?id=paper-document&codeScope=overall

## 📝 Usage Examples

### Generate Coverage for Both Projects

```bash
# paper-payment-backend
./scripts/generate-coverage-graph.sh paper-payment-backend

# paper-document
./scripts/generate-coverage-graph.sh paper-document
```

### Custom Date Range

```bash
./scripts/generate-coverage-graph.sh paper-payment-backend 2025-01-01 2025-12-31
```

### View All Reports

```bash
# Overall code summary
less reports/OVERALL-CODE-SUMMARY.md

# New code quality
less reports/SUMMARY.md

# Project links
cat reports/PROJECT-LINKS.md
```

### Analyze Data with jq

```bash
# Count critical issues
jq '[.[] | select(.severity == "HIGH")] | length' data/paper-payment-backend-all-issues.json

# Top issue authors
jq -r '.[] | .author' data/paper-payment-backend-all-issues.json | sort | uniq -c | sort -rn
```

## 🆘 Troubleshooting

### "401 Unauthorized"
- Check SONAR_TOKEN in `.env` file
- Verify token is valid at https://sonar.infra.paper.id

### "No module named 'requests'"
- Script will auto-install
- Or manually: `python3 -m pip install --break-system-packages requests`

### "Failed to fetch coverage history"
- Verify SONAR_TOKEN is set
- Check network connection
- Verify project key is correct

## 📧 Support

For issues or questions:
- Check documentation in `docs/`
- Review test results in `docs/TEST-RESULTS.md`
- Contact DevOps/QA team

---

**Last Updated:** 2026-01-26
**Location:** `/Users/adon/paperid/adons-okr/sonarqube-analytics/`
