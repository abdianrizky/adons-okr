"""Sprint metrics calculation"""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

from .carryover_detector import CarryoverDetector


@dataclass
class Task:
    """Task data structure"""
    task_id: str
    name: str
    url: str
    status: str
    points: int
    is_completed: bool


@dataclass
class SprintMetrics:
    """Sprint metrics data structure"""
    sprint_number: int
    sprint_name: str
    week: int
    list_id: str
    url: str

    # Raw counts
    total_tasks: int
    completed_tasks_count: int

    # Points metrics
    points_committed: int      # Total points in sprint
    carryover_in: int         # Points from previous sprint
    points_delivered: int     # Points completed
    carryover_out: int        # Points not completed
    total_work: int           # committed + carryover_in
    burndown: int             # total_work - delivered

    # Calculated metrics
    delivery_rate: float      # (delivered / total_work) * 100

    # Task lists (must come before optional fields)
    all_tasks: List[Task]
    completed_tasks: List[Task]
    carryover_in_tasks: List[Dict]
    carryover_out_tasks: List[Dict]

    # Sprint dates (milliseconds timestamp) - optional fields at end
    sprint_start_date: Optional[int] = None
    sprint_end_date: Optional[int] = None

    # Daily burndown data: date -> remaining points (History-Based Approach)
    daily_completion: Optional[Dict[str, int]] = None

    # Sprint Reporting dashboard URL - optional
    sprint_reporting_url: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert Task objects to dicts
        data['all_tasks'] = [asdict(t) for t in self.all_tasks]
        data['completed_tasks'] = [asdict(t) for t in self.completed_tasks]
        return data


