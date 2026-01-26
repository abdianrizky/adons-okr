#!/usr/bin/env python3
"""Test script for new sprint timeline gantt chart"""

from datetime import datetime
from src.report_generator import ReportGenerator
from src.metrics_calculator import SprintMetrics, Task


def create_mock_sprint(sprint_num, name, start_date, end_date,
                       points_committed, points_delivered, total_work):
    """Create a mock SprintMetrics object for testing"""

    # Create mock tasks
    tasks = []
    for i in range(3):
        task = Task(
            task_id=f"task_{sprint_num}_{i}",
            name=f"Task {i+1}",
            url=f"https://example.com/task_{sprint_num}_{i}",
            status="complete" if i < 2 else "in progress",
            points=points_committed // 3 if i < 2 else points_committed - (2 * (points_committed // 3)),
            is_completed=True if i < 2 else False
        )
        tasks.append(task)

    # Convert date strings to timestamps
    start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)

    metrics = SprintMetrics(
        sprint_number=sprint_num,
        sprint_name=name,
        week=27 + (sprint_num - 43) * 2,  # Mock week numbers
        list_id=f"list_{sprint_num}",
        url=f"https://app.clickup.com/sprint/{sprint_num}",
        total_tasks=len(tasks),
        completed_tasks_count=len([t for t in tasks if t.status == "complete"]),
        points_committed=points_committed,
        carryover_in=0,
        points_delivered=points_delivered,
        carryover_out=total_work - points_delivered,
        total_work=total_work,
        burndown=total_work - points_delivered,
        delivery_rate=(points_delivered / total_work * 100) if total_work > 0 else 0,
        all_tasks=tasks,
        completed_tasks=[t for t in tasks if t.status == "complete"],
        carryover_in_tasks=[],
        carryover_out_tasks=[],
        sprint_start_date=start_ts,
        sprint_end_date=end_ts,
        sprint_reporting_url=f"https://app.clickup.com/reporting/sprint/{sprint_num}"
    )

    return metrics


def main():
    """Test the new sprint timeline gantt chart"""

    print("Testing Sprint Timeline Gantt Chart")
    print("=" * 60)

    # Create mock sprint data
    mock_sprints = [
        create_mock_sprint(43, "Sprint 43 (Payment)", "2025-07-08", "2025-07-22", 11, 11, 11),
        create_mock_sprint(44, "Sprint 44 (Payment)", "2025-07-23", "2025-08-05", 15, 15, 15),
        create_mock_sprint(45, "Sprint 45 (Payment)", "2025-08-06", "2025-08-19", 13, 13, 13),
        create_mock_sprint(46, "Sprint 46 (Payment)", "2025-08-20", "2025-09-02", 14, 10, 14),
        create_mock_sprint(47, "Sprint 47 (Payment)", "2025-09-03", "2025-09-16", 12, 12, 12),
    ]

    # Create report generator
    generator = ReportGenerator(output_dir='output')

    # Generate the new sprint timeline gantt
    print("\nGenerating Sprint Timeline Gantt Chart...")
    print("-" * 60)

    gantt_output = generator._generate_sprint_timeline_gantt(mock_sprints)

    print("\n" + gantt_output)
    print("\n" + "=" * 60)
    print("✅ Sprint Timeline Gantt chart generated successfully!")
    print("\nColor coding:")
    print("  🟢 Green (done)   = Perfect delivery (≥100%)")
    print("  🔵 Blue (active)  = Good performance (≥75%)")
    print("  🔴 Red (crit)     = Needs attention (<75%)")
    print("\nThis gantt chart shows all sprints as timeline items,")
    print("not individual tasks, providing an overview of sprint performance.")


if __name__ == "__main__":
    main()
