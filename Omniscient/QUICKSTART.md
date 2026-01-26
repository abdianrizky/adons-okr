# Quick Start Guide - Omniscient OKR Analytics

## 1. Setup (One-time)

### Option A: Automatic Setup
```bash
cd omniscient
./setup.sh
```

### Option B: Manual Setup
```bash
cd omniscient

# Copy environment template
cp .env.example .env

# Install dependencies
pip3 install -r requirements.txt
```

## 2. Configure Database

Edit the `.env` file with your MySQL credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=omniscient
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Optional: Date range filter
START_DATE=2025-01-01
END_DATE=2025-12-31
```

## 3. Test Connection

Verify your database connection works:

```bash
python3 test_connection.py
```

Expected output:
```
========================================
🔌 Testing Omniscient Database Connection
========================================

📋 Checking configuration...
   ✓ DB_HOST: localhost
   ✓ DB_NAME: omniscient
   ✓ DB_USER: your_user
   ✓ DB_PASSWORD: ********
   ✓ DB_PORT: 3306

🔌 Attempting to connect...
   ✓ Connection successful!

📊 Fetching sample data...
   ✓ Found 150 PR records
   ✓ Date range: 2025-01-01 to 2025-12-31
   ✓ Contributors: 25
   ✓ Repositories: 8

========================================
✅ Database connection test successful!
========================================
```

## 4. Generate Report

Run the main script to generate your OKR report:

```bash
python3 gather_okr_metrics.py
```

### Common Options

```bash
# Full report (default)
python3 gather_okr_metrics.py

# Custom date range
python3 gather_okr_metrics.py --start-date 2025-01-01 --end-date 2025-06-30

# Only JSON output (faster)
python3 gather_okr_metrics.py --format json

# Only CSV output
python3 gather_okr_metrics.py --format csv

# Only Markdown report
python3 gather_okr_metrics.py --format markdown

# Skip chart generation (faster)
python3 gather_okr_metrics.py --no-charts

# Verbose output for debugging
python3 gather_okr_metrics.py -v
```

## 5. View Results

### Markdown Report
```bash
open reports/okr_report.md
```

### Charts
```bash
open output/pr_quality_trend.png
open output/score_distribution.png
open output/contributor_performance.png
open output/category_heatmap.png
open output/decision_breakdown.png
open output/monthly_pr_volume.png
```

### Data Exports
```bash
# JSON
cat output/okr_metrics.json

# CSV
open output/okr_pr_data.csv
```

## Example Output

When you run `gather_okr_metrics.py`, you'll see:

```
============================================================
🎯 Omniscient OKR Metrics Generator
============================================================

📋 Loading configuration...
   Database: omniscient @ localhost:3306
   Date Range: 2025-01-01 to 2025-12-31

📁 Setting up directories...
   ✓ Ensured directory: output/
   ✓ Ensured directory: data/
   ✓ Ensured directory: reports/

🔌 Connecting to database...
   ✓ Connected successfully

📊 Fetching PR data...
   ✓ Fetched 150 PR records

🧮 Calculating OKR metrics...
   ✓ Calculated metrics for 150 PRs
   ✓ Total contributors: 25
   ✓ Average overall score: 28.5

📈 Generating visualizations...
   ✓ Generated: output/pr_quality_trend.png
   ✓ Generated: output/score_distribution.png
   ✓ Generated: output/contributor_performance.png
   ✓ Generated: output/category_heatmap.png
   ✓ Generated: output/decision_breakdown.png
   ✓ Generated: output/monthly_pr_volume.png

📝 Generating reports...
   ✓ Generated: output/okr_metrics.json
   ✓ Generated: output/okr_pr_data.csv
   ✓ Generated: reports/okr_report.md

============================================================
✅ OKR Report Generated Successfully!
============================================================

📂 Generated files:
   • output/okr_metrics.json
   • output/okr_pr_data.csv
   • reports/okr_report.md

📊 View charts in: output/

🎉 Done!
```

## Troubleshooting

### Connection Error
```
❌ Database error: (2003, "Can't connect to MySQL server...")
```

**Solution:**
1. Verify MySQL is running: `mysql.server status`
2. Check credentials in `.env`
3. Test MySQL connection: `mysql -h localhost -u your_user -p omniscient`

### No Data Found
```
⚠️  No data found for the specified date range
```

**Solution:**
1. Check date range in `.env` or command line args
2. Verify data exists: `SELECT COUNT(*) FROM pr_scores;`
3. Remove date filters to see all data

### Import Error
```
ModuleNotFoundError: No module named 'pymysql'
```

**Solution:**
```bash
pip3 install -r requirements.txt
```

### Permission Denied
```
PermissionError: [Errno 13] Permission denied: 'output/...'
```

**Solution:**
```bash
chmod -R 755 output/ data/ reports/
```

## Next Steps

1. Review the markdown report in `reports/okr_report.md`
2. Share visualizations from `output/` folder
3. Use JSON/CSV exports for further analysis
4. Schedule regular report generation (weekly/monthly)
5. Set up automated reporting with cron jobs

## Automation Example

Add to crontab for weekly reports:

```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /Users/adon/paperid/adons-okr/omniscient && python3 gather_okr_metrics.py
```

## Support

For issues or questions:
- Check the main [README.md](./README.md)
- Review the [paper-omniscient source](/Users/adon/paperid/paper-omniscient)
- Check database schema in [paper-omniscient/pr-label](../../paper-omniscient/pr-label)

---

Happy analyzing! 🎯📊
