"""Cross-sprint task analysis for carryover detection"""

import logging
from typing import Dict, List, Set
from collections import defaultdict


class CarryoverDetector:
    """Detects tasks carried over between sprints"""

    def __init__(
        self,
        all_sprints_data: Dict[int, List[Dict]],
        completion_keyword: str = "deployed"
    ):
        """Initialize carryover detector

        Args:
            all_sprints_data: Dict mapping sprint_number -> list of tasks
            completion_keyword: Keyword to identify completed tasks
        """
        self.all_sprints_data = all_sprints_data
        self.completion_keyword = completion_keyword
        self.logger = logging.getLogger('sprint_analytics.carryover')

        # Build task-to-sprints mapping
        self.task_sprint_map = self._build_task_sprint_map()

        self.logger.info(
            f"Built carryover map: {len(self.task_sprint_map)} unique tasks"
        )

    def _build_task_sprint_map(self) -> Dict[str, Dict]:
        """Build mapping of task_id -> sprint appearances with status

        Returns:
            Dict mapping task_id to dict with:
                - sprints: set of sprint numbers where task appears
                - status_by_sprint: dict of sprint_number -> status
                - points: task points
                - name: task name
        """
        task_map = defaultdict(lambda: {
            'sprints': set(),
            'status_by_sprint': {},
            'points': 0,
            'name': '',
            'url': ''
        })

        for sprint_num, tasks in self.all_sprints_data.items():
            for task in tasks:
                task_id = task.get('id')
                if not task_id:
                    continue

                task_map[task_id]['sprints'].add(sprint_num)
                task_map[task_id]['status_by_sprint'][sprint_num] = \
                    self._get_task_status(task)

                # Store task metadata (use latest)
                if not task_map[task_id]['name']:
                    task_map[task_id]['name'] = task.get('name', '')
                    task_map[task_id]['url'] = task.get('url', '')
                    task_map[task_id]['points'] = self._extract_points(task)

        return dict(task_map)

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

    def _is_completed(self, status: str) -> bool:
        """Check if status indicates completion

        Args:
            status: Status string

        Returns:
            True if status contains completion keyword
        """
        return self.completion_keyword.lower() in status.lower()

    def detect_carryover_in(self, sprint_num: int) -> List[Dict]:
        """Detect tasks carried over INTO this sprint from previous sprint

        A task is carried over IN if:
        1. It appears in both (sprint_num - 1) and sprint_num
        2. It was NOT completed in sprint_num - 1

        Args:
            sprint_num: Sprint number to analyze

        Returns:
            List of carryover task dicts with metadata
        """
        if sprint_num <= 1:
            return []  # No previous sprint

        prev_sprint = sprint_num - 1
        carryover_tasks = []

        for task_id, task_info in self.task_sprint_map.items():
            sprints = task_info['sprints']

            # Task must appear in both sprints
            if prev_sprint in sprints and sprint_num in sprints:
                # Check if it was incomplete in previous sprint
                prev_status = task_info['status_by_sprint'].get(prev_sprint, '')

                if not self._is_completed(prev_status):
                    carryover_tasks.append({
                        'task_id': task_id,
                        'name': task_info['name'],
                        'url': task_info['url'],
                        'points': task_info['points'],
                        'previous_status': prev_status,
                        'from_sprint': prev_sprint
                    })

        self.logger.debug(
            f"Sprint {sprint_num}: {len(carryover_tasks)} tasks carried in"
        )

        return carryover_tasks

    def detect_carryover_out(self, sprint_num: int, sprint_tasks: List[Dict]) -> List[Dict]:
        """Detect tasks carried over OUT of this sprint to next sprint

        A task is carried over OUT if:
        1. It appears in this sprint
        2. It was NOT completed in this sprint
        3. It appears in the next sprint OR still exists incomplete

        Args:
            sprint_num: Sprint number to analyze
            sprint_tasks: List of tasks in this sprint

        Returns:
            List of carryover task dicts with metadata
        """
        next_sprint = sprint_num + 1
        carryover_tasks = []

        for task in sprint_tasks:
            task_id = task.get('id')
            if not task_id:
                continue

            # Get current status
            current_status = self._get_task_status(task)

            # Skip if completed
            if self._is_completed(current_status):
                continue

            # Check if task exists in mapping (should always be true)
            if task_id not in self.task_sprint_map:
                continue

            task_info = self.task_sprint_map[task_id]
            sprints = task_info['sprints']

            # Task carried out if it appears in next sprint OR
            # if this is the last sprint and task is incomplete
            max_sprint = max(self.all_sprints_data.keys())

            if next_sprint in sprints or sprint_num == max_sprint:
                carryover_tasks.append({
                    'task_id': task_id,
                    'name': task.get('name', ''),
                    'url': task.get('url', ''),
                    'points': self._extract_points(task),
                    'current_status': current_status,
                    'to_sprint': next_sprint if next_sprint in sprints else None
                })

        self.logger.debug(
            f"Sprint {sprint_num}: {len(carryover_tasks)} tasks carried out"
        )

        return carryover_tasks

    def get_task_sprint_history(self, task_id: str) -> List[int]:
        """Get all sprints where a task appeared

        Args:
            task_id: Task ID

        Returns:
            Sorted list of sprint numbers
        """
        if task_id not in self.task_sprint_map:
            return []

        return sorted(list(self.task_sprint_map[task_id]['sprints']))

    def get_multi_sprint_tasks(self) -> List[Dict]:
        """Get tasks that appeared in multiple sprints

        Returns:
            List of dicts with task info and sprint history
        """
        multi_sprint = []

        for task_id, task_info in self.task_sprint_map.items():
            if len(task_info['sprints']) > 1:
                multi_sprint.append({
                    'task_id': task_id,
                    'name': task_info['name'],
                    'url': task_info['url'],
                    'points': task_info['points'],
                    'sprints': sorted(list(task_info['sprints'])),
                    'sprint_count': len(task_info['sprints'])
                })

        return sorted(multi_sprint, key=lambda x: x['sprint_count'], reverse=True)
