#!/usr/bin/env python3
"""
Generate OKR Report for a specific user and date range

Usage:
    python generate_user_report.py --user user@email.com --start-date 2025-07-01 --end-date 2025-12-31
    python generate_user_report.py --user user@email.com --period H2-2025
    python generate_user_report.py --user user@email.com --period Q3-2025
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

import pymysql
import pandas as pd
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.db_client import OmniscientDBClient
from src.metrics_calculator import OKRMetricsCalculator
from src.visualizer import OKRVisualizer
from src.report_generator import OKRReportGenerator


def parse_period(period: str, year: int = None) -> tuple:
    """Parse period string to start and end dates

    Args:
        period: Period string (e.g., 'Q1-2025', 'H2-2025', 'Jan-2025')
        year: Optional year override

    Returns:
        Tuple of (start_date, end_date)
    """
    if not year and '-' in period:
        period_name, year_str = period.split('-')
        year = int(year_str)
    elif not year:
        year = datetime.now().year
        period_name = period
    else:
        period_name = period

    period_name = period_name.upper()

    # Quarterly periods
    quarters = {
        'Q1': ('01-01', '03-31'),
        'Q2': ('04-01', '06-30'),
        'Q3': ('07-01', '09-30'),
        'Q4': ('10-01', '12-31'),
    }

    # Half-yearly periods
    halves = {
        'H1': ('01-01', '06-30'),
        'H2': ('07-01', '12-31'),
    }

    # Monthly periods
    months = {
        'JAN': ('01-01', '01-31'), 'FEB': ('02-01', '02-28'),
        'MAR': ('03-01', '03-31'), 'APR': ('04-01', '04-30'),
        'MAY': ('05-01', '05-31'), 'JUN': ('06-01', '06-30'),
        'JUL': ('07-01', '07-31'), 'AUG': ('08-01', '08-31'),
        'SEP': ('09-01', '09-30'), 'OCT': ('10-01', '10-31'),
        'NOV': ('11-01', '11-30'), 'DEC': ('12-01', '12-31'),
    }

    all_periods = {**quarters, **halves, **months}

    if period_name in all_periods:
        start_month_day, end_month_day = all_periods[period_name]
        return f"{year}-{start_month_day}", f"{year}-{end_month_day}"
    elif period_name == 'YTD':
        return f"{year}-01-01", datetime.now().strftime('%Y-%m-%d')
    else:
        raise ValueError(f"Unknown period: {period}. Use Q1-Q4, H1-H2, month names, or YTD")


def main():
    parser = argparse.ArgumentParser(
        description='Generate OKR report for a specific user',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report with all data up to a specific date
  python generate_user_report.py --user adon-paper --end-date 2025-12-31

  # Generate H2 2025 report
  python generate_user_report.py --user adon-paper --period H2-2025

  # Generate Q3 2025 report
  python generate_user_report.py --user john.doe@paper.id --period Q3-2025

  # Generate custom date range report
  python generate_user_report.py --user jane@paper.id --start-date 2025-01-01 --end-date 2025-06-30

  # Generate YTD report
  python generate_user_report.py --user user@paper.id --period YTD

  # Generate all data from beginning to today
  python generate_user_report.py --user adon-paper --end-date $(date +%Y-%m-%d)
        """
    )

    parser.add_argument(
        '--user',
        type=str,
        required=True,
        help='GitHub user email (e.g., user@paper.id)'
    )

    parser.add_argument(
        '--period',
        type=str,
        help='Period (e.g., H2-2025, Q3-2025, JAN-2025, YTD)'
    )

    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date (YYYY-MM-DD). Overrides --period. Omit to use earliest data.'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        help='End date (YYYY-MM-DD). Required if --start-date is omitted. Use alone to get all data from beginning.'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='Skip chart generation'
    )

    args = parser.parse_args()

    # Determine date range
    if args.end_date and not args.start_date and not args.period:
        # Just end-date specified: get all data from beginning to end_date
        start_date = None  # Will fetch earliest date from database
        end_date = args.end_date
        period_name = f"all_to_{end_date.replace('-', '_')}"
    elif args.start_date and args.end_date:
        start_date = args.start_date
        end_date = args.end_date
        period_name = f"{start_date}_to_{end_date}".replace('-', '_')
    elif args.period:
        start_date, end_date = parse_period(args.period)
        period_name = args.period.replace('-', '_')
    else:
        print("❌ Error: Must specify one of:")
        print("  - --period PERIOD")
        print("  - --end-date DATE (for all data up to date)")
        print("  - --start-date DATE --end-date DATE (for custom range)")
        parser.print_help()
        sys.exit(1)

    # Clean user identifier for folder name
    user_folder = args.user.replace('@', '_at_').replace('.', '_')

    print("=" * 70)
    print(f"🎯 Generating OKR Report for {args.user}")
    print("=" * 70)
    print()
    print(f"📋 Report Configuration:")
    print(f"   User: {args.user}")
    print(f"   Period: {period_name}")
    if start_date:
        print(f"   Date Range: {start_date} to {end_date}")
    else:
        print(f"   Date Range: All data from beginning to {end_date}")
    print()

    # Load database configuration
    load_dotenv()

    try:
        db_config = {
            'DB_HOST': os.getenv('DB_HOST'),
            'DB_PORT': int(os.getenv('DB_PORT', '3306')),
            'DB_NAME': os.getenv('DB_NAME'),
            'DB_USER': os.getenv('DB_USER'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD')
        }

        # Validate configuration
        missing = [k for k, v in db_config.items() if v is None and k != 'DB_PORT']
        if missing:
            print(f"❌ Missing configuration: {', '.join(missing)}")
            print()
            print("Please set up your .env file with MySQL credentials:")
            print("  cp .env.example .env")
            print("  # Edit .env with your credentials")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Connect to database
    print("🔌 Connecting to database...")
    try:
        db_client = OmniscientDBClient(
            host=db_config['DB_HOST'],
            port=db_config['DB_PORT'],
            database=db_config['DB_NAME'],
            user=db_config['DB_USER'],
            password=db_config['DB_PASSWORD']
        )
        print("   ✓ Connected successfully")
        print()
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        sys.exit(1)

    # Fetch data
    print("📊 Fetching PR data...")
    try:
        # Fetch all data for the period
        all_data = db_client.fetch_pr_scores(
            start_date=start_date,
            end_date=end_date
        )

        if all_data.empty:
            print(f"   ⚠️  No data found for period {start_date} to {end_date}")
            sys.exit(1)

        print(f"   ✓ Fetched {len(all_data)} total PR records for the period")

        # Filter for specific user
        user_data = all_data[all_data['github_user_id'] == args.user]

        if user_data.empty:
            print(f"   ⚠️  No PRs found for {args.user} in the specified period")
            print()
            print(f"Available users in this period ({len(all_data['github_user_id'].unique())} total):")
            for user in sorted(all_data['github_user_id'].unique())[:20]:
                count = len(all_data[all_data['github_user_id'] == user])
                print(f"     - {user}: {count} PRs")
            if len(all_data['github_user_id'].unique()) > 20:
                print(f"     ... and {len(all_data['github_user_id'].unique()) - 20} more")
            sys.exit(1)

        print(f"   ✓ Found {len(user_data)} PRs for {args.user}")
        print()

    except Exception as e:
        print(f"   ❌ Error fetching data: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Calculate metrics
    print("🧮 Calculating metrics...")
    try:
        calculator = OKRMetricsCalculator(user_data)
        metrics = calculator.calculate_all_metrics()

        print(f"   ✓ Average overall score: {metrics['summary']['avg_overall_score']:.2f}")
        print(f"   ✓ Total PRs: {metrics['summary']['total_prs']}")
        print(f"   ✓ Repositories: {metrics['summary']['total_repositories']}")
        print()
    except Exception as e:
        print(f"   ❌ Error calculating metrics: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Create output directories
    output_dir = Path('output') / user_folder / period_name
    reports_dir = Path('reports') / user_folder / period_name
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualizations
    if not args.no_charts:
        print("📈 Generating visualizations...")
        try:
            visualizer = OKRVisualizer(user_data, metrics)

            charts = {
                'pr_quality_trend': visualizer.plot_pr_quality_trend(),
                'score_distribution': visualizer.plot_score_distribution(),
                'category_heatmap': visualizer.plot_category_heatmap(),
                'decision_breakdown': visualizer.plot_decision_breakdown(),
                'monthly_pr_volume': visualizer.plot_monthly_pr_volume()
            }

            # Move charts to user-specific folder
            for chart_name, chart_path in charts.items():
                if Path(chart_path).exists():
                    new_path = output_dir / Path(chart_path).name
                    Path(chart_path).rename(new_path)
                    print(f"   ✓ Generated: {new_path}")

            print()
        except Exception as e:
            print(f"   ⚠️  Warning: Could not generate all charts: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            print()

    # Generate reports
    print("📝 Generating reports...")
    try:
        # Save JSON and CSV
        json_file = output_dir / 'okr_metrics.json'
        csv_file = output_dir / 'pr_data.csv'
        md_file = reports_dir / 'okr_report.md'

        # Generate custom markdown report
        generate_custom_markdown_report(
            user_data, metrics, args.user, period_name,
            start_date, end_date, md_file, user_folder, args.no_charts
        )

        # Save JSON and CSV
        import json
        with open(json_file, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

        user_data.to_csv(csv_file, index=False)

        print(f"   ✓ Generated: {json_file}")
        print(f"   ✓ Generated: {csv_file}")
        print(f"   ✓ Generated: {md_file}")
        print()

    except Exception as e:
        print(f"   ❌ Error generating reports: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Summary
    print("=" * 70)
    print("✅ Report Generated Successfully!")
    print("=" * 70)
    print()
    print(f"📂 Report Location: {reports_dir}/")
    print(f"📂 Charts & Data: {output_dir}/")
    print()
    print("📄 Files generated:")
    print(f"   • {md_file}")
    print(f"   • {json_file}")
    print(f"   • {csv_file}")
    print()
    print("📊 View report:")
    print(f"   open {md_file}")
    print()


def generate_custom_markdown_report(pr_data, metrics, user, period_name, start_date, end_date, output_path, user_folder, no_charts=False):
    """Generate a custom markdown report for the user"""

    summary = metrics['summary']
    category_scores = metrics['category_scores']
    decision_dist = metrics['decision_distribution']

    md_content = f"""# OKR Report: {user}

**Period:** {period_name.replace('_', ' ').upper()} ({start_date} to {end_date})
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

### Performance Overview
- **Total PRs:** {summary['total_prs']}
- **Repositories Contributed:** {summary['total_repositories']}
- **Average Overall Score:** {summary['avg_overall_score']:.2f} / 40
- **Median Overall Score:** {summary['median_overall_score']:.2f} / 40
- **Performance Grade:** {calculate_grade(summary['avg_overall_score'])}

### Key Achievements
"""

    # Add top-performing categories
    if category_scores:
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        md_content += "\n**Strengths:**\n"
        for i, (category, score) in enumerate(sorted_categories[:3], 1):
            rating = score_to_rating(score)
            md_content += f"{i}. **{category.replace('_', ' ').title()}**: {score:.2f}/5 - {rating}\n"

    md_content += "\n---\n\n## Quality Metrics Breakdown\n\n"

    # Add category scores table
    if category_scores:
        md_content += "| Category | Score (1-5) | Rating |\n"
        md_content += "|----------|-------------|--------|\n"

        for category, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True):
            rating = score_to_rating(score)
            md_content += f"| {category.replace('_', ' ').title()} | {score:.2f} | {rating} |\n"

        md_content += "\n"

    md_content += """---

## PR Decision Distribution

"""

    # Add decision distribution
    if decision_dist:
        md_content += "| Decision | Count | Percentage |\n"
        md_content += "|----------|-------|------------|\n"

        total_decisions = sum(decision_dist.values())
        for decision, count in sorted(decision_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_decisions) * 100
            md_content += f"| {decision} | {count} | {percentage:.1f}% |\n"

        md_content += "\n"

    # Add visualizations if generated
    if not no_charts:
        md_content += """---

## Visualizations

### Quality Trend Over Time
![PR Quality Trend](../../../output/{user_folder}/{period_name}/pr_quality_trend.png)

### Score Distribution
![Score Distribution](../../../output/{user_folder}/{period_name}/score_distribution.png)

### Category Performance
![Category Heatmap](../../../output/{user_folder}/{period_name}/category_heatmap.png)

### Decision Breakdown
![Decision Breakdown](../../../output/{user_folder}/{period_name}/decision_breakdown.png)

### Monthly Activity
![Monthly PR Volume](../../../output/{user_folder}/{period_name}/monthly_pr_volume.png)

""".replace('{user_folder}', user_folder).replace('{period_name}', period_name)

    md_content += """---

## Recommendations

Based on the performance analysis:

"""

    # Add recommendations based on scores
    if category_scores:
        low_categories = [(cat, score) for cat, score in category_scores.items() if score < 3.0]
        if low_categories:
            md_content += "### Areas for Improvement\n\n"
            for cat, score in sorted(low_categories, key=lambda x: x[1]):
                md_content += f"- **{cat.replace('_', ' ').title()}** (Score: {score:.2f}/5): Focus on improving this area\n"
            md_content += "\n"

    md_content += """### General Recommendations

1. **Maintain Strengths**: Continue excellent performance in top-scoring categories
2. **Address Gaps**: Focus improvement efforts on categories scoring below 3.0
3. **Peer Learning**: Review high-quality PRs from top performers
4. **Best Practices**: Follow coding standards and quality guidelines consistently

---

## Repository Breakdown

"""

    # Add per-repository stats
    repo_stats = pr_data.groupby('repository').agg({
        'pr_number': 'count',
        'overall_score': 'mean'
    }).reset_index()
    repo_stats.columns = ['Repository', 'PRs', 'Avg Score']
    repo_stats = repo_stats.sort_values('PRs', ascending=False)

    md_content += "| Repository | PRs | Average Score |\n"
    md_content += "|------------|-----|---------------|\n"

    for _, row in repo_stats.iterrows():
        md_content += f"| {row['Repository']} | {row['PRs']} | {row['Avg Score']:.2f} |\n"

    md_content += f"""

---

## Data Files

- **[JSON Metrics](../../../output/{user_folder}/{period_name}/okr_metrics.json)** - Complete structured data
- **[CSV Data](../../../output/{user_folder}/{period_name}/pr_data.csv)** - Raw PR records

---

*This report was automatically generated by the Omniscient OKR Analytics system.*
""".replace('{user_folder}', user_folder).replace('{period_name}', period_name)

    # Write to file
    with open(output_path, 'w') as f:
        f.write(md_content)


def calculate_grade(score: float) -> str:
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
        return "F (Needs Significant Improvement)"


def score_to_rating(score: float) -> str:
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


if __name__ == '__main__':
    main()
