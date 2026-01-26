#!/usr/bin/env python3
"""
Quick test script to verify database connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.db_client import OmniscientDBClient


def main():
    print("=" * 60)
    print("🔌 Testing Omniscient Database Connection")
    print("=" * 60)
    print()

    # Load environment variables
    load_dotenv()

    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    config = {}

    print("📋 Checking configuration...")
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"   ❌ Missing: {var}")
            print()
            print("Please create a .env file with your database credentials.")
            print("Use .env.example as a template:")
            print()
            print("  cp .env.example .env")
            print()
            sys.exit(1)
        config[var] = value
        # Mask password
        display_value = value if var != 'DB_PASSWORD' else '*' * len(value)
        print(f"   ✓ {var}: {display_value}")

    config['DB_PORT'] = int(os.getenv('DB_PORT', '3306'))
    print(f"   ✓ DB_PORT: {config['DB_PORT']}")
    print()

    # Test connection
    print("🔌 Attempting to connect...")
    try:
        db_client = OmniscientDBClient(
            host=config['DB_HOST'],
            port=config['DB_PORT'],
            database=config['DB_NAME'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD']
        )

        if db_client.test_connection():
            print("   ✓ Connection successful!")
            print()

            # Fetch sample data
            print("📊 Fetching sample data...")
            pr_data = db_client.fetch_pr_scores()

            if pr_data.empty:
                print("   ⚠️  No data found in pr_scores table")
            else:
                print(f"   ✓ Found {len(pr_data)} PR records")
                print(f"   ✓ Date range: {pr_data['created_at'].min()} to {pr_data['created_at'].max()}")
                print(f"   ✓ Contributors: {pr_data['github_user_id'].nunique()}")
                print(f"   ✓ Repositories: {pr_data['repository'].nunique()}")

            print()
            print("=" * 60)
            print("✅ Database connection test successful!")
            print("=" * 60)
            print()
            print("You can now run:")
            print("  python gather_okr_metrics.py")
            print()

        else:
            print("   ❌ Connection failed")
            sys.exit(1)

    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
        print("Please check:")
        print("  1. MySQL server is running")
        print("  2. Database credentials are correct")
        print("  3. Database name exists")
        print("  4. Network connectivity to database host")
        sys.exit(1)


if __name__ == '__main__':
    main()
