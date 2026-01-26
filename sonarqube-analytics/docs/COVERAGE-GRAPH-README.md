# Coverage Graph Generation

## 🎯 Objective

Generate coverage history graphs similar to the SonarQube UI, showing:
- Lines to Cover (solid line)
- Covered Lines (dotted line)
- Coverage percentage over time
- New Code area (shaded)

## 📊 SonarQube API for Coverage Graphs

The SonarQube frontend uses this API endpoint for coverage graphs:

```
GET /api/measures/search_history
```

**Parameters:**
- `component`: Project key (e.g., `paper-payment-backend`)
- `metrics`: Comma-separated metrics (e.g., `coverage,lines_to_cover,uncovered_lines`)
- `from`: Start date (YYYY-MM-DD)
- `to`: End date (YYYY-MM-DD)

**Example:**
```bash
https://sonar.infra.paper.id/api/measures/search_history?\
  component=paper-payment-backend&\
  metrics=coverage,lines_to_cover,uncovered_lines&\
  from=2025-07-01&\
  to=2025-12-31
```

## ⚠️ MCP Limitation

**Current Issue:** The SonarQube MCP **does NOT have** the `search_history` endpoint implemented.

**Available MCP Tools:**
- ✅ `get_component_measures` - Single point-in-time measures (has permission issues)
- ✅ `search_metrics` - List available metrics
- ✅ `search_sonar_issues_in_projects` - Search issues
- ❌ `search_history` - **NOT AVAILABLE**

**Impact:** We cannot fetch historical/time-series coverage data through the MCP.

## 🛠️ Solution

I've created Python scripts that directly call the SonarQube API to fetch and visualize coverage history.

### Files Created

1. **fetch-coverage-history.py** - Fetches historical data from SonarQube API
2. **visualize-coverage.py** - Creates ASCII, markdown, and HTML charts
3. **generate-coverage-graph.sh** - Wrapper script to run everything

## 📖 Usage

### Quick Start

```bash
# Set your SonarQube token (required for authentication)
export SONAR_TOKEN="your-sonarqube-token-here"

# Generate coverage graph
./generate-coverage-graph.sh paper-payment-backend 2025-07-01 2025-12-31
```

### Step-by-Step

#### 1. Get SonarQube Token

You need a SonarQube authentication token:

1. Go to https://sonar.infra.paper.id
2. Login
3. Go to: User Menu → My Account → Security
4. Generate a new token
5. Export it: `export SONAR_TOKEN="your-token"`

#### 2. Fetch Coverage History

```bash
python3 fetch-coverage-history.py paper-payment-backend 2025-07-01 2025-12-31
```

**Output:**
- `paper-payment-backend-coverage-history.csv` - Coverage data
- `paper-payment-backend-coverage-history.json` - Raw API response

#### 3. Visualize the Data

```bash
python3 visualize-coverage.py paper-payment-backend-coverage-history.csv
```

**Output:**
- ASCII graph in terminal
- Markdown table
- `paper-payment-backend-coverage-history.html` - Interactive HTML chart

#### 4. Open the HTML Chart

```bash
open paper-payment-backend-coverage-history.html
```

## 📊 Output Examples

### CSV Format

```csv
date,coverage,lines_to_cover,uncovered_lines,covered_lines
2025-07-01T00:00:00+0000,22.1,71563,55731,15832
2025-08-01T00:00:00+0000,23.5,72100,55157,16943
2025-09-01T00:00:00+0000,25.2,73500,54978,18522
...
```

### ASCII Graph

```
================================================================================
COVERAGE TREND
================================================================================
 35.0% |                                                                    ━●
 30.0% |                                                          ━●━━━━━━━━
 25.0% |                                            ━●━━━━━━━━━━━━
 20.0% |                              ━●━━━━━━━━━━━━
 15.0% |                ━●━━━━━━━━━━━━
 10.0% |  ━●━━━━━━━━━━━━
  5.0% |
  0.0% |
        ────────────────────────────────────────────────────────────────────
        Jul 01, 2025 → Dec 31, 2025

  Start: 22.10%
  End:   31.60%
  Change: +9.50pp
```

### HTML Chart

Interactive Chart.js visualization with:
- Line chart showing coverage trend
- Dual-axis chart for lines to cover vs covered lines
- Hover tooltips
- Responsive design
- Stats cards

## 🔧 Troubleshooting

### Error: "Insufficient privileges"

**Problem:** MCP `get_component_measures` returns permission error

**Solution:** Use the Python scripts with your own SONAR_TOKEN

### Error: "401 Unauthorized"

**Problem:** SONAR_TOKEN not set or invalid

**Solution:**
```bash
export SONAR_TOKEN="your-valid-token"
```

### Error: "No data found"

**Problem:** The API returned empty results

**Possible causes:**
- Project key is wrong
- Date range has no data
- No analysis runs in that period

**Solution:** Check project key and date range

### Error: "requests module not found"

**Problem:** Python requests library not installed

**Solution:**
```bash
pip3 install requests
```

## 🚀 Extending the MCP

To add the `search_history` endpoint to the SonarQube MCP, you would need to:

1. **Modify the MCP Server** to add a new tool:
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

2. **Update MCP Schema** to include the new tool definition

3. **Test** with your SonarQube instance

## 📈 Metrics Available

Common metrics for coverage graphs:

- `coverage` - Coverage percentage
- `lines_to_cover` - Total lines to cover
- `uncovered_lines` - Lines without coverage
- `line_coverage` - Line coverage percentage
- `branch_coverage` - Branch coverage percentage
- `conditions_to_cover` - Total conditions to cover
- `uncovered_conditions` - Conditions without coverage

## 🔗 References

- **SonarQube API Docs:** https://docs.sonarsource.com/sonarqube/latest/extension-guide/web-api/
- **Measures API:** `/api/measures/search_history`
- **SonarQube Dashboard:** https://sonar.infra.paper.id
- **Project Dashboard:** https://sonar.infra.paper.id/dashboard?id=paper-payment-backend&codeScope=overall

## 📝 Next Steps

### For Both Projects

Run for both projects:

```bash
# paper-payment-backend
./generate-coverage-graph.sh paper-payment-backend 2025-07-01 2025-12-31

# paper-document
./generate-coverage-graph.sh paper-document 2025-07-01 2025-12-31
```

### Integration with Reports

Once you have the CSV data, you can:

1. **Add to OVERALL-CODE-SUMMARY.md**
   - Include coverage trend graph
   - Show historical progression

2. **Create Comparison Chart**
   - Compare both projects side-by-side
   - Show which project is improving faster

3. **Add to Sprint Reports**
   - Track coverage improvement per sprint
   - Set targets based on historical trends

## 💡 Pro Tips

1. **Automate:** Add to CI/CD to generate weekly coverage reports
2. **Alert:** Set up alerts when coverage drops below threshold
3. **Track:** Monitor coverage trend alongside issue growth
4. **Compare:** Generate graphs for both projects to compare improvement rates

---

**Generated:** 2026-01-26
**Location:** `/Users/adon/paperid/adons-okr/sonarqube-analytics/`
