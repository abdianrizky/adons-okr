"""
Database client for Omniscient MySQL database
"""

import pymysql
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime


class OmniscientDBClient:
    """Client for connecting to and querying Omniscient database"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        """Initialize database connection parameters

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def _get_connection(self):
        """Create and return a database connection"""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )

    def fetch_pr_scores(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch PR scores from database

        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            DataFrame containing PR scores
        """
        query = """
            SELECT
                id,
                github_user_id,
                commit_hash,
                pr_number,
                repository,
                tags,
                readability,
                function_usability,
                idiomaticity,
                test_inclusion,
                commit_size,
                complexity,
                code_churn,
                clean_code_structure,
                overall_score,
                decision,
                pr_comment,
                created_at,
                updated_at,
                clickup_task_id,
                clickup_alignment_score,
                clickup_alignment_comment
            FROM pr_scores
        """

        conditions = []
        params = []

        if start_date:
            conditions.append("created_at >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("created_at <= %s")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        conn = self._get_connection()
        try:
            df = pd.read_sql(query, conn, params=params if params else None)

            # Convert score columns to numeric
            score_columns = [
                'readability', 'function_usability', 'idiomaticity',
                'test_inclusion', 'commit_size', 'complexity',
                'code_churn', 'clean_code_structure'
            ]

            # Map text values to numeric scores
            score_map = {
                # Score 5: Excellent
                'excellent': 5, 'elegant': 5, 'minimal': 5, 'small': 5, 'stable': 5, 'reusable': 5, 'comprehensive': 5,
                # Score 4: Good
                'good': 4, 'clear': 4, 'well-structured': 4, 'manageable': 4, 'controlled': 4, 'low': 4, 'good-coverage': 4,
                # Score 3: Acceptable
                'acceptable': 3, 'functional': 3, 'adequate': 3, 'basic': 3, 'medium': 3, 'moderate': 3,
                # Score 2: Needs Work
                'poor': 2, 'confusing': 2, 'tangled': 2, 'awkward': 2, 'minimal-testing': 2, 'large': 2, 'high': 2, 'problematic': 2,
                # Score 1: Critical
                'unreadable': 1, 'messy': 1, 'none': 1, 'huge': 1, 'very-complex': 1, 'excessive': 1
            }

            for col in score_columns:
                if col in df.columns:
                    df[f'{col}_numeric'] = df[col].map(score_map)

            return df

        finally:
            conn.close()

    def fetch_repository_stats(self) -> pd.DataFrame:
        """Fetch repository statistics

        Returns:
            DataFrame with repository statistics
        """
        query = """
            SELECT
                repository,
                COUNT(*) as total_prs,
                AVG(overall_score) as avg_score,
                MIN(created_at) as first_pr_date,
                MAX(created_at) as last_pr_date
            FROM pr_scores
            GROUP BY repository
            ORDER BY total_prs DESC
        """

        conn = self._get_connection()
        try:
            return pd.read_sql(query, conn)
        finally:
            conn.close()

    def fetch_contributor_stats(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Fetch contributor statistics

        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            DataFrame with contributor statistics
        """
        query = """
            SELECT
                github_user_id,
                COUNT(*) as total_prs,
                AVG(overall_score) as avg_overall_score,
                AVG(CASE
                    WHEN readability = 'excellent' THEN 5
                    WHEN readability = 'good' THEN 4
                    WHEN readability = 'acceptable' THEN 3
                    WHEN readability = 'confusing' THEN 2
                    WHEN readability = 'unreadable' THEN 1
                    ELSE NULL
                END) as avg_readability,
                MIN(created_at) as first_pr_date,
                MAX(created_at) as last_pr_date
            FROM pr_scores
        """

        conditions = []
        params = []

        if start_date:
            conditions.append("created_at >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("created_at <= %s")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            GROUP BY github_user_id
            ORDER BY total_prs DESC
        """

        conn = self._get_connection()
        try:
            return pd.read_sql(query, conn, params=params if params else None)
        finally:
            conn.close()

    def test_connection(self) -> bool:
        """Test database connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            conn = self._get_connection()
            conn.close()
            return True
        except Exception:
            return False
