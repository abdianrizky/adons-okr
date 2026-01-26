# Quick Start: Generate Coverage Graph

## 🎯 Goal
Generate a coverage graph like the SonarQube UI showing coverage trends over time.

## ⚡ Quick Start (3 Steps)

### Step 1: Get Your SonarQube Token

1. Go to https://sonar.infra.paper.id
2. Click your profile → **My Account** → **Security**
3. Generate a new token
4. Copy the token

### Step 2: Set the Token

```bash
export SONAR_TOKEN="your-token-here"
```

### Step 3: Generate the Graph

```bash
cd /Users/adon/paperid/adons-okr/sonarqube-analytics

# For paper-payment-backend
./generate-coverage-graph.sh paper-payment-backend 2025-07-01 2025-12-31

# For paper-document
./generate-coverage-graph.sh paper-document 2025-07-01 2025-12-31
```

## 📊 Output

You'll get:

1. **CSV File** - Coverage data over time
   - `paper-payment-backend-coverage-history.csv`

2. **JSON File** - Raw API response
   - `paper-payment-backend-coverage-history.json`

3. **HTML Chart** - Interactive visualization
   - `paper-payment-backend-coverage-history.html`
   - Open with: `open paper-payment-backend-coverage-history.html`

4. **Terminal Output** - ASCII graph and stats

## 🔍 Why Not Use MCP?

**Finding:** The SonarQube MCP **does not have** the `search_history` endpoint needed for historical/time-series data.

**Available in MCP:**
- ✅ Issue search
- ✅ Quality gate status
- ✅ Project list
- ❌ Historical measures (coverage trends)

**Solution:** Direct API calls using Python scripts (provided).

## 📖 More Info

- **Full Documentation:** `COVERAGE-GRAPH-README.md`
- **MCP Analysis:** `MCP-FINDINGS.md`
- **All Files:** `INDEX.md`

---

**Generated:** 2026-01-26
