"""
Visualization generator for OKR metrics
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional


class OKRVisualizer:
    """Generate visualizations for OKR metrics"""

    def __init__(self, pr_data: pd.DataFrame, metrics: Dict[str, Any]):
        """Initialize visualizer

        Args:
            pr_data: DataFrame containing PR scores
            metrics: Dictionary of calculated metrics
        """
        self.pr_data = pr_data
        self.metrics = metrics
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['font.size'] = 10

    def plot_pr_quality_trend(self) -> str:
        """Plot PR quality trend over time

        Returns:
            Path to saved chart
        """
        quality_trends = self.metrics['quality_trends']

        fig, ax1 = plt.subplots(figsize=(14, 6))

        # Plot average scores
        color = 'tab:blue'
        ax1.set_xlabel('Week', fontsize=12)
        ax1.set_ylabel('Average Quality Score', color=color, fontsize=12)
        ax1.plot(quality_trends['weeks'], quality_trends['avg_scores'],
                 color=color, marker='o', linewidth=2, markersize=6, label='Avg Score')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)

        # Plot PR count on secondary axis
        ax2 = ax1.twinx()
        color = 'tab:orange'
        ax2.set_ylabel('PR Count', color=color, fontsize=12)
        ax2.bar(quality_trends['weeks'], quality_trends['pr_counts'],
                alpha=0.3, color=color, label='PR Count')
        ax2.tick_params(axis='y', labelcolor=color)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')

        plt.title('PR Quality Trend Over Time', fontsize=14, fontweight='bold', pad=20)
        fig.tight_layout()

        output_path = self.output_dir / 'pr_quality_trend.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_score_distribution(self) -> str:
        """Plot overall score distribution

        Returns:
            Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot histogram with KDE
        ax.hist(self.pr_data['overall_score'], bins=20, alpha=0.6,
                color='skyblue', edgecolor='black')

        # Add mean and median lines
        mean_score = self.pr_data['overall_score'].mean()
        median_score = self.pr_data['overall_score'].median()

        ax.axvline(mean_score, color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {mean_score:.1f}')
        ax.axvline(median_score, color='green', linestyle='--', linewidth=2,
                   label=f'Median: {median_score:.1f}')

        ax.set_xlabel('Overall Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Overall PR Quality Score Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.legend()
        ax.grid(True, alpha=0.3)

        output_path = self.output_dir / 'score_distribution.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_contributor_performance(self) -> str:
        """Plot top contributor performance

        Returns:
            Path to saved chart
        """
        # Get top 10 contributors by PR count
        contributor_stats = self.pr_data.groupby('github_user_id').agg({
            'pr_number': 'count',
            'overall_score': 'mean'
        }).reset_index()

        top_contributors = contributor_stats.nlargest(10, 'pr_number')

        fig, ax = plt.subplots(figsize=(12, 8))

        # Create horizontal bar chart
        y_pos = np.arange(len(top_contributors))
        colors = plt.cm.viridis(top_contributors['overall_score'] / top_contributors['overall_score'].max())

        bars = ax.barh(y_pos, top_contributors['pr_number'], color=colors)

        # Add score labels on bars
        for i, (idx, row) in enumerate(top_contributors.iterrows()):
            ax.text(row['pr_number'] + 0.5, i,
                    f"Avg: {row['overall_score']:.1f}",
                    va='center', fontsize=9)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(top_contributors['github_user_id'])
        ax.set_xlabel('Total PRs', fontsize=12)
        ax.set_ylabel('Contributor', fontsize=12)
        ax.set_title('Top 10 Contributors by PR Count', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x')

        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis,
                                   norm=plt.Normalize(vmin=top_contributors['overall_score'].min(),
                                                     vmax=top_contributors['overall_score'].max()))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Average Score', fontsize=10)

        output_path = self.output_dir / 'contributor_performance.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_category_heatmap(self) -> str:
        """Plot category scores heatmap

        Returns:
            Path to saved chart
        """
        # Get category scores for each contributor
        score_columns = [
            'readability_numeric', 'function_usability_numeric',
            'idiomaticity_numeric', 'test_inclusion_numeric',
            'commit_size_numeric', 'complexity_numeric',
            'code_churn_numeric', 'clean_code_structure_numeric'
        ]

        # Filter columns that exist
        available_columns = [col for col in score_columns if col in self.pr_data.columns]

        if not available_columns:
            # Create empty chart
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.text(0.5, 0.5, 'No category data available',
                    ha='center', va='center', fontsize=14)
            ax.axis('off')
            output_path = self.output_dir / 'category_heatmap.png'
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            return str(output_path)

        # Calculate average scores per category
        category_avgs = self.pr_data[available_columns].mean().values.reshape(1, -1)

        # Clean column names
        category_names = [col.replace('_numeric', '').replace('_', ' ').title()
                         for col in available_columns]

        fig, ax = plt.subplots(figsize=(14, 3))

        # Create heatmap
        sns.heatmap(category_avgs, annot=True, fmt='.2f', cmap='RdYlGn',
                   xticklabels=category_names, yticklabels=['Average'],
                   cbar_kws={'label': 'Score (1-5)'}, vmin=1, vmax=5, ax=ax)

        ax.set_title('Average Scores by Category', fontsize=14, fontweight='bold', pad=20)

        output_path = self.output_dir / 'category_heatmap.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_decision_breakdown(self) -> str:
        """Plot PR decision breakdown

        Returns:
            Path to saved chart
        """
        if 'decision' not in self.pr_data.columns:
            # Create empty chart
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No decision data available',
                    ha='center', va='center', fontsize=14)
            ax.axis('off')
            output_path = self.output_dir / 'decision_breakdown.png'
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            return str(output_path)

        decision_counts = self.pr_data['decision'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create pie chart
        colors = plt.cm.Set3(range(len(decision_counts)))
        wedges, texts, autotexts = ax.pie(decision_counts.values,
                                           labels=decision_counts.index,
                                           autopct='%1.1f%%',
                                           colors=colors,
                                           startangle=90)

        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        ax.set_title('PR Decision Breakdown', fontsize=14, fontweight='bold', pad=20)

        output_path = self.output_dir / 'decision_breakdown.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_monthly_pr_volume(self) -> str:
        """Plot monthly PR volume and quality

        Returns:
            Path to saved chart
        """
        monthly_metrics = self.metrics['monthly_metrics']

        if not monthly_metrics:
            # Create empty chart
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.text(0.5, 0.5, 'No monthly data available',
                    ha='center', va='center', fontsize=14)
            ax.axis('off')
            output_path = self.output_dir / 'monthly_pr_volume.png'
            plt.savefig(output_path, bbox_inches='tight')
            plt.close()
            return str(output_path)

        months = [m['month'] for m in monthly_metrics]
        pr_counts = [m['total_prs'] for m in monthly_metrics]
        avg_scores = [m['avg_score'] for m in monthly_metrics]

        fig, ax1 = plt.subplots(figsize=(14, 6))

        # Plot PR volume
        color = 'tab:blue'
        ax1.set_xlabel('Month', fontsize=12)
        ax1.set_ylabel('PR Count', color=color, fontsize=12)
        ax1.bar(months, pr_counts, alpha=0.6, color=color, label='PR Count')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True, alpha=0.3)

        # Plot average score on secondary axis
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Average Score', color=color, fontsize=12)
        ax2.plot(months, avg_scores, color=color, marker='o',
                 linewidth=2, markersize=8, label='Avg Score')
        ax2.tick_params(axis='y', labelcolor=color)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')

        plt.title('Monthly PR Volume and Quality', fontsize=14, fontweight='bold', pad=20)
        fig.tight_layout()

        output_path = self.output_dir / 'monthly_pr_volume.png'
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()

        return str(output_path)
