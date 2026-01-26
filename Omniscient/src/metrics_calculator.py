"""
OKR metrics calculator for PR quality data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta


class OKRMetricsCalculator:
    """Calculate OKR metrics from PR quality data"""

    def __init__(self, pr_data: pd.DataFrame):
        """Initialize calculator with PR data

        Args:
            pr_data: DataFrame containing PR scores
        """
        self.pr_data = pr_data
        self.score_columns = [
            'readability_numeric', 'function_usability_numeric',
            'idiomaticity_numeric', 'test_inclusion_numeric',
            'commit_size_numeric', 'complexity_numeric',
            'code_churn_numeric', 'clean_code_structure_numeric'
        ]

    def calculate_all_metrics(self) -> Dict[str, Any]:
        """Calculate all OKR metrics

        Returns:
            Dictionary containing all calculated metrics
        """
        return {
            'summary': self._calculate_summary_metrics(),
            'quality_trends': self._calculate_quality_trends(),
            'contributor_metrics': self._calculate_contributor_metrics(),
            'repository_metrics': self._calculate_repository_metrics(),
            'category_scores': self._calculate_category_scores(),
            'decision_distribution': self._calculate_decision_distribution(),
            'monthly_metrics': self._calculate_monthly_metrics(),
            'top_performers': self._calculate_top_performers(),
            'improvement_areas': self._identify_improvement_areas()
        }

    def _calculate_summary_metrics(self) -> Dict[str, Any]:
        """Calculate high-level summary metrics"""
        return {
            'total_prs': len(self.pr_data),
            'total_contributors': self.pr_data['github_user_id'].nunique(),
            'total_repositories': self.pr_data['repository'].nunique(),
            'avg_overall_score': float(self.pr_data['overall_score'].mean()) if 'overall_score' in self.pr_data.columns else 0,
            'median_overall_score': float(self.pr_data['overall_score'].median()) if 'overall_score' in self.pr_data.columns else 0,
            'date_range': {
                'start': str(self.pr_data['created_at'].min()),
                'end': str(self.pr_data['created_at'].max())
            }
        }

    def _calculate_quality_trends(self) -> Dict[str, List]:
        """Calculate quality trends over time"""
        # Group by week
        self.pr_data['week'] = pd.to_datetime(self.pr_data['created_at']).dt.to_period('W')

        weekly_avg = self.pr_data.groupby('week').agg({
            'overall_score': 'mean',
            'pr_number': 'count'
        }).reset_index()

        weekly_avg['week'] = weekly_avg['week'].astype(str)

        return {
            'weeks': weekly_avg['week'].tolist(),
            'avg_scores': weekly_avg['overall_score'].tolist(),
            'pr_counts': weekly_avg['pr_number'].tolist()
        }

    def _calculate_contributor_metrics(self) -> List[Dict[str, Any]]:
        """Calculate per-contributor metrics"""
        contributor_stats = self.pr_data.groupby('github_user_id').agg({
            'pr_number': 'count',
            'overall_score': ['mean', 'median', 'std'],
            'created_at': ['min', 'max']
        }).reset_index()

        contributor_stats.columns = [
            'contributor', 'total_prs', 'avg_score',
            'median_score', 'score_std', 'first_pr', 'last_pr'
        ]

        # Sort by total PRs
        contributor_stats = contributor_stats.sort_values('total_prs', ascending=False)

        return contributor_stats.to_dict('records')

    def _calculate_repository_metrics(self) -> List[Dict[str, Any]]:
        """Calculate per-repository metrics"""
        repo_stats = self.pr_data.groupby('repository').agg({
            'pr_number': 'count',
            'overall_score': ['mean', 'median'],
            'github_user_id': 'nunique'
        }).reset_index()

        repo_stats.columns = [
            'repository', 'total_prs', 'avg_score',
            'median_score', 'contributors'
        ]

        repo_stats = repo_stats.sort_values('total_prs', ascending=False)

        return repo_stats.to_dict('records')

    def _calculate_category_scores(self) -> Dict[str, float]:
        """Calculate average scores per category"""
        category_scores = {}

        for col in self.score_columns:
            if col in self.pr_data.columns:
                category_name = col.replace('_numeric', '')
                category_scores[category_name] = float(self.pr_data[col].mean())

        return category_scores

    def _calculate_decision_distribution(self) -> Dict[str, int]:
        """Calculate distribution of PR decisions"""
        if 'decision' not in self.pr_data.columns:
            return {}

        decision_counts = self.pr_data['decision'].value_counts().to_dict()
        return {str(k): int(v) for k, v in decision_counts.items()}

    def _calculate_monthly_metrics(self) -> List[Dict[str, Any]]:
        """Calculate monthly aggregated metrics"""
        self.pr_data['month'] = pd.to_datetime(self.pr_data['created_at']).dt.to_period('M')

        monthly_stats = self.pr_data.groupby('month').agg({
            'pr_number': 'count',
            'overall_score': 'mean',
            'github_user_id': 'nunique'
        }).reset_index()

        monthly_stats.columns = ['month', 'total_prs', 'avg_score', 'active_contributors']
        monthly_stats['month'] = monthly_stats['month'].astype(str)

        return monthly_stats.to_dict('records')

    def _calculate_top_performers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identify top performing contributors and repositories"""
        # Top contributors by average score (min 3 PRs)
        contributor_stats = self.pr_data.groupby('github_user_id').agg({
            'pr_number': 'count',
            'overall_score': 'mean'
        }).reset_index()

        contributor_stats = contributor_stats[contributor_stats['pr_number'] >= 3]
        top_contributors = contributor_stats.nlargest(10, 'overall_score')

        # Top repositories by average score
        repo_stats = self.pr_data.groupby('repository').agg({
            'pr_number': 'count',
            'overall_score': 'mean'
        }).reset_index()

        top_repos = repo_stats.nlargest(5, 'overall_score')

        return {
            'top_contributors': [
                {
                    'contributor': row['github_user_id'],
                    'avg_score': float(row['overall_score']),
                    'total_prs': int(row['pr_number'])
                }
                for _, row in top_contributors.iterrows()
            ],
            'top_repositories': [
                {
                    'repository': row['repository'],
                    'avg_score': float(row['overall_score']),
                    'total_prs': int(row['pr_number'])
                }
                for _, row in top_repos.iterrows()
            ]
        }

    def _identify_improvement_areas(self) -> Dict[str, Any]:
        """Identify areas that need improvement"""
        improvement_areas = {}

        # Find categories with lowest average scores
        category_scores = self._calculate_category_scores()
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1])

        improvement_areas['lowest_scoring_categories'] = [
            {'category': cat, 'avg_score': score}
            for cat, score in sorted_categories[:3]
        ]

        # Find contributors who may need support (low average score, multiple PRs)
        contributor_stats = self.pr_data.groupby('github_user_id').agg({
            'pr_number': 'count',
            'overall_score': 'mean'
        }).reset_index()

        needs_support = contributor_stats[
            (contributor_stats['pr_number'] >= 3) &
            (contributor_stats['overall_score'] < 25)
        ]

        improvement_areas['contributors_needing_support'] = [
            {
                'contributor': row['github_user_id'],
                'avg_score': float(row['overall_score']),
                'total_prs': int(row['pr_number'])
            }
            for _, row in needs_support.iterrows()
        ]

        return improvement_areas
