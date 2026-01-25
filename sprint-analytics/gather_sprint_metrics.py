#!/usr/bin/env python3
"""
ClickUp Sprint Metrics Analysis CLI

Collects sprint data from ClickUp, calculates KPIs with carryover detection,
and generates visualizations and reports.
"""

import argparse
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils import setup_logging, CacheHandler, ensure_directory
from src.clickup_client import ClickUpClient, RateLimiter
from src.metrics_calculator import SprintMetricsCalculator
from src.visualizer import SprintVisualizer
from src.report_generator import ReportGenerator


def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def load_sample_data(sample_path: str = 'data/sample_sprint.json') -> dict:
    """Load sample data for dry-run mode

    Args:
        sample_path: Path to sample data file

    Returns:
        Sample data dictionary
    """
    import json

    sample_file = Path(sample_path)
    if not sample_file.exists():
        raise FileNotFoundError(f"Sample data file not found: {sample_path}")

    with open(sample_file, 'r') as f:
        return json.load(f)


def create_sample_data() -> dict:
    """Create minimal sample data if file doesn't exist

    Returns:
        Sample data dictionary
    """
    # Create sample data for 2 sprints
    sample_data = {
        43: [
            {
                'id': 'task1',
                'name': 'Sample Task 1',
                'url': 'https://app.clickup.com/t/task1',
                'status': {'status': '8.0 deployed'},
                'points': 5,
                'custom_fields': []
            },
            {
                'id': 'task2',
                'name': 'Sample Task 2',
                'url': 'https://app.clickup.com/t/task2',
                'status': {'status': 'In Progress'},
                'points': 3,
                'custom_fields': []
            }
        ],
        44: [
            {
                'id': 'task2',  # Carried over from Sprint 43
                'name': 'Sample Task 2',
                'url': 'https://app.clickup.com/t/task2',
                'status': {'status': '8.0 deployed'},
                'points': 3,
                'custom_fields': []
            },
            {
                'id': 'task3',
                'name': 'Sample Task 3',
                'url': 'https://app.clickup.com/t/task3',
                'status': {'status': '8.0 deployed'},
                'points': 8,
                'custom_fields': []
            }
        ]
    }

    return sample_data


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='ClickUp Sprint Metrics Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (fetches data from ClickUp)
  python gather_sprint_metrics.py

  # Dry-run with sample data (no API calls)
  python gather_sprint_metrics.py --dry-run

  # Use cached data only
  python gather_sprint_metrics.py --cache

  # Force refresh from API
  python gather_sprint_metrics.py --refresh

  # Process specific sprints
  python gather_sprint_metrics.py --sprints 43 44 45

  # Custom output directory
  python gather_sprint_metrics.py --output-dir ./custom_output

  # Verbose logging
  python gather_sprint_metrics.py --verbose
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test with sample data (no API calls)'
    )

    parser.add_argument(
        '--cache',
        action='store_true',
        help='Use only cached data (fail if not cached)'
    )

    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Force refresh all data from API (ignore cache)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for charts and reports (default: output)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    parser.add_argument(
        '--sprints',
        type=int,
        nargs='+',
        help='Process specific sprint numbers only (e.g., --sprints 43 44 45)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)
    logger.info("=== ClickUp Sprint Metrics Analysis ===")

    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)

        # Ensure output directory exists
        output_dir = ensure_directory(args.output_dir)
        logger.info(f"Output directory: {output_dir}")

        # Merge all sprint configs (SMB Payment + Revenue & Growth)
        sprint_configs = config.get('sprints', [])
        revenue_growth_sprints = config.get('revenue_growth_sprints', [])

        # Merge both sprint lists
        all_sprint_configs = sprint_configs + revenue_growth_sprints

        # Filter sprints if requested
        if args.sprints:
            all_sprint_configs = [
                s for s in all_sprint_configs
                if s['sprint_number'] in args.sprints
            ]
            logger.info(f"Processing {len(all_sprint_configs)} selected sprints: {args.sprints}")
        else:
            logger.info(f"Processing {len(all_sprint_configs)} sprints ({len(sprint_configs)} SMB Payment + {len(revenue_growth_sprints)} Revenue & Growth)")

        sprint_configs = all_sprint_configs

        # Dry-run mode
        if args.dry_run:
            logger.info("DRY-RUN MODE: Using sample data")

            # Try to load sample data, create if doesn't exist
            try:
                all_sprints_data = load_sample_data()
            except FileNotFoundError:
                logger.warning("Sample data not found, creating minimal sample")
                all_sprints_data = create_sample_data()
                # Use only sample sprints in config
                sprint_configs = [s for s in sprint_configs if s['sprint_number'] in all_sprints_data]

        else:
            # Load environment variables
            load_dotenv()

            api_token = os.getenv('CLICKUP_API_TOKEN')
            if not api_token:
                logger.error("CLICKUP_API_TOKEN not found in environment")
                logger.error("Please set it in .env file or export it")
                return 1

            # Initialize components
            cache_config = config.get('cache', {})
            cache_handler = CacheHandler(
                cache_dir=cache_config.get('directory', 'data/cache'),
                ttl_hours=cache_config.get('ttl_hours', 24)
            )

            rate_limit_config = config.get('rate_limit', {})
            rate_limiter = RateLimiter(
                requests_per_minute=rate_limit_config.get('requests_per_minute', 80),
                burst_size=rate_limit_config.get('burst_size', 10)
            )

            clickup_client = ClickUpClient(
                api_token=api_token,
                cache_handler=cache_handler,
                rate_limiter=rate_limiter
            )

            # Determine cache usage
            use_cache = not args.refresh
            if args.cache:
                use_cache = True
                logger.info("Using cache-only mode")

            # Fetch all sprints data
            logger.info(f"Fetching data for {len(sprint_configs)} sprints...")
            all_sprints_data = clickup_client.fetch_all_sprints_data(
                sprint_configs=sprint_configs,
                user_id=config['user_id'],
                use_cache=use_cache
            )

            # Fetch Sprint Reporting view URLs for each sprint
            workspace_id = config.get('workspace_id', '3708016')
            logger.info("Fetching Sprint Reporting views...")

            for sprint_config in sprint_configs:
                list_id = sprint_config['list_id']

                # Ensure list URL is set
                if 'url' not in sprint_config:
                    sprint_config['url'] = f"https://app.clickup.com/{workspace_id}/v/li/{list_id}"

                # Fetch Sprint Reporting view as separate URL
                sprint_reporting_url = clickup_client.get_sprint_reporting_view(
                    list_id=list_id,
                    workspace_id=workspace_id,
                    use_cache=use_cache
                )

                if sprint_reporting_url:
                    sprint_config['sprint_reporting_url'] = sprint_reporting_url
                    logger.debug(f"Sprint {sprint_config['sprint_number']}: Sprint Reporting URL stored separately")

        # Calculate metrics
        logger.info("Calculating sprint metrics...")
        calculator = SprintMetricsCalculator(
            all_sprints_data=all_sprints_data,
            sprint_configs=sprint_configs,
            completion_keyword=config['completion_status']['keyword'],
            clickup_client=clickup_client if not args.dry_run else None
        )

        metrics_list = calculator.calculate_all_metrics()

        if not metrics_list:
            logger.error("No metrics calculated")
            return 1

        # Calculate overall statistics
        overall_stats = calculator.get_overall_statistics(metrics_list)

        # Print summary to console
        print("\n" + "=" * 60)
        print("SPRINT METRICS SUMMARY")
        print("=" * 60)
        print(f"Total Sprints: {overall_stats['total_sprints']}")
        print(f"Total Points Delivered: {overall_stats['total_delivered']} / {overall_stats['total_work']}")
        print(f"Average Delivery Rate: {overall_stats['avg_delivery_rate']:.1f}%")
        print(f"Average Velocity: {overall_stats['avg_points_per_sprint']:.1f} points/sprint")
        print(f"Best Sprint: {overall_stats['best_sprint']['name']} ({overall_stats['best_sprint']['delivery_rate']:.1f}%)")
        print(f"Worst Sprint: {overall_stats['worst_sprint']['name']} ({overall_stats['worst_sprint']['delivery_rate']:.1f}%)")
        print("=" * 60)
        print()

        # Generate visualizations
        logger.info("Generating charts...")
        visualizer = SprintVisualizer(output_dir=str(output_dir))
        chart_config = config.get('output', {}).get('charts', {})

        charts = visualizer.create_all_charts(
            metrics_list=metrics_list,
            velocity_filename=chart_config.get('velocity_chart', 'sprint_velocity_chart.png'),
            burndown_filename=chart_config.get('burndown_chart', 'sprint_burndown_chart.png'),
            delivery_filename=chart_config.get('delivery_rate_chart', 'sprint_delivery_rate_chart.png')
        )

        print("Generated Charts:")
        for chart_type, path in charts.items():
            print(f"  - {chart_type}: {path}")
        print()

        # Generate reports
        logger.info("Generating reports...")
        reporter = ReportGenerator(output_dir=str(output_dir))
        report_config = config.get('output', {}).get('reports', {})

        reports = reporter.generate_all_reports(
            metrics_list=metrics_list,
            overall_stats=overall_stats,
            json_filename=report_config.get('json', 'sprint_metrics.json'),
            csv_filename=report_config.get('csv', 'sprint_metrics.csv'),
            md_filename=report_config.get('markdown', 'sprint_summary.md')
        )

        print("Generated Reports:")
        for report_type, path in reports.items():
            print(f"  - {report_type}: {path}")
        print()

        logger.info("=== Analysis Complete ===")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1

    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML configuration: {e}")
        return 1

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
