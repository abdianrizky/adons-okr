# SonarQube MCP Coverage Graph Analysis

**Date:** 2026-01-26
**Request:** Add coverage graph similar to SonarQube UI showing coverage trends over time

---

## 🔍 Investigation Results

### What the SonarQube UI Uses

The coverage graph shown in your screenshot (with "Lines to Cover" and "Covered Lines" over time) uses this API:

```
GET /api/measures/search_history
```

**Endpoint URL:**
```
https://sonar.infra.paper.id/api/measures/search_history?
  component=paper-payment-backend&
  metrics=coverage,lines_to_cover,uncovered_lines&
  from=2025-07-01&
  to=2025-12-31
```

**Response Format:**
```json
{
  "paging": {...},
  "measures": [
    {
      "metric": "coverage",
      "history": [
        {"date": "2025-07-01T00:00:00+0000", "value": "22.1"},
        {"date": "2025-07-04T01:00:00+0000", "value": "22.1"},
        {"date": "2025-08-01T00:00:00+0000", "value": "23.5"},
        ...
      ]
    },
    {
      "metric": "lines_to_cover",
      "history": [
        {"date": "2025-07-01T00:00:00+0000", "value": "71563"},
        ...
      ]
    }
  ]
}
```

---

## ❌ MCP Limitation Found

### Current SonarQube MCP Tools

The SonarQube MCP currently has these tools:

**✅ Available:**
- `get_system_health` - System health status
- `get_system_info` - System configuration
- `get_system_status` - System status
- `search_my_sonarqube_projects` - List projects
- `search_sonar_issues_in_projects` - Search issues
- `get_project_quality_gate_status` - Quality gate status
- `show_rule` - Rule details
- `list_rule_repositories` - List repositories
- `list_quality_gates` - List quality gates
- `list_languages` - List languages
- `get_component_measures` - Get measures (point-in-time)
- `search_metrics` - Search available metrics
- `get_scm_info` - SCM info
- `get_raw_source` - Source code
- `create_webhook` - Create webhook
- `list_webhooks` - List webhooks
- `list_portfolios` - List portfolios
- `analyze_code_snippet` - Analyze code

**❌ Missing:**
- `search_history` or `measures_history` - **NOT AVAILABLE**

### Impact

**Cannot fetch historical/time-series data through the MCP**, including:
- Coverage trends over time
- Duplication trends
- Issue count trends
- Any metric history

The `get_component_measures` tool only returns **current/latest** values, not historical data.

### Additional Issue

The `get_component_measures` tool also returns **permission errors** in our setup:
```
Error: SonarQube answered with Insufficient privileges
```

This suggests the MCP's authentication token doesn't have the required permissions for the measures API.

---

## ✅ Solution Provided

Since the MCP doesn't have the `search_history` endpoint, I created Python scripts that directly call the SonarQube API.

### Files Created

| File | Purpose |
|------|---------|
| `fetch-coverage-history.py` | Fetches historical coverage data from `/api/measures/search_history` |
| `visualize-coverage.py` | Creates ASCII graphs, markdown tables, and HTML charts |
| `generate-coverage-graph.sh` | Wrapper script to run everything |
| `COVERAGE-GRAPH-README.md` | Complete documentation and usage guide |

### Usage

```bash
# Set authentication token
export SONAR_TOKEN="your-sonarqube-token"

# Generate coverage graph
./generate-coverage-graph.sh paper-payment-backend 2025-07-01 2025-12-31
```

**Output:**
- CSV file with historical data
- JSON file with raw API response
- ASCII graph in terminal
- Interactive HTML chart with Chart.js

---

## 🎯 Comparison: MCP vs Direct API

| Feature | SonarQube MCP | Direct API Call |
|---------|---------------|-----------------|
| **Current measures** | ❌ Permission error | ✅ Works with token |
| **Historical data** | ❌ Not available | ✅ Available via `/api/measures/search_history` |
| **Issue search** | ✅ Works | ✅ Works |
| **Quality gate** | ✅ Works | ✅ Works |
| **Projects list** | ✅ Works | ✅ Works |
| **Authentication** | Automatic (but limited permissions) | Requires SONAR_TOKEN |

