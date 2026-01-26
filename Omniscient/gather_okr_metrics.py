#!/usr/bin/env python3
"""
Omniscient OKR Metrics Gathering Script

Collects PR quality data from the omniscient database,
calculates OKR metrics, and generates visualizations and reports.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

import pymysql
import pandas as pd
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.db_client import OmniscientDBClient
from src.metrics_calculator import OKRMetricsCalculator
from src.visualizer import OKRVisualizer
from src.report_generator import OKRReportGenerator


def load_env_config() -> Dict[str, str]:
    """Load configuration from .env file

    Returns:
        Configuration dictionary

    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv()

    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    config = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value

    # Optional variables with defaults
    config['DB_PORT'] = int(os.getenv('DB_PORT', '3306'))
    config['START_DATE'] = os.getenv('START_DATE', None)
    config['END_DATE'] = os.getenv('END_DATE', None)

    return config


def ensure_directories():
    """Ensure output directories exist"""
    directories = ['output', 'data', 'reports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Ensured directory: {directory}/")


def main():
    parser = argparse.ArgumentParser(
        description='Gather OKR metrics from Omniscient database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full OKR report
  python gather_okr_metrics.py

  # Specify custom date range
  python gather_okr_metrics.py --start-date 2025-01-01 --end-date 2025-06-30

  # Output only JSON (no visualizations)
  python gather_okr_metrics.py --format json

  # Verbose output
  python gather_okr_metrics.py -v
        """
    )

    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for report (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        help='End date for report (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--format',
        choices=['all', 'json', 'csv', 'markdown'],
        default='all',
        help='Output format (default: all)'
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

    print("=" * 60)
    print("🎯 Omniscient OKR Metrics Generator")
    print("=" * 60)
    print()

    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_env_config()

        # Override with command line args if provided
        if args.start_date:
            config['START_DATE'] = args.start_date
        if args.end_date:
            config['END_DATE'] = args.end_date

        print(f"   Database: {config['DB_NAME']} @ {config['DB_HOST']}:{config['DB_PORT']}")
        if config['START_DATE']:
            print(f"   Date Range: {config['START_DATE']} to {config['END_DATE']}")
        else:
            print(f"   Date Range: All available data")
        print()

        # Ensure directories exist
        print("📁 Setting up directories...")
        ensure_directories()
        print()

        # Initialize database client
        print("🔌 Connecting to database...")
        db_client = OmniscientDBClient(
            host=config['DB_HOST'],
            port=config['DB_PORT'],
            database=config['DB_NAME'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD']
        )
        print("   ✓ Connected successfully")
        print()

        # Fetch PR data
        print("📊 Fetching PR data...")
        pr_data = db_client.fetch_pr_scores(
            start_date=config['START_DATE'],
            end_date=config['END_DATE']
        )

        if pr_data.empty:
            print("   ⚠️  No data found for the specified date range")
            return

        print(f"   ✓ Fetched {len(pr_data)} PR records")
        print()

        # Calculate metrics
        print("🧮 Calculating OKR metrics...")
        calculator = OKRMetricsCalculator(pr_data)
        metrics = calculator.calculate_all_metrics()

        print(f"   ✓ Calculated metrics for {metrics['summary']['total_prs']} PRs")
        print(f"   ✓ Total contributors: {metrics['summary']['total_contributors']}")
        print(f"   ✓ Average overall score: {metrics['summary']['avg_overall_score']:.2f}")
        print()

        # Generate visualizations
        if not args.no_charts:
            print("📈 Generating visualizations...")
            visualizer = OKRVisualizer(pr_data, metrics)

            charts = {
                'pr_quality_trend': visualizer.plot_pr_quality_trend(),
                'score_distribution': visualizer.plot_score_distribution(),
                'contributor_performance': visualizer.plot_contributor_performance(),
                'category_heatmap': visualizer.plot_category_heatmap(),
                'decision_breakdown': visualizer.plot_decision_breakdown(),
                'monthly_pr_volume': visualizer.plot_monthly_pr_volume()
            }

            for chart_name, chart_path in charts.items():
                print(f"   ✓ Generated: {chart_path}")
            print()

        # Generate reports
        print("📝 Generating reports...")
        report_generator = OKRReportGenerator(pr_data, metrics)

        generated_files = []

        if args.format in ['all', 'json']:
            json_file = report_generator.save_json()
            generated_files.append(json_file)
            print(f"   ✓ Generated: {json_file}")

        if args.format in ['all', 'csv']:
            csv_file = report_generator.save_csv()
            generated_files.append(csv_file)
            print(f"   ✓ Generated: {csv_file}")

        if args.format in ['all', 'markdown']:
            md_file = report_generator.save_markdown()
            generated_files.append(md_file)
            print(f"   ✓ Generated: {md_file}")

        print()
        print("=" * 60)
        print("✅ OKR Report Generated Successfully!")
        print("=" * 60)
        print()
        print("📂 Generated files:")
        for file in generated_files:
            print(f"   • {file}")

        if not args.no_charts:
            print()
            print("📊 View charts in: output/")

        print()
        print("🎉 Done!")

    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except pymysql.Error as e:
        print(f"❌ Database error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
