# SonarQube Analytics Directory

This directory contains comprehensive SonarQube analysis data for paper-payment-backend and paper-document repositories.

## 📊 Files Overview

### Summary Reports
- **OVERALL-CODE-SUMMARY.md** - ⭐ **NEW** Complete codebase analysis (302k LOC)
- **SUMMARY.md** - New code analysis (recent changes)
- **README.md** - This file

### CSV Exports (for Excel/Google Sheets)
- **overall-code-metrics.csv** - ⭐ **NEW** Overall codebase metrics
- **metrics-comparison.csv** - New code metrics comparison
- **severity-summary.csv** - Issue count by severity level
- **monthly-trend.csv** - Monthly issue growth trends (July-December 2025)
- **paper-payment-backend-issues.csv** - All issues with details (3,001 issues)
- **paper-document-issues.csv** - All issues with details (1,540 issues)

### JSON Data (for programmatic analysis)
- **paper-payment-backend-all-issues.json** - Complete raw data (3,001 issues)
- **paper-document-all-issues.json** - Complete raw data (1,540 issues)

## 🆕 What's New - Overall Code Metrics

The **OVERALL-CODE-SUMMARY.md** report now includes metrics for the entire codebase:

### Key Overall Metrics (paper-payment-backend)
- **Lines of Code:** 302,000
- **Test Coverage:** 31.6% ❌ (vs 40% for new code)
- **Duplications:** 3.8% ✅ (vs 3.21% for new code)
- **Bugs:** 1 (C rating)
- **Vulnerabilities:** 0 (A rating)
- **Code Smells:** 3,000 (A rating)
- **Security Hotspots:** 1 (A rating)

## 📈 Quick Comparison: Overall vs New Code

### paper-payment-backend

| Metric | Overall Codebase | New Code Only | Trend |
|--------|-----------------|---------------|-------|
| **Coverage** | 31.6% ❌ | 40.0% ⚠️ | ✅ Improving |
| **Duplications** | 3.8% ✅ | 3.21% ✅ | ✅ Improving |
| **Total Issues** | 3,001 | Subset | - |
| **Code Smells** | 3,000 | Subset | - |
| **Bugs** | 1 (C rating) | Subset | - |

**Key Insight:** New code quality is better than overall codebase, showing improvement in recent development practices.

## 🚀 Quick Start

### View Overall Code Summary
```bash
cat OVERALL-CODE-SUMMARY.md
```

### View New Code Summary
```bash
cat SUMMARY.md
```

### Open in Excel/Numbers
```bash
open overall-code-metrics.csv       # Overall codebase
open metrics-comparison.csv         # New code only
open monthly-trend.csv              # Trends
```

### Analyze with Python/Pandas
```python
import pandas as pd

# Load overall code metrics
overall = pd.read_csv('overall-code-metrics.csv')

# Load new code metrics
new_code = pd.read_csv('metrics-comparison.csv')

# Load trends
trends = pd.read_csv('monthly-trend.csv')

# Load all issues
issues = pd.read_csv('paper-payment-backend-issues.csv')

# Load JSON data
import json
with open('paper-payment-backend-all-issues.json', 'r') as f:
    issues_data = json.load(f)
```

### Query with jq
```bash
# Count critical issues
jq '[.[] | select(.severity == "CRITICAL")] | length' paper-payment-backend-all-issues.json

# List top 10 authors by issue count
jq -r '.[] | .author' paper-payment-backend-all-issues.json | sort | uniq -c | sort -rn | head -10

# Find issues created in December 2025
jq '[.[] | select(.creationDate | startswith("2025-12"))]' paper-payment-backend-all-issues.json

# Issues by component
jq 'group_by(.component) | map({component: .[0].component, count: length})' paper-payment-backend-all-issues.json | jq 'sort_by(-.count) | .[0:10]'
```

## 📊 Key Metrics Summary

### paper-payment-backend (Overall Codebase)
- **Total Issues:** 3,001
- **Quality Gate:** ❌ FAILED
- **Coverage:** 31.6% ❌ (need 80%)
- **Duplications:** 3.8% ✅ (threshold: 3%)
- **Bugs:** 1 (C rating)
- **Vulnerabilities:** 0 (A rating)
- **Code Smells:** 3,000 (A rating)
- **Lines of Code:** 302,000