---

## 📋 Recommendations

### Short-term (Immediate)

Use the provided Python scripts:
1. Get a SonarQube token from: https://sonar.infra.paper.id → My Account → Security
2. Export it: `export SONAR_TOKEN="your-token"`
3. Run: `./generate-coverage-graph.sh paper-payment-backend 2025-07-01 2025-12-31`

### Mid-term (Next Sprint)

**Option 1: Extend the MCP**

Add `search_history` tool to the SonarQube MCP:

```python
@tool()
def search_history(
    component: str,
    metrics: List[str],
    from_date: str,
    to_date: str
) -> Dict:
    """Get historical measures for a component over time"""
    url = f"{SONAR_URL}/api/measures/search_history"
    params = {
        "component": component,
        "metrics": ",".join(metrics),
        "from": from_date,
        "to": to_date
    }
    response = requests.get(url, params=params, headers=auth_headers)
    return response.json()
```

**Option 2: Fix MCP Permissions**

Grant the MCP's authentication token the required permissions for `get_component_measures`.

### Long-term

1. **Automate:** Add coverage graph generation to CI/CD
2. **Dashboard:** Create a dashboard showing trends for both projects
3. **Alerts:** Set up alerts when coverage drops
4. **Reports:** Include coverage graphs in sprint reports

---

## 📊 Expected Output

### Example Coverage Graph Data

```csv
date,coverage,lines_to_cover,uncovered_lines,covered_lines
2025-07-01T00:00:00+0000,22.1,71563,55731,15832
2025-07-04T01:00:00+0000,22.1,71563,55731,15832
2025-08-01T00:00:00+0000,23.5,72100,55157,16943
2025-09-01T00:00:00+0000,25.2,73500,54978,18522
2025-10-01T00:00:00+0000,27.8,75200,54294,20906
2025-11-01T00:00:00+0000,29.5,78100,55081,23019
2025-12-01T00:00:00+0000,31.6,89000,60876,28124
```

### Visualization

The scripts will generate:

1. **ASCII Graph** (terminal output)
```
================================================================================
COVERAGE TREND
================================================================================
 35.0% |                                                                    ━●
 30.0% |                                                          ━●━━━━━━━━
 25.0% |                                            ━●━━━━━━━━━━━━
 20.0% |                              ━●━━━━━━━━━━━━
 15.0% |                ━●━━━━━━━━━━━━
        ────────────────────────────────────────────────────────────────────
        Jul 2025 → Dec 2025
```

2. **HTML Interactive Chart**
   - Line chart with Chart.js
   - Hover tooltips showing exact values
   - Responsive design
   - Stats cards with current values

3. **Markdown Table**
   - Coverage percentage over time
   - Lines to cover vs covered lines
   - Ready for reports

---

## 🔗 Related Documentation

- **SonarQube API Docs:** https://docs.sonarsource.com/sonarqube/latest/extension-guide/web-api/
- **Measures API:** `/api/measures/search_history`
- **Current Reports:**
  - `OVERALL-CODE-SUMMARY.md` - Overall code analysis
  - `PROJECT-LINKS.md` - Dashboard links
  - `COVERAGE-GRAPH-README.md` - Coverage graph documentation

---

## 📝 Summary

**Question:** "Can we add coverage graph like the SonarQube UI?"

**Answer:**
- ❌ The SonarQube MCP **does not have** the `search_history` endpoint
- ✅ I've created Python scripts that directly call the API
- ✅ These scripts work with a SonarQube authentication token
- 🔧 The MCP could be extended to include this functionality

**Next Step:** Use the provided scripts with your SONAR_TOKEN to generate coverage graphs.

---

**Generated:** 2026-01-26
**Location:** `/Users/adon/paperid/adons-okr/sonarqube-analytics/`
