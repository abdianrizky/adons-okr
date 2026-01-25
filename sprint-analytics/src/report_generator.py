"""Report generation in JSON, CSV, and Markdown formats"""

import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from .metrics_calculator import SprintMetrics


class ReportGenerator:
    """Generate sprint metrics reports in multiple formats"""

    # Indonesian public holidays 2025 (H2)
    INDONESIAN_HOLIDAYS_2025 = {
        '2025-08-17': 'Hari Kemerdekaan Indonesia',
        '2025-09-16': 'Maulid Nabi Muhammad SAW',
        '2025-12-25': 'Hari Raya Natal',
        '2025-12-26': 'Cuti Bersama Natal'
    }

    def __init__(self, output_dir: str = 'output'):
        """Initialize report generator

        Args:
            output_dir: Directory to save report files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('sprint_analytics.reports')

    def generate_json_report(
        self,
        metrics_list: List[SprintMetrics],
        overall_stats: Dict,
        filename: str = 'sprint_metrics.json'
    ) -> str:
        """Generate comprehensive JSON report

        Args:
            metrics_list: List of SprintMetrics
            overall_stats: Overall statistics dictionary
            filename: Output filename

        Returns:
            Path to saved report
        """
        self.logger.info("Generating JSON report")

        report = {
            'generated_at': self._get_timestamp(),
            'overall_statistics': overall_stats,
            'sprints': [m.to_dict() for m in metrics_list]
        }

        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"JSON report saved to {output_path}")
        return str(output_path)

    def generate_csv_report(
        self,
        metrics_list: List[SprintMetrics],
        filename: str = 'sprint_metrics.csv'
    ) -> str:
        """Generate CSV summary report

        Args:
            metrics_list: List of SprintMetrics
            filename: Output filename

        Returns:
            Path to saved report
        """
        self.logger.info("Generating CSV report")

        output_path = self.output_dir / filename

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Sprint Number',
                'Sprint Name',
                'Week',
                'Total Tasks',
                'Completed Tasks',
                'Points Committed',
                'Carryover In',
                'Total Work',
                'Points Delivered',
                'Carryover Out',
                'Burndown',
                'Delivery Rate (%)',
                'URL'
            ])

            # Data rows
            for m in metrics_list:
                writer.writerow([
                    m.sprint_number,
                    m.sprint_name,
                    m.week,
                    m.total_tasks,
                    m.completed_tasks_count,
                    m.points_committed,
                    m.carryover_in,
                    m.total_work,
                    m.points_delivered,
                    m.carryover_out,
                    m.burndown,
                    f'{m.delivery_rate:.2f}',
                    m.url
                ])

        self.logger.info(f"CSV report saved to {output_path}")
        return str(output_path)

    def _get_week_date_range(self, week_number: int, year: int = 2025) -> Tuple[str, str]:
        """Calculate date range for a given ISO week number (2-week sprint)

        Args:
            week_number: ISO week number (1-52)
            year: Year

        Returns:
            Tuple of (start_date, end_date) in YYYY-MM-DD format for 2-week sprint
        """
        # ISO week starts on Monday
        # Week 1 is the first week with a Thursday
        jan_4 = datetime(year, 1, 4)
        week_1_start = jan_4 - timedelta(days=jan_4.weekday())

        target_week_start = week_1_start + timedelta(weeks=week_number - 1)
        target_week_end = target_week_start + timedelta(days=13)  # 14 days (2 weeks)

        return (
            target_week_start.strftime('%Y-%m-%d'),
            target_week_end.strftime('%Y-%m-%d')
        )

    def _get_sprint_date_range(self, sprint_metrics: SprintMetrics) -> Tuple[str, str]:
        """Get sprint date range from API data or calculated from week number

        Args:
            sprint_metrics: SprintMetrics object

        Returns:
            Tuple of (start_date, end_date) in YYYY-MM-DD format
        """
        # Try to use real dates from API first
        if sprint_metrics.sprint_start_date and sprint_metrics.sprint_end_date:
            try:
                start_ts = int(sprint_metrics.sprint_start_date) if isinstance(sprint_metrics.sprint_start_date, str) else sprint_metrics.sprint_start_date
                end_ts = int(sprint_metrics.sprint_end_date) if isinstance(sprint_metrics.sprint_end_date, str) else sprint_metrics.sprint_end_date

                start_dt = datetime.fromtimestamp(start_ts / 1000)
                end_dt = datetime.fromtimestamp(end_ts / 1000)

                return (
                    start_dt.strftime('%Y-%m-%d'),
                    end_dt.strftime('%Y-%m-%d')
                )
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse sprint dates from API: {e}")

        # Fallback to calculated date range from week number
        return self._get_week_date_range(sprint_metrics.week)

    def _format_date_range(self, start_date: str, end_date: str) -> str:
        """Format date range in human-readable format

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Formatted string like "Sep 2-15, 2025"
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        if start.month == end.month:
            return f"{start.strftime('%b')} {start.day}-{end.day}, {start.year}"
        else:
            return f"{start.strftime('%b %d')} - {end.strftime('%b %d')}, {start.year}"

    def _check_indonesian_holidays(self, start_date: str, end_date: str) -> List[Dict]:
        """Check for Indonesian public holidays in date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of dicts with 'date' and 'name' keys
        """
        holidays = []
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        for date_str, holiday_name in self.INDONESIAN_HOLIDAYS_2025.items():
            holiday_date = datetime.strptime(date_str, '%Y-%m-%d')
            if start <= holiday_date <= end:
                holidays.append({
                    'date': date_str,
                    'name': holiday_name,
                    'formatted': holiday_date.strftime('%b %d')
                })

        return holidays

    def generate_markdown_report(
        self,
        metrics_list: List[SprintMetrics],
        overall_stats: Dict,
        filename: str = 'sprint_summary.md'
    ) -> str:
        """Generate Markdown summary report with insights

        Args:
            metrics_list: List of SprintMetrics
            overall_stats: Overall statistics dictionary
            filename: Output filename

        Returns:
            Path to saved report
        """
        self.logger.info("Generating Markdown report")

        lines = []

        # Title
        lines.append("# Sprint Analytics Report - H2 2025")
        lines.append("## SMB Payment Team")
        lines.append("")
        lines.append(f"*Generated: {self._get_timestamp()}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"**Total Sprints Analyzed:** {overall_stats['total_sprints']}")
        lines.append("")
        lines.append(f"**Total Points Delivered:** {overall_stats['total_delivered']} / {overall_stats['total_work']}")
        lines.append("")
        lines.append(f"**Average Delivery Rate:** {overall_stats['avg_delivery_rate']:.1f}%")
        lines.append("")
        lines.append(f"**Average Velocity:** {overall_stats['avg_points_per_sprint']:.1f} points/sprint")
        lines.append("")
        lines.append("")

        # Best/Worst Performance
        lines.append("### Performance Highlights")
        lines.append("")
        lines.append(f"**Best Sprint:** {overall_stats['best_sprint']['name']} "
                    f"({overall_stats['best_sprint']['delivery_rate']:.1f}% delivery rate)")
        lines.append("")
        lines.append(f"**Worst Sprint:** {overall_stats['worst_sprint']['name']} "
                    f"({overall_stats['worst_sprint']['delivery_rate']:.1f}% delivery rate)")
        lines.append("")
        lines.append("")

        # Insights
        insights = self._generate_insights(metrics_list, overall_stats)
        if insights:
            lines.append("### Key Insights")
            lines.append("")
            for insight in insights:
                lines.append(f"- {insight}")
            lines.append("")
            lines.append("")

        # Visualizations
        lines.append("## Visualizations")
        lines.append("")
        lines.append("")
        lines.append("### Sprint Velocity")
        lines.append("")
        lines.append("![Sprint Velocity](sprint_velocity_chart.png)")
        lines.append("")
        lines.append("*Comparison of Points Committed, Delivered, and Carried Over across sprints*")
        lines.append("")
        lines.append("")
        lines.append("### Burndown Trend")
        lines.append("")
        lines.append("![Burndown Trend](sprint_burndown_chart.png)")
        lines.append("")
        lines.append("*Points remaining (burndown) over time*")
        lines.append("")
        lines.append("")
        lines.append("### Delivery Rate")
        lines.append("")
        lines.append("![Delivery Rate](sprint_delivery_rate_chart.png)")
        lines.append("")
        lines.append("*Percentage of work delivered per sprint (target: 100%)*")
        lines.append("")
        lines.append("")

        # Overall Statistics Table
        lines.append("## Overall Statistics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Committed | {overall_stats['total_committed']} points |")
        lines.append(f"| Total Carryover In | {overall_stats['total_carryover_in']} points |")
        lines.append(f"| Total Work | {overall_stats['total_work']} points |")
        lines.append(f"| Total Delivered | {overall_stats['total_delivered']} points |")
        lines.append(f"| Total Carryover Out | {overall_stats['total_carryover_out']} points |")
        lines.append(f"| Velocity Consistency (σ) | {overall_stats['velocity_std_dev']:.2f} points |")
        lines.append("")
        lines.append("")

        # Sprint-by-Sprint Breakdown
        lines.append("## Sprint-by-Sprint Breakdown")
        lines.append("")
        lines.append("")

        for m in metrics_list:
            # Calculate date range (use API dates if available)
            start_date, end_date = self._get_sprint_date_range(m)
            date_range = self._format_date_range(start_date, end_date)

            # Check for holidays
            holidays = self._check_indonesian_holidays(start_date, end_date)

            # Sprint header with date range (no week number)
            lines.append(f"### [{m.sprint_name}]({m.url})")
            lines.append("")
            lines.append(f"**{date_range}**")
            lines.append("")

            # Add Sprint Reporting link if available
            if m.sprint_reporting_url:
                lines.append(f"📊 **[Sprint Reporting Dashboard]({m.sprint_reporting_url})**")
                lines.append("")

            # Add holiday information if exists
            if holidays:
                holiday_text = ", ".join([f"🔴 {h['formatted']} ({h['name']})" for h in holidays])
                lines.append(f"*Tanggal Merah: {holiday_text}*")
                lines.append("")

            # Performance badge
            if m.delivery_rate >= 100:
                badge = "🌟 **Perfect Sprint!**"
            elif m.delivery_rate >= 90:
                badge = "✅ **Excellent Performance**"
            elif m.delivery_rate >= 75:
                badge = "👍 **Good Performance**"
            elif m.delivery_rate >= 50:
                badge = "⚠️ **Needs Improvement**"
            else:
                badge = "❌ **Critical**"

            lines.append(badge)
            lines.append("")
            lines.append("")

            # Metrics table
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            lines.append(f"| 📅 Date Range | {date_range} |")
            lines.append(f"| 📊 Points Committed | {m.points_committed} |")
            lines.append(f"| ⬆️ Carryover In | {m.carryover_in} |")
            lines.append(f"| 💼 Total Work | {m.total_work} |")
            lines.append(f"| ✅ Points Delivered | {m.points_delivered} |")
            lines.append(f"| ⬇️ Carryover Out | {m.carryover_out} |")
            lines.append(f"| 🔥 Burndown | {m.burndown} |")
            lines.append(f"| 🎯 **Delivery Rate** | **{m.delivery_rate:.1f}%** |")
            lines.append(f"| 📋 Tasks Completed | {m.completed_tasks_count} / {m.total_tasks} |")
            lines.append("")
            lines.append("")

            # Completed tasks
            if m.completed_tasks:
                lines.append("**Completed Tasks:**")
                lines.append("")
                for task in m.completed_tasks:
                    lines.append(f"- [{task.name}]({task.url}) - {task.points} pts")
                lines.append("")
                lines.append("")

            # Carryover in
            if m.carryover_in_tasks:
                lines.append("**Carried In from Previous Sprint:**")
                lines.append("")
                for task in m.carryover_in_tasks:
                    lines.append(f"- [{task['name']}]({task['url']}) - {task['points']} pts "
                               f"(from Sprint {task['from_sprint']})")
                lines.append("")
                lines.append("")

            # Carryover out
            if m.carryover_out_tasks:
                lines.append("**Carried Out to Next Sprint:**")
                lines.append("")
                for task in m.carryover_out_tasks:
                    next_sprint = task['to_sprint'] if task['to_sprint'] else "unknown"
                    lines.append(f"- [{task['name']}]({task['url']}) - {task['points']} pts "
                               f"(to Sprint {next_sprint})")
                lines.append("")
                lines.append("")

            lines.append("---")
            lines.append("")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("")
        lines.append("## About This Report")
        lines.append("")
        lines.append("This report was automatically generated by the Sprint Analytics system.")
        lines.append("")
        lines.append("")
        lines.append("**Report Contents:**")
        lines.append("")
        lines.append("- Executive summary with key performance indicators")
        lines.append("- Visual charts for velocity, burndown, and delivery rate")
        lines.append("- Detailed sprint-by-sprint breakdown with task lists")
        lines.append("- Indonesian public holiday indicators")
        lines.append("- Automated insights and recommendations")
        lines.append("")
        lines.append("")
        lines.append("**Files Generated:**")
        lines.append("")
        lines.append("- `sprint_summary.md` - This comprehensive report")
        lines.append("- `sprint_metrics.json` - Complete data in JSON format")
        lines.append("- `sprint_metrics.csv` - Summary data for Excel/Sheets")
        lines.append("- `sprint_velocity_chart.png` - Velocity comparison chart")
        lines.append("- `sprint_burndown_chart.png` - Burndown trend chart")
        lines.append("- `sprint_delivery_rate_chart.png` - Delivery rate chart")
        lines.append("")
        lines.append("")
        lines.append("**Legend:**")
        lines.append("")
        lines.append("- 🌟 Perfect Sprint (≥100% delivery)")
        lines.append("- ✅ Excellent Performance (90-99%)")
        lines.append("- 👍 Good Performance (75-89%)")
        lines.append("- ⚠️ Needs Improvement (50-74%)")
        lines.append("- ❌ Critical (<50%)")
        lines.append("- 🔴 Tanggal Merah (Indonesian Public Holiday)")
        lines.append("")

        # Write to file
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

        self.logger.info(f"Markdown report saved to {output_path}")
        return str(output_path)

    def _generate_insights(
        self,
        metrics_list: List[SprintMetrics],
        overall_stats: Dict
    ) -> List[str]:
        """Generate automated insights from metrics

        Args:
            metrics_list: List of SprintMetrics
            overall_stats: Overall statistics dictionary

        Returns:
            List of insight strings
        """
        insights = []

        # Trend analysis
        if len(metrics_list) >= 3:
            first_half = metrics_list[:len(metrics_list)//2]
            second_half = metrics_list[len(metrics_list)//2:]

            avg_first = sum(m.delivery_rate for m in first_half) / len(first_half)
            avg_second = sum(m.delivery_rate for m in second_half) / len(second_half)

            if avg_second > avg_first + 5:
                insights.append(
                    f"Delivery rate is **improving** over time "
                    f"(first half: {avg_first:.1f}%, second half: {avg_second:.1f}%)"
                )
            elif avg_second < avg_first - 5:
                insights.append(
                    f"Delivery rate is **declining** over time "
                    f"(first half: {avg_first:.1f}%, second half: {avg_second:.1f}%)"
                )
            else:
                insights.append(
                    f"Delivery rate remains **consistent** "
                    f"(avg: {overall_stats['avg_delivery_rate']:.1f}%)"
                )

        # Carryover pattern
        total_carryover = overall_stats['total_carryover_out']
        if total_carryover > overall_stats['total_delivered'] * 0.2:
            insights.append(
                f"High carryover detected: {total_carryover} points carried over "
                f"({total_carryover / overall_stats['total_work'] * 100:.1f}% of total work)"
            )

        # Velocity consistency
        if overall_stats['velocity_std_dev'] < 5:
            insights.append(
                f"Very **consistent velocity** (σ = {overall_stats['velocity_std_dev']:.2f} points)"
            )
        elif overall_stats['velocity_std_dev'] > 15:
            insights.append(
                f"**Variable velocity** detected (σ = {overall_stats['velocity_std_dev']:.2f} points) - "
                f"consider investigating sprint planning consistency"
            )

        # High performers
        high_performers = [m for m in metrics_list if m.delivery_rate >= 100]
        if len(high_performers) >= len(metrics_list) * 0.5:
            insights.append(
                f"**Strong performance**: {len(high_performers)} out of {len(metrics_list)} sprints "
                f"achieved 100%+ delivery rate"
            )

        return insights

    def _get_timestamp(self) -> str:
        """Get current timestamp string

        Returns:
            Formatted timestamp
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate_all_reports(
        self,
        metrics_list: List[SprintMetrics],
        overall_stats: Dict,
        json_filename: str = 'sprint_metrics.json',
        csv_filename: str = 'sprint_metrics.csv',
        md_filename: str = 'sprint_summary.md'
    ) -> dict:
        """Generate all report formats

        Args:
            metrics_list: List of SprintMetrics
            overall_stats: Overall statistics dictionary
            json_filename: JSON report filename
            csv_filename: CSV report filename
            md_filename: Markdown report filename

        Returns:
            Dictionary with report paths
        """
        self.logger.info("Generating all reports")

        reports = {
            'json': self.generate_json_report(metrics_list, overall_stats, json_filename),
            'csv': self.generate_csv_report(metrics_list, csv_filename),
            'markdown': self.generate_markdown_report(
                metrics_list,
                overall_stats,
                md_filename
            )
        }

        self.logger.info("All reports generated successfully")
        return reports