### paper-document (Overall Codebase)
- **Total Issues:** 1,540
- **Quality Gate:** ❌ FAILED
- **Critical Issues:** 538
- **Info Issues:** 967

## 🎯 Critical Findings

### 🔴 Top Priority: Low Test Coverage
- **Current:** 31.6% (paper-payment-backend)
- **Target:** 80%
- **Gap:** 48.4 percentage points
- **Impact:** 61,000+ lines uncovered
- **Recommendation:** Increase coverage to 60% by Q2 2026

### 📈 Issue Growth Trend
- **paper-payment-backend:** +1,363 issues in 6 months (83% growth)
- **paper-document:** +184 issues in 6 months (14% growth)
- **Action:** Implement stricter quality gates in CI/CD

## 📅 Data Details

- **Source:** SonarQube Server (https://sonar.infra.paper.id)
- **Query Date:** 2026-01-26
- **Analysis Period:** July 2025 - January 2026
- **Query Method:** SonarQube MCP API
- **Scope:** 
  - Overall Code: Entire codebase (all historical code)
  - New Code: Recent changes only

## 🔍 Common Queries

### Overall Code Analysis

#### Find high complexity issues
```bash
jq '[.[] | select(.rule == "go:S3776")]' paper-payment-backend-all-issues.json | jq 'length'
```

#### Coverage gap analysis
```python
lines_of_code = 302000
lines_to_cover = 89000
coverage_pct = 31.6

covered_lines = int(lines_to_cover * (coverage_pct / 100))
uncovered_lines = lines_to_cover - covered_lines
target_coverage = 80

needed_coverage = int(lines_to_cover * (target_coverage / 100))
additional_tests_needed = needed_coverage - covered_lines

print(f"Covered: {covered_lines:,} lines")
print(f"Uncovered: {uncovered_lines:,} lines")
print(f"Need to cover {additional_tests_needed:,} more lines for 80% coverage")
```

#### Duplication analysis
```bash
duplicated_lines = 11476
total_lines = 302000
duplication_pct = $(echo "scale=2; $duplicated_lines / $total_lines * 100" | bc)
```

### Issues by creation date
```bash
jq 'group_by(.creationDate[:7]) | map({month: .[0].creationDate[:7], count: length}) | sort_by(.month)' paper-payment-backend-all-issues.json
```

### Top contributors to issues
```bash
jq -r '.[] | .author' paper-payment-backend-all-issues.json | sort | uniq -c | sort -rn | head -20
```

## 📝 Report Descriptions

### OVERALL-CODE-SUMMARY.md
Complete analysis of the entire codebase including:
- Overall code metrics (not just new code)
- Test coverage analysis (31.6% overall)
- Duplication analysis (3.8% overall)
- Bug, vulnerability, and code smell breakdown
- Recommendations for improving overall code quality

### SUMMARY.md
Analysis focused on new/recently changed code including:
- New code quality gates
- Recent issue trends
- Monthly growth patterns
- New code vs overall code comparison

## 📧 Understanding the Difference

### Overall Code Metrics
- Represents the **entire codebase** (all 302k lines)
- Includes all historical code
- Shows cumulative technical debt
- Use for: Overall health assessment, long-term planning

### New Code Metrics
- Represents **only recent changes**
- Focuses on code added/modified recently
- Shows current development quality
- Use for: PR quality gates, developer feedback, trend analysis

## 🛠️ Recommended Tools

- **Excel/Google Sheets** - For viewing CSV files
- **jq** - For querying JSON data
- **VS Code** - For viewing JSON/CSV files
- **Python/Pandas** - For data analysis
- **Tableau/PowerBI** - For data visualization
- **SonarLint** - IDE integration for real-time feedback

## 📧 Support

For questions about this data:
- DevOps Team
- Quality Assurance Team
- SonarQube Admin: https://sonar.infra.paper.id

---

**Last Updated:** 2026-01-26 11:46:00
**Total Files:** 18
**Total Size:** ~6MB

