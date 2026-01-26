"""
Report generator for OKR metrics
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class OKRReportGenerator:
    """Generate reports in various formats"""

    def __init__(self, pr_data: pd.DataFrame, metrics: Dict[str, Any]):
        """Initialize report generator

        Args:
            pr_data: DataFrame containing PR scores
            metrics: Dictionary of calculated metrics
        """
        self.pr_data = pr_data
        self.metrics = metrics
        self.output_dir = Path('output')
        self.reports_dir = Path('reports')
        self.output_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def save_json(self) -> str:
        """Save metrics as JSON

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / 'okr_metrics.json'

        # Convert any non-serializable objects
        serializable_metrics = self._make_serializable(self.metrics)

        with open(output_path, 'w') as f:
            json.dump(serializable_metrics, f, indent=2, default=str)

        return str(output_path)

    def save_csv(self) -> str:
        """Save PR data as CSV

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / 'okr_pr_data.csv'

        # Select relevant columns
        columns_to_export = [
            'pr_number', 'repository', 'github_user_id',
            'overall_score', 'decision', 'created_at',
            'readability', 'function_usability', 'idiomaticity',
            'test_inclusion', 'commit_size', 'complexity',
            'code_churn', 'clean_code_structure'
        ]

        # Filter columns that exist
        available_columns = [col for col in columns_to_export if col in self.pr_data.columns]

        self.pr_data[available_columns].to_csv(output_path, index=False)

        return str(output_path)

    def save_markdown(self) -> str:
        """Generate and save markdown report

        Returns:
            Path to saved file
        """
        output_path = self.reports_dir / 'okr_report.md'

        summary = self.metrics['summary']
        quality_trends = self.metrics['quality_trends']
        category_scores = self.metrics['category_scores']
        decision_dist = self.metrics['decision_distribution']
        top_performers = self.metrics['top_performers']
        improvement_areas = self.metrics['improvement_areas']

        # Generate markdown content
        md_content = f"""# Omniscient OKR Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

### Overview
- **Total PRs Analyzed:** {summary['total_prs']}
- **Active Contributors:** {summary['total_contributors']}
- **Repositories:** {summary['total_repositories']}
- **Date Range:** {summary['date_range']['start']} to {summary['date_range']['end']}

### Key Metrics
- **Average Overall Score:** {summary['avg_overall_score']:.2f} / 40
- **Median Overall Score:** {summary['median_overall_score']:.2f} / 40
- **Quality Grade:** {self._calculate_grade(summary['avg_overall_score'])}

---

## Quality Trends

### Weekly Performance
The quality trends over time show {'improvement' if self._is_improving(quality_trends) else 'stable performance'}.

![PR Quality Trend](../output/pr_quality_trend.png)

---

## Category Performance

### Average Scores by Category (1-5 scale)

"""

        # Add category scores table
        if category_scores:
            md_content += "| Category | Average Score | Rating |\n"
            md_content += "|----------|--------------|--------|\n"

            for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
                rating = self._score_to_rating(score)
                md_content += f"| {category.replace('_', ' ').title()} | {score:.2f} | {rating} |\n"

            md_content += "\n![Category Heatmap](../output/category_heatmap.png)\n\n"

        md_content += """---

## Decision Distribution

"""

        # Add decision distribution
        if decision_dist:
            md_content += "| Decision | Count | Percentage |\n"
            md_content += "|----------|-------|------------|\n"

            total_decisions = sum(decision_dist.values())
            for decision, count in sorted(decision_dist.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_decisions) * 100
                md_content += f"| {decision} | {count} | {percentage:.1f}% |\n"

            md_content += "\n![Decision Breakdown](../output/decision_breakdown.png)\n\n"

        md_content += """---

## Top Performers

### Top Contributors

"""

        # Add top contributors
        if top_performers['top_contributors']:
            md_content += "| Rank | Contributor | Avg Score | Total PRs |\n"
            md_content += "|------|-------------|-----------|----------|\n"

            for i, contributor in enumerate(top_performers['top_contributors'][:10], 1):
                md_content += f"| {i} | {contributor['contributor']} | {contributor['avg_score']:.2f} | {contributor['total_prs']} |\n"

            md_content += "\n![Contributor Performance](../output/contributor_performance.png)\n\n"

        md_content += """### Top Repositories

"""

        # Add top repositories
        if top_performers['top_repositories']:
            md_content += "| Rank | Repository | Avg Score | Total PRs |\n"
            md_content += "|------|------------|-----------|----------|\n"

            for i, repo in enumerate(top_performers['top_repositories'][:5], 1):
                md_content += f"| {i} | {repo['repository']} | {repo['avg_score']:.2f} | {repo['total_prs']} |\n"

            md_content += "\n"

        md_content += """---

## Areas for Improvement

"""

        # Add improvement areas
        if improvement_areas.get('lowest_scoring_categories'):
            md_content += "### Focus Areas\n\n"
            for area in improvement_areas['lowest_scoring_categories']:
                md_content += f"- **{area['category'].replace('_', ' ').title()}**: {area['avg_score']:.2f} / 5\n"

            md_content += "\n"

        if improvement_areas.get('contributors_needing_support'):
            md_content += "### Contributors Who May Need Support\n\n"
            md_content += "| Contributor | Avg Score | Total PRs |\n"
            md_content += "|-------------|-----------|----------|\n"

            for contributor in improvement_areas['contributors_needing_support']:
                md_content += f"| {contributor['contributor']} | {contributor['avg_score']:.2f} | {contributor['total_prs']} |\n"

            md_content += "\n"

        md_content += """---

## Recommendations

Based on the analysis:

1. **Quality Improvement**: Focus on the lowest-scoring categories to raise overall code quality
2. **Mentorship**: Provide support to contributors with lower average scores
3. **Best Practices**: Share best practices from top performers across the team
4. **Process Improvement**: Review PR processes to maintain consistent quality standards

---

## Monthly Trends

![Monthly PR Volume](../output/monthly_pr_volume.png)

---

## Additional Charts

- [Score Distribution](../output/score_distribution.png)
- [Category Heatmap](../output/category_heatmap.png)
- [Decision Breakdown](../output/decision_breakdown.png)

---

*This report was automatically generated by the Omniscient OKR Analytics system.*
"""

        # Write to file
        with open(output_path, 'w') as f:
            f.write(md_content)

        return str(output_path)

    def _make_serializable(self, obj: Any) -> Any:
        """Convert non-serializable objects to serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return str(obj)
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 35:
            return "A (Excellent)"
        elif score >= 28:
            return "B (Good)"
        elif score >= 21:
            return "C (Acceptable)"
        elif score >= 14:
            return "D (Needs Work)"
        else:
            return "F (Reject)"

    def _score_to_rating(self, score: float) -> str:
        """Convert numeric score to rating"""
        if score >= 4.5:
            return "⭐⭐⭐⭐⭐ Excellent"
        elif score >= 3.5:
            return "⭐⭐⭐⭐ Good"
        elif score >= 2.5:
            return "⭐⭐⭐ Acceptable"
        elif score >= 1.5:
            return "⭐⭐ Needs Work"
        else:
            return "⭐ Poor"

    def _is_improving(self, quality_trends: Dict) -> bool:
        """Check if quality is improving over time"""
        if not quality_trends['avg_scores'] or len(quality_trends['avg_scores']) < 2:
            return False

        scores = quality_trends['avg_scores']
        # Compare first half vs second half
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / len(scores[:mid])
        second_half_avg = sum(scores[mid:]) / len(scores[mid:])

        return second_half_avg > first_half_avg