class SprintMetricsCalculator:
    """Calculate sprint metrics with carryover detection"""

    def __init__(
        self,
        all_sprints_data: Dict[int, List[Dict]],
        sprint_configs: List[Dict],
        completion_keyword: str = "deployed",
        clickup_client = None
    ):
        """Initialize metrics calculator

        Args:
            all_sprints_data: Dict mapping sprint_number -> list of tasks
            sprint_configs: List of sprint configuration dicts
            completion_keyword: Keyword to identify completed tasks
            clickup_client: ClickUpClient instance for fetching sprint/task details
        """
        self.all_sprints_data = all_sprints_data
        self.sprint_configs = sprint_configs
        self.completion_keyword = completion_keyword
        self.clickup_client = clickup_client
        self.logger = logging.getLogger('sprint_analytics.metrics')

        # Initialize carryover detector
        self.carryover_detector = CarryoverDetector(
            all_sprints_data,
            completion_keyword
        )

    def _extract_points(self, task: Dict) -> int:
        """Extract story points from task

        Args:
            task: Task dictionary

        Returns:
            Story points (0 if not found)
        """
        # Check direct points field
        if 'points' in task and task['points'] is not None:
            try:
                return int(task['points'])
            except (ValueError, TypeError):
                pass

        # Check custom fields
        custom_fields = task.get('custom_fields', [])
        for field in custom_fields:
            if field.get('name', '').lower() == 'points':
                value = field.get('value')
                if value is not None:
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        pass

        return 0

    def _get_task_status(self, task: Dict) -> str:
        """Extract status from task

        Args:
            task: Task dictionary

        Returns:
            Status string
        """
        status = task.get('status', {})
        if isinstance(status, dict):
            return status.get('status', '')
        return str(status)

    def _is_task_completed(self, status: str) -> bool:
        """Check if task is completed

        Args:
            status: Task status string

        Returns:
            True if status contains completion keyword
        """
        return self.completion_keyword.lower() in status.lower()

    def _convert_to_task(self, task_dict: Dict) -> Task:
        """Convert task dict to Task object

        Args:
            task_dict: Task dictionary from API

        Returns:
            Task object
        """
        status = self._get_task_status(task_dict)
        return Task(
            task_id=task_dict.get('id', ''),
            name=task_dict.get('name', ''),
            url=task_dict.get('url', ''),
            status=status,
            points=self._extract_points(task_dict),
            is_completed=self._is_task_completed(status)
        )

    def _build_daily_snapshots(
        self,
        sprint_tasks: List[Dict],
        sprint_start: int,
        sprint_end: int
    ) -> Dict[str, Dict]:
        """Build daily status snapshots for all tasks (History-Based Approach)

        Args:
            sprint_tasks: List of task dictionaries
            sprint_start: Sprint start timestamp (ms)
            sprint_end: Sprint end timestamp (ms)

        Returns:
            Dictionary mapping date -> task_id -> {name, points, status}
        """
        from datetime import datetime, timedelta

        if not self.clickup_client or not sprint_start or not sprint_end:
            return {}

        # Convert timestamps to dates
        try:
            start_ts = int(sprint_start) if isinstance(sprint_start, str) else sprint_start
            end_ts = int(sprint_end) if isinstance(sprint_end, str) else sprint_end
            start_date = datetime.fromtimestamp(start_ts / 1000)
            end_date = datetime.fromtimestamp(end_ts / 1000)
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to parse sprint dates: {e}")
            return {}

        # Extract task IDs and build task info map
        task_ids = []
        task_info = {}

        for task in sprint_tasks:
            task_id = task.get('id')
            if not task_id:
                continue

            points = self._extract_points(task)
            task_ids.append(task_id)
            task_info[task_id] = {
                'name': task.get('name', ''),
                'points': points
            }

        if not task_ids:
            return {}

        # Fetch bulk time in status for all tasks (EFFICIENT!)
        self.logger.info(f"Fetching time_in_status for {len(task_ids)} tasks")
        bulk_status_data = self.clickup_client.get_bulk_time_in_status(task_ids)

        # Build snapshot for each day in sprint
        daily_snapshots = {}
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_snapshots[date_str] = {}

            # For each task, determine its status on this date
            for task_id in task_ids:
                status = self._get_task_status_on_date_from_history(
                    bulk_status_data.get(task_id, {}),
                    current_date
                )

                daily_snapshots[date_str][task_id] = {
                    'name': task_info[task_id]['name'],
                    'points': task_info[task_id]['points'],
                    'status': status
                }

            current_date += timedelta(days=1)

        return daily_snapshots

    def _get_task_status_on_date_from_history(
        self,
        time_in_status_data: Dict,
        target_date: datetime
    ) -> str:
        """Find task status on specific date from time_in_status API data

        Args:
            time_in_status_data: Data from bulk_time_in_status API
                Format: {current_status: {...}, status_history: [{status, since, ...}, ...]}
            target_date: Target date to check

        Returns:
            Status string on that date
        """
        from datetime import datetime

        if not time_in_status_data:
            return 'not started'

        status_history = time_in_status_data.get('status_history', [])
        current_status = time_in_status_data.get('current_status', {})

        if not status_history:
            # No history, use current status
            return current_status.get('status', 'unknown')

        # Convert target to timestamp (ms)
        target_ts = int(target_date.timestamp() * 1000)

        # Find the latest status change before or on target_date
        # status_history is sorted by time (earliest first)
        active_status = None

        for status_entry in status_history:
            # 'since' is nested in 'total_time' object
            total_time = status_entry.get('total_time', {})
            since_ts = total_time.get('since')

            if not since_ts:
                continue

            try:
                since = int(since_ts) if isinstance(since_ts, str) else since_ts

                # If this status started before or on target date, it was active
                if since <= target_ts:
                    active_status = status_entry.get('status', '')
                else:
                    # Future status change, stop here
                    break

            except (ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse since timestamp: {e}")
                continue

        # Return the active status or 'not started'
        return active_status or 'not started'

    def _calculate_daily_burndown(self, daily_snapshots: Dict) -> Dict[str, int]:
        """Calculate remaining work per day from daily snapshots

        Args:
            daily_snapshots: Daily status snapshots

        Returns:
            Dictionary mapping date -> remaining points
        """
        burndown_data = {}

        for date_str, tasks in sorted(daily_snapshots.items()):
            # Total points in sprint
            total_points = sum(task['points'] for task in tasks.values())

            # Completed points (deployed status)
            completed_points = sum(
                task['points']
                for task in tasks.values()
                if self._is_task_completed(task['status'])
            )

            # Remaining work = Total - Completed
            remaining = total_points - completed_points

            burndown_data[date_str] = remaining

        return burndown_data

    def calculate_sprint_metrics(self, sprint_num: int) -> Optional[SprintMetrics]:
        """Calculate metrics for a single sprint

        Args:
            sprint_num: Sprint number to calculate

        Returns:
            SprintMetrics object or None if sprint not found
        """
        # Find sprint config
        sprint_config = next(
            (s for s in self.sprint_configs if s['sprint_number'] == sprint_num),
            None
        )

        if not sprint_config:
            self.logger.error(f"Sprint {sprint_num} not found in config")
            return None

        # Get sprint tasks
        sprint_tasks = self.all_sprints_data.get(sprint_num, [])

        if not sprint_tasks:
            self.logger.warning(f"Sprint {sprint_num}: No tasks found")

        # Convert to Task objects
        all_tasks = [self._convert_to_task(t) for t in sprint_tasks]
        completed_tasks = [t for t in all_tasks if t.is_completed]

        # Calculate basic metrics
        points_committed = sum(t.points for t in all_tasks)
        points_delivered = sum(t.points for t in completed_tasks)

        # Detect carryover
        carryover_in_tasks = self.carryover_detector.detect_carryover_in(sprint_num)
        carryover_out_tasks = self.carryover_detector.detect_carryover_out(
            sprint_num,
            sprint_tasks
        )

        carryover_in = sum(t['points'] for t in carryover_in_tasks)
        carryover_out = sum(t['points'] for t in carryover_out_tasks)

        # Calculate derived metrics
        total_work = points_committed + carryover_in
        burndown = total_work - points_delivered

        # Calculate delivery rate
        delivery_rate = (points_delivered / total_work * 100) if total_work > 0 else 0.0

        # Fetch sprint dates and build daily burndown if client available
        sprint_start_date = None
        sprint_end_date = None
        daily_completion = None

        if self.clickup_client:
            try:
                sprint_start_date, sprint_end_date = self.clickup_client.get_sprint_date_range(
                    sprint_config['list_id']
                )

                if sprint_start_date and sprint_end_date:
                    self.logger.info(
                        f"Sprint {sprint_num}: Fetched date range "
                        f"{sprint_start_date} - {sprint_end_date}"
                    )

                    # Build daily snapshots (History-Based Approach)
                    daily_snapshots = self._build_daily_snapshots(
                        sprint_tasks,
                        sprint_start_date,
                        sprint_end_date
                    )

                    # Calculate daily burndown (remaining points per day)
                    if daily_snapshots:
                        daily_completion = self._calculate_daily_burndown(daily_snapshots)
                        total_remaining = sum(daily_completion.values())
                        self.logger.debug(
                            f"Sprint {sprint_num}: Daily burndown calculated, "
                            f"final remaining = {list(daily_completion.values())[-1] if daily_completion else 0} pts"
                        )
                else:
                    self.logger.warning(f"Sprint {sprint_num}: No date range available")
            except Exception as e:
                self.logger.warning(f"Sprint {sprint_num}: Failed to fetch sprint dates: {e}")

        # Create metrics object
        metrics = SprintMetrics(
            sprint_number=sprint_num,
            sprint_name=sprint_config['name'],
            week=sprint_config['week'],
            list_id=sprint_config['list_id'],
            url=sprint_config['url'],
            total_tasks=len(all_tasks),
            completed_tasks_count=len(completed_tasks),
            points_committed=points_committed,
            carryover_in=carryover_in,
            points_delivered=points_delivered,
            carryover_out=carryover_out,
            total_work=total_work,
            burndown=burndown,
            delivery_rate=delivery_rate,
            all_tasks=all_tasks,
            completed_tasks=completed_tasks,
            carryover_in_tasks=carryover_in_tasks,
            carryover_out_tasks=carryover_out_tasks,
            sprint_start_date=sprint_start_date,
            sprint_end_date=sprint_end_date,
            daily_completion=daily_completion,
            sprint_reporting_url=sprint_config.get('sprint_reporting_url')
        )

        self.logger.info(
            f"Sprint {sprint_num}: "
            f"{points_delivered}/{total_work} points delivered "
            f"({delivery_rate:.1f}% delivery rate)"
        )

        return metrics

    def calculate_all_metrics(self) -> List[SprintMetrics]:
        """Calculate metrics for all sprints

        Returns:
            List of SprintMetrics objects, sorted by start date
        """
        self.logger.info(f"Calculating metrics for {len(self.sprint_configs)} sprints")

        metrics_list = []

        for sprint_config in self.sprint_configs:
            sprint_num = sprint_config['sprint_number']
            metrics = self.calculate_sprint_metrics(sprint_num)

            if metrics:
                metrics_list.append(metrics)

        # Sort by sprint start date (fallback to sprint number if no date)
        metrics_list.sort(key=lambda m: (m.sprint_start_date or 0, m.sprint_number))

        self.logger.info(f"Calculated metrics for {len(metrics_list)} sprints")

        return metrics_list

    def get_overall_statistics(self, metrics_list: List[SprintMetrics]) -> Dict:
        """Calculate overall statistics across all sprints

        Args:
            metrics_list: List of SprintMetrics

        Returns:
            Dictionary with overall stats
        """
        if not metrics_list:
            return {}

        total_committed = sum(m.points_committed for m in metrics_list)
        total_delivered = sum(m.points_delivered for m in metrics_list)
        total_carryover_in = sum(m.carryover_in for m in metrics_list)
        total_carryover_out = sum(m.carryover_out for m in metrics_list)
        total_work = sum(m.total_work for m in metrics_list)

        avg_delivery_rate = sum(m.delivery_rate for m in metrics_list) / len(metrics_list)

        # Find best/worst sprints
        best_sprint = max(metrics_list, key=lambda m: m.delivery_rate)
        worst_sprint = min(metrics_list, key=lambda m: m.delivery_rate)

        # Calculate velocity consistency (standard deviation)
        avg_delivered = total_delivered / len(metrics_list)
        variance = sum((m.points_delivered - avg_delivered) ** 2 for m in metrics_list) / len(metrics_list)
        std_dev = variance ** 0.5

        return {
            'total_sprints': len(metrics_list),
            'total_committed': total_committed,
            'total_delivered': total_delivered,
            'total_carryover_in': total_carryover_in,
            'total_carryover_out': total_carryover_out,
            'total_work': total_work,
            'avg_delivery_rate': avg_delivery_rate,
            'avg_points_per_sprint': total_delivered / len(metrics_list),
            'velocity_std_dev': std_dev,
            'best_sprint': {
                'number': best_sprint.sprint_number,
                'name': best_sprint.sprint_name,
                'delivery_rate': best_sprint.delivery_rate
            },
            'worst_sprint': {
                'number': worst_sprint.sprint_number,
                'name': worst_sprint.sprint_name,
                'delivery_rate': worst_sprint.delivery_rate
            }
        }
