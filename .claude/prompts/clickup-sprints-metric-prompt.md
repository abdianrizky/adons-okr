# Claude Code Prompt: ClickUp Sprint Metrics Analysis & Visualization

## Context
I need to gather sprint metrics from ClickUp for H2 2025 (Sprint 43-50) in the SMB - Payment folder and create visualizations for OKR reporting.

## Requirements

### 1. Data Collection
Create a Python script that:
- Connects to ClickUp API using the workspace API token
- Fetches all tasks for each sprint (Sprint 43-50) assigned to user Adon (user_id: 60603760)
- Collects the following data for each task:
  - Task name
  - Points (from custom field or task.points)
  - Status
  - Sprint list ID
  - URL

### 2. Metrics Calculation
For each sprint, calculate:
- **Points Committed**: Sum of all points for tasks originally in that sprint
- **Carryover In**: Points from tasks that were moved from previous sprint
- **Points Delivered**: Sum of points for tasks with status containing "deployed" or "done"
- **Carryover Out**: Points from tasks moved to next sprint (not completed)
- **Burndown**: Total Work - Points Delivered

### 3. Data Structure

```python
sprints = {
    "Sprint 43 - 2.36": {
        "list_id": "901609751709",
        "week": 36,
        "url": "https://app.clickup.com/3708016/v/li/901609751709"
    },
    "Sprint 44 - 2.37": {
        "list_id": "901610062693",
        "week": 37,
        "url": "https://app.clickup.com/3708016/v/li/901610062693"
    },
    "Sprint 45 - 2.38": {
        "list_id": "901610251697",
        "week": 38,
        "url": "https://app.clickup.com/3708016/v/li/901610251697"
    },
    "Sprint 46 - 2.39": {
        "list_id": "901610523078",
        "week": 39,
        "url": "https://app.clickup.com/3708016/v/li/901610523078"
    },
    "Sprint 47 - 2.40": {
        "list_id": "901610830843",
        "week": 40,
        "url": "https://app.clickup.com/3708016/v/li/901610830843"
    },
    "Sprint 48 - 2.41": {
        "list_id": "901611066339",
        "week": 41,
        "url": "https://app.clickup.com/3708016/v/li/901611066339"
    },
    "Sprint 49 - 2.42": {
        "list_id": "901611303982",
        "week": 42,
        "url": "https://app.clickup.com/3708016/v/li/901611303982"
    },
    "Sprint 50 - 2.43": {
        "list_id": "901611529803",
        "week": 43,
        "url": "https://app.clickup.com/3708016/v/li/901611529803"
    }
}

# ClickUp API Configuration
WORKSPACE_ID = "3708016"
USER_ID = 60603760  # Adon
FOLDER_ID = "90160117762"  # SMB - Payment folder
API_TOKEN = os.getenv("CLICKUP_API_TOKEN")  # Get from environment variable
```

### 4. API Endpoints to Use

```python
# Search tasks in a specific list for a specific user
GET https://api.clickup.com/api/v2/list/{list_id}/task
Headers:
  Authorization: {api_token}
Query params:
  assignees[]={user_id}
  include_closed=true
  
# Alternative: Use search endpoint
POST https://api.clickup.com/api/v2/team/{workspace_id}/search
Body:
{
  "filters": {
    "location": {
      "subcategories": ["{list_id}"]
    },
    "assignees": [60603760]
  }
}
```

### 5. Visualization Requirements

Create the following charts using matplotlib/plotly:

#### A. Sprint Velocity Chart (Bar Chart)
- X-axis: Sprint names (Sprint 43 - Sprint 50)
- Y-axis: Points
- Bars: 
  - Points Committed (blue)
  - Points Delivered (green)
  - Carryover (orange)

#### B. Burndown Trend (Line Chart)
- X-axis: Sprint names
- Y-axis: Points remaining
- Line showing burndown trend across sprints

#### C. Delivery Rate (%)
- X-axis: Sprint names
- Y-axis: Percentage (0-100%)
- Formula: (Points Delivered / (Points Committed + Carryover In)) * 100

#### D. Summary Table
Create a summary table showing:
```
| Sprint | Points Committed | Carryover In | Points Delivered | Carryover Out | Delivery Rate |
|--------|-----------------|--------------|------------------|---------------|---------------|
| Sprint 43 | X | Y | Z | W | %  |
| ...
```

### 6. Output Format

Generate:
1. `sprint_metrics.json` - Raw data in JSON format
2. `sprint_metrics.csv` - CSV format for easy import
3. `sprint_velocity_chart.png` - Velocity visualization
4. `burndown_chart.png` - Burndown trend
5. `delivery_rate_chart.png` - Delivery rate over time
6. `sprint_summary.md` - Markdown report with all metrics and insights

### 7. Additional Requirements

- Handle rate limiting (ClickUp API: 100 requests/minute)
- Cache API responses to avoid repeated calls
- Error handling for missing data or API failures
- Add retry logic with exponential backoff
- Log all API calls for debugging
- Support dry-run mode to test without making API calls

### 8. Example Output Structure

```markdown
# H2 2025 Sprint Metrics - SMB Payment Team
## Summary
- Total Sprints: 8
- Total Points Committed: XXX
- Total Points Delivered: XXX
- Average Delivery Rate: XX%
- Total Carryover: XXX

## Sprint-by-Sprint Breakdown

### Sprint 43 - 2.36 (Week 36)
- Points Committed: 11
- Carryover In: 8
- Points Delivered: 19
- Carryover Out: 0
- Delivery Rate: 100%

**Tasks Completed:**
1. [Pivot][BE] Validate Payment (3 pts)
2. [Pivot][BE] Request 3DS (3 pts)
3. [Pivot][BE] Pivot Callback (5 pts)
...
```

### 9. Usage

```bash
# Install dependencies
pip install clickup-python-sdk requests matplotlib pandas plotly

# Set API token
export CLICKUP_API_TOKEN="your_token_here"

# Run the script
python gather_sprint_metrics.py

# Options
python gather_sprint_metrics.py --dry-run  # Test without API calls
python gather_sprint_metrics.py --cache    # Use cached data
python gather_sprint_metrics.py --output-dir ./reports  # Custom output directory
```

### 10. Success Criteria

- ✅ All 8 sprints data collected successfully
- ✅ Accurate metrics calculation (verified against ClickUp UI)
- ✅ Clear, professional visualizations
- ✅ Easy to read summary report
- ✅ Exportable data (JSON, CSV)
- ✅ Script is reusable for future sprints

## Notes
- Sprint 51, 52, 53 exist but have no tasks assigned to Adon
- Status "8.0 deployed" means task is completed
- Some tasks may have been moved between sprints (carryover)
- Points field might be in task.points or in custom fields

## Expected Deliverables
1. `gather_sprint_metrics.py` - Main script
2. `config.yaml` - Configuration file
3. `requirements.txt` - Python dependencies
4. `README.md` - Usage instructions
5. All visualization files mentioned above
6. Summary report in markdown format