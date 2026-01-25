"""ClickUp API Client with caching and rate limiting"""

import logging
import time
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from .utils import CacheHandler


class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, requests_per_minute: int = 80, burst_size: int = 10):
        """Initialize rate limiter

        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size
        """
        self.rate = requests_per_minute / 60.0  # requests per second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.logger = logging.getLogger('sprint_analytics.ratelimiter')

    def acquire(self) -> None:
        """Acquire a token, blocking if necessary"""
        while True:
            now = time.time()
            elapsed = now - self.last_update

            # Add tokens based on elapsed time
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return

            # Wait until next token available
            sleep_time = (1 - self.tokens) / self.rate
            self.logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)


class ClickUpClient:
    """ClickUp API wrapper with caching and rate limiting"""

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(
        self,
        api_token: str,
        cache_handler: Optional[CacheHandler] = None,
        rate_limiter: Optional[RateLimiter] = None,
        max_retries: int = 3
    ):
        """Initialize ClickUp client

        Args:
            api_token: ClickUp API token
            cache_handler: Cache handler instance
            rate_limiter: Rate limiter instance
            max_retries: Maximum retry attempts for failed requests
        """
        self.api_token = api_token
        self.cache = cache_handler or CacheHandler()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.max_retries = max_retries
        self.logger = logging.getLogger('sprint_analytics.clickup')

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': api_token,
            'Content-Type': 'application/json'
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
        reraise=True
    )
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with retry logic

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            requests.RequestException: On API errors
        """
        self.rate_limiter.acquire()

        url = f"{self.BASE_URL}/{endpoint}"
        self.logger.debug(f"API request: {url}")

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        return response.json()

    def get_tasks_in_list(
        self,
        list_id: str,
        user_id: str,
        use_cache: bool = True
    ) -> List[Dict]:
        """Get all tasks in a list for a specific user

        Args:
            list_id: ClickUp list ID
            user_id: User ID to filter tasks
            use_cache: Use cached data if available

        Returns:
            List of task dictionaries
        """
        cache_key = f"list_{list_id}_user_{user_id}"

        # Check cache first
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.logger.info(f"Using cached data for list {list_id}")
                return cached

        # Fetch from API
        self.logger.info(f"Fetching tasks from list {list_id}")

        params = {
            'assignees[]': user_id,
            'include_closed': 'true',
            'subtasks': 'true'
        }

        try:
            response = self._make_request(f"list/{list_id}/task", params)
            tasks = response.get('tasks', [])

            # Cache the result
            self.cache.set(cache_key, tasks)

            self.logger.info(f"Fetched {len(tasks)} tasks from list {list_id}")
            return tasks

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch tasks from list {list_id}: {e}")
            raise

    def fetch_all_sprints_data(
        self,
        sprint_configs: List[Dict],
        user_id: str,
        use_cache: bool = True,
        max_workers: int = 4
    ) -> Dict[int, List[Dict]]:
        """Fetch all sprints data in parallel

        Args:
            sprint_configs: List of sprint configuration dicts
            user_id: User ID to filter tasks
            use_cache: Use cached data if available
            max_workers: Maximum parallel workers

        Returns:
            Dictionary mapping sprint_number -> list of tasks
        """
        self.logger.info(f"Fetching data for {len(sprint_configs)} sprints")

        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all fetch tasks
            future_to_sprint = {
                executor.submit(
                    self.get_tasks_in_list,
                    sprint['list_id'],
                    user_id,
                    use_cache
                ): sprint
                for sprint in sprint_configs
            }

            # Collect results
            for future in as_completed(future_to_sprint):
                sprint = future_to_sprint[future]
                sprint_num = sprint['sprint_number']

                try:
                    tasks = future.result()
                    results[sprint_num] = tasks
                    self.logger.info(
                        f"Sprint {sprint_num}: {len(tasks)} tasks"
                    )

                except Exception as e:
                    self.logger.error(
                        f"Failed to fetch Sprint {sprint_num}: {e}"
                    )
                    results[sprint_num] = []

        return results

    @staticmethod
    def extract_task_points(task: Dict) -> int:
        """Extract story points from task

        Tries multiple locations:
        1. task.points field
        2. Custom field named 'Points'

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

    @staticmethod
    def get_task_status(task: Dict) -> str:
        """Get task status string

        Args:
            task: Task dictionary

        Returns:
            Status name (empty string if not found)
        """
        status = task.get('status', {})
        if isinstance(status, dict):
            return status.get('status', '')
        return str(status)

    @staticmethod
    def is_task_completed(status: str, completion_keyword: str = "deployed") -> bool:
        """Check if task status indicates completion

        Args:
            status: Task status string
            completion_keyword: Keyword to match (case-insensitive)

        Returns:
            True if status contains completion keyword
        """
        return completion_keyword.lower() in status.lower()

    def get_list_details(
        self,
        list_id: str,
        use_cache: bool = True
    ) -> Dict:
        """Get list details including start/end dates

        Args:
            list_id: ClickUp list ID
            use_cache: Use cached data if available

        Returns:
            List details dictionary
        """
        cache_key = f"list_details_{list_id}"

        # Check cache first
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.logger.debug(f"Using cached list details for {list_id}")
                return cached

        # Fetch from API
        self.logger.info(f"Fetching list details for {list_id}")

        try:
            response = self._make_request(f"list/{list_id}")

            # Cache the result
            self.cache.set(cache_key, response)

            return response

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch list details for {list_id}: {e}")
            return {}

    def get_task_history(
        self,
        task_id: str,
        use_cache: bool = True
    ) -> List[Dict]:
        """Get task history/activity to track status changes

        Args:
            task_id: ClickUp task ID
            use_cache: Use cached data if available

        Returns:
            List of history items
        """
        cache_key = f"task_history_{task_id}"

        # Check cache first
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.logger.debug(f"Using cached history for task {task_id}")
                return cached

        # Fetch from API
        self.logger.debug(f"Fetching history for task {task_id}")

        try:
            # Get task details which includes date_closed and status history
            response = self._make_request(f"task/{task_id}")

            # Extract relevant history information
            history = {
                'date_created': response.get('date_created'),
                'date_closed': response.get('date_closed'),
                'date_updated': response.get('date_updated'),
                'status': response.get('status', {}).get('status', ''),
                'custom_fields': response.get('custom_fields', [])
            }

            # Cache the result
            self.cache.set(cache_key, history)

            return history

        except requests.RequestException as e:
            self.logger.warning(f"Failed to fetch history for task {task_id}: {e}")
            return {}

    def get_bulk_time_in_status(
        self,
        task_ids: List[str],
        use_cache: bool = True
    ) -> Dict:
        """Get time in status for multiple tasks (bulk operation)

        Args:
            task_ids: List of task IDs
            use_cache: Whether to use cached data

        Returns:
            Dict mapping task_id -> {current_status, status_history}
            Each status_history entry: {status, since (timestamp ms), total_time, type}
        """
        if not task_ids:
            return {}

        # Check cache for all tasks
        cached_results = {}
        uncached_ids = []

        if use_cache:
            for task_id in task_ids:
                cache_key = f'time_in_status_{task_id}'
                cached = self.cache.get(cache_key)
                if cached:
                    cached_results[task_id] = cached
                else:
                    uncached_ids.append(task_id)

            # If all cached, return cached results
            if not uncached_ids:
                self.logger.debug(f"Using cached time_in_status for all {len(task_ids)} tasks")
                return cached_results

            task_ids_to_fetch = uncached_ids
        else:
            task_ids_to_fetch = task_ids

        self.logger.info(f"Fetching bulk time_in_status for {len(task_ids_to_fetch)} tasks")

        try:
            # ClickUp accepts task_ids as repeated query params
            params = {'task_ids': task_ids_to_fetch}
            response = self._make_request('task/bulk_time_in_status/task_ids', params=params)

            # Cache individual results
            if use_cache:
                for task_id, data in response.items():
                    cache_key = f'time_in_status_{task_id}'
                    self.cache.set(cache_key, data)

            # Merge with cached results
            cached_results.update(response)
            return cached_results

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch bulk time_in_status: {e}")
            return cached_results  # Return any cached data we have

    def get_sprint_reporting_view(
        self,
        list_id: str,
        workspace_id: str = "3708016",
        use_cache: bool = True
    ) -> Optional[str]:
        """Get Sprint Reporting view URL for a sprint list

        Args:
            list_id: ClickUp list ID
            workspace_id: ClickUp workspace ID
            use_cache: Use cached data if available

        Returns:
            URL to Sprint Reporting view, or None if not found
        """
        cache_key = f"sprint_reporting_view_{list_id}"

        # Check cache
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                self.logger.debug(f"Using cached Sprint Reporting view for list {list_id}")
                return cached

        # Fetch views from API
        self.logger.debug(f"Fetching views for list {list_id}")

        try:
            response = self._make_request(f"list/{list_id}/view")
            views = response.get('views', [])

            # Find Sprint Reporting view
            for view in views:
                view_name = view.get('name', '').lower()
                if 'sprint' in view_name and 'report' in view_name:
                    view_id = view.get('id')
                    view_url = f"https://app.clickup.com/{workspace_id}/v/{view_id}"

                    # Cache the result
                    if use_cache:
                        self.cache.set(cache_key, view_url)

                    self.logger.info(f"Found Sprint Reporting view for list {list_id}: {view_url}")
                    return view_url

            self.logger.warning(f"Sprint Reporting view not found for list {list_id}")
            return None

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch views for list {list_id}: {e}")
            return None

    def get_sprint_date_range(
        self,
        list_id: str,
        use_cache: bool = True
    ) -> tuple:
        """Get sprint start and end dates from list details

        Args:
            list_id: ClickUp list ID
            use_cache: Use cached data if available

        Returns:
            Tuple of (start_date, end_date) as timestamps in milliseconds
        """
        list_details = self.get_list_details(list_id, use_cache)

        # ClickUp lists can have start_date and due_date
        start_date = list_details.get('start_date')
        due_date = list_details.get('due_date')

        return (start_date, due_date)
