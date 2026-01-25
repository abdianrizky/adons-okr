"""Sprint metrics visualization using matplotlib"""

import logging
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from .metrics_calculator import SprintMetrics


class SprintVisualizer:
    """Generate static PNG charts for sprint metrics"""

    # Color palette
    COLORS = {
        'committed': '#3498db',     # Blue
        'delivered': '#2ecc71',     # Green
        'carryover_out': '#e67e22', # Orange
        'burndown': '#e74c3c',      # Red
        'delivery_rate': '#9b59b6', # Purple
        'target': '#95a5a6',        # Gray
        'guideline': '#999999',     # Gray for ideal line
        'completed': '#4ecdc4',     # Teal for completed
        'remaining': '#ff6b6b'      # Red for remaining
    }

    def __init__(self, output_dir: str = 'output'):
        """Initialize visualizer

        Args:
            output_dir: Directory to save chart files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('sprint_analytics.visualizer')

        # Set matplotlib style
        plt.style.use('seaborn-v0_8-whitegrid')

        # Set default font sizes
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10

    def create_velocity_chart(
        self,
        metrics_list: List[SprintMetrics],
        filename: str = 'sprint_velocity_chart.png'
    ) -> str:
        """Create horizontal grouped bar chart for sprint velocity

        Args:
            metrics_list: List of SprintMetrics (already sorted by start date)
            filename: Output filename

        Returns:
            Path to saved chart
        """
        self.logger.info("Creating velocity chart")

        # Calculate figure height based on number of sprints
        num_sprints = len(metrics_list)
        fig_height = max(8, num_sprints * 0.6)
        fig, ax = plt.subplots(figsize=(12, fig_height))

        # Prepare data (already sorted by sprint_start_date)
        sprint_names = [m.sprint_name for m in metrics_list]
        committed = [m.points_committed for m in metrics_list]
        delivered = [m.points_delivered for m in metrics_list]
        carryover_out = [m.carryover_out for m in metrics_list]

        # Y positions (reverse order so oldest sprint is at bottom)
        y = np.arange(len(sprint_names))
        height = 0.25

        # Create horizontal bars
        bars1 = ax.barh(
            y + height,
            committed,
            height,
            label='Points Committed',
            color=self.COLORS['committed'],
            alpha=0.8
        )

        bars2 = ax.barh(
            y,
            delivered,
            height,
            label='Points Delivered',
            color=self.COLORS['delivered'],
            alpha=0.8
        )

        bars3 = ax.barh(
            y - height,
            carryover_out,
            height,
            label='Carryover Out',
            color=self.COLORS['carryover_out'],
            alpha=0.8
        )

        # Add value labels on bars
        def autolabel(bars):
            for bar in bars:
                width = bar.get_width()
                if width > 0:
                    ax.text(
                        width,
                        bar.get_y() + bar.get_height() / 2.,
                        f'{int(width)}',
                        ha='left',
                        va='center',
                        fontsize=9,
                        fontweight='bold'
                    )

        autolabel(bars1)
        autolabel(bars2)
        autolabel(bars3)

        # Customize chart
        ax.set_ylabel('Sprint', fontweight='bold')
        ax.set_xlabel('Story Points', fontweight='bold')
        ax.set_title('Sprint Velocity: Committed vs Delivered vs Carryover',
                     fontweight='bold', pad=20)
        ax.set_yticks(y)
        ax.set_yticklabels(sprint_names, fontsize=10)
        ax.legend(loc='lower right', framealpha=0.9)
        ax.grid(axis='x', alpha=0.3)

        # Add zero line
        ax.axvline(x=0, color='black', linewidth=0.8)

        # Set x-axis limit with some padding
        max_points = max(max(committed), max(delivered)) if committed and delivered else 20
        ax.set_xlim(0, max_points * 1.15)

        plt.tight_layout()

        # Save chart
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Velocity chart saved to {output_path}")
        return str(output_path)

    def create_burndown_chart(
        self,
        metrics_list: List[SprintMetrics],
        filename: str = 'sprint_burndown_chart.png'
    ) -> str:
        """Create line chart with area fill for burndown trend

        Args:
            metrics_list: List of SprintMetrics
            filename: Output filename

        Returns:
            Path to saved chart
        """
        self.logger.info("Creating burndown chart")

        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        weeks = [m.week for m in metrics_list]
        burndown = [m.burndown for m in metrics_list]

        # Create line with markers
        ax.plot(
            weeks,
            burndown,
            marker='o',
            linewidth=2.5,
            markersize=8,
            color=self.COLORS['burndown'],
            label='Burndown (Points Remaining)'
        )

        # Fill area under curve
        ax.fill_between(
            weeks,
            burndown,
            alpha=0.3,
            color=self.COLORS['burndown']
        )

        # Add value labels
        for week, bd in zip(weeks, burndown):
            ax.text(
                week,
                bd + max(burndown) * 0.03,
                f'{int(bd)}',
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold'
            )

        # Customize chart
        ax.set_xlabel('Week Number', fontweight='bold')
        ax.set_ylabel('Points Remaining', fontweight='bold')
        ax.set_title('Sprint Burndown Trend', fontweight='bold', pad=20)
        ax.set_xticks(weeks)
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Add zero line
        ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)

        plt.tight_layout()

        # Save chart
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Burndown chart saved to {output_path}")
        return str(output_path)

    def create_delivery_rate_chart(
        self,
        metrics_list: List[SprintMetrics],
        filename: str = 'sprint_delivery_rate_chart.png'
    ) -> str:
        """Create line chart for delivery rate with annotations

        Args:
            metrics_list: List of SprintMetrics
            filename: Output filename

        Returns:
            Path to saved chart
        """
        self.logger.info("Creating delivery rate chart")

        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        sprint_names = [m.sprint_name for m in metrics_list]
        delivery_rates = [m.delivery_rate for m in metrics_list]
        x = np.arange(len(sprint_names))

        # Create line with markers
        ax.plot(
            x,
            delivery_rates,
            marker='s',
            linewidth=2.5,
            markersize=10,
            color=self.COLORS['delivery_rate'],
            label='Delivery Rate'
        )

        # Add target line at 100%
        ax.axhline(
            y=100,
            color=self.COLORS['target'],
            linewidth=2,
            linestyle='--',
            alpha=0.7,
            label='Target (100%)'
        )

        # Add percentage labels above points
        for i, rate in enumerate(delivery_rates):
            ax.text(
                i,
                rate + 2,
                f'{rate:.1f}%',
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold',
                color=self.COLORS['delivery_rate']
            )

        # Customize chart
        ax.set_xlabel('Sprint', fontweight='bold')
        ax.set_ylabel('Delivery Rate (%)', fontweight='bold')
        ax.set_title('Sprint Delivery Rate Trend', fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(sprint_names, rotation=0)
        ax.set_ylim(0, max(110, max(delivery_rates) + 10))
        ax.legend(loc='lower right', framealpha=0.9)
        ax.grid(True, alpha=0.3)

        # Add color-coded background zones
        ax.axhspan(0, 70, alpha=0.1, color='red', label='Low')
        ax.axhspan(70, 90, alpha=0.1, color='orange', label='Medium')
        ax.axhspan(90, 110, alpha=0.1, color='green', label='High')

        plt.tight_layout()

        # Save chart
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        self.logger.info(f"Delivery rate chart saved to {output_path}")
        return str(output_path)

    def create_all_charts(
        self,
        metrics_list: List[SprintMetrics],
        velocity_filename: str = 'sprint_velocity_chart.png',
        burndown_filename: str = 'sprint_burndown_chart.png',
        delivery_filename: str = 'sprint_delivery_rate_chart.png'
    ) -> dict:
        """Create all charts

        Args:
            metrics_list: List of SprintMetrics
            velocity_filename: Velocity chart filename
            burndown_filename: Burndown chart filename
            delivery_filename: Delivery rate chart filename

        Returns:
            Dictionary with chart paths
        """
        self.logger.info("Creating all charts")

        charts = {
            'velocity': self.create_velocity_chart(metrics_list, velocity_filename),
            'burndown': self.create_burndown_chart(metrics_list, burndown_filename),
            'delivery_rate': self.create_delivery_rate_chart(metrics_list, delivery_filename)
        }

        self.logger.info(f"All charts created successfully")
        return charts
