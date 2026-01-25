"""Utility functions for logging and caching"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the application

    Args:
        verbose: Enable debug logging if True

    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configure root logger
    logger = logging.getLogger('sprint_analytics')
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


class CacheHandler:
    """File-based cache handler with TTL support"""

    def __init__(self, cache_dir: str = "data/cache", ttl_hours: int = 24):
        """Initialize cache handler

        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours for cache entries
        """
        self.cache_dir = Path(cache_dir)
        self.ttl = timedelta(hours=ttl_hours)
        self.logger = logging.getLogger('sprint_analytics.cache')

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key

        Args:
            key: Cache key (will be sanitized for filesystem)

        Returns:
            Path to cache file
        """
        # Sanitize key for filesystem
        safe_key = key.replace('/', '_').replace(':', '_')
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache if valid

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        cache_file = self._get_cache_path(key)

        if not cache_file.exists():
            self.logger.debug(f"Cache miss: {key}")
            return None

        try:
            # Read cache file
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Check expiration
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > self.ttl:
                self.logger.debug(f"Cache expired: {key}")
                cache_file.unlink()  # Delete expired cache
                return None

            self.logger.debug(f"Cache hit: {key}")
            return cache_data['value']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.warning(f"Cache corrupted for {key}: {e}")
            # Delete corrupted cache
            if cache_file.exists():
                cache_file.unlink()
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_file = self._get_cache_path(key)

        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'value': value
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self.logger.debug(f"Cached: {key}")

        except (TypeError, ValueError) as e:
            self.logger.error(f"Failed to cache {key}: {e}")

    def clear(self) -> None:
        """Clear all cache files"""
        cleared = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            cleared += 1

        self.logger.info(f"Cleared {cleared} cache entries")

    def clear_key(self, key: str) -> None:
        """Clear specific cache key

        Args:
            key: Cache key to clear
        """
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            cache_file.unlink()
            self.logger.debug(f"Cleared cache: {key}")


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if necessary

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
