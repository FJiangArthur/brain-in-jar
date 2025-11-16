#!/usr/bin/env python3
"""
Launcher script for the Experiment Comparison Dashboard.

Starts a Streamlit server with the comparison dashboard interface.

Usage:
    python scripts/run_comparison_dashboard.py --db logs/experiments.db --port 8501

    # Or from Jetson Orin, connecting to remote database:
    python scripts/run_comparison_dashboard.py --db /mnt/jetson/logs/experiments.db --port 8501

    # With custom host (to allow remote access):
    python scripts/run_comparison_dashboard.py --host 0.0.0.0 --port 8501
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Launch the Brain-in-Jar Experiment Comparison Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch with default settings
  python scripts/run_comparison_dashboard.py

  # Specify custom database and port
  python scripts/run_comparison_dashboard.py --db logs/experiments.db --port 8502

  # Allow remote connections (useful for Jetson Orin)
  python scripts/run_comparison_dashboard.py --host 0.0.0.0 --port 8501

  # Custom theme
  python scripts/run_comparison_dashboard.py --theme dark
        """
    )

    parser.add_argument(
        '--db',
        type=str,
        default='logs/experiments.db',
        help='Path to experiments database (default: logs/experiments.db)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Port number for dashboard server (default: 8501)'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host address to bind to (default: localhost, use 0.0.0.0 for remote access)'
    )

    parser.add_argument(
        '--theme',
        type=str,
        choices=['light', 'dark'],
        default='light',
        help='Dashboard theme (default: light)'
    )

    parser.add_argument(
        '--browser',
        action='store_true',
        help='Automatically open browser (default: False)'
    )

    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode with auto-reload'
    )

    return parser.parse_args()


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['streamlit', 'plotly', 'pandas', 'scipy']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:", ', '.join(missing_packages))
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False

    return True


def check_database(db_path: str):
    """Check if database exists and is accessible."""
    db_file = Path(db_path)

    if not db_file.exists():
        print(f"⚠️  Database not found at: {db_path}")
        print("\nThe dashboard will start, but you'll need a database with experiments.")
        print("Run an experiment first to populate the database.")
        response = input("\nContinue anyway? [y/N]: ")
        if response.lower() != 'y':
            return False

    return True


def create_streamlit_config(theme: str):
    """Create Streamlit configuration file."""
    config_dir = Path.home() / '.streamlit'
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / 'config.toml'

    theme_settings = {
        'light': {
            'primaryColor': '#1f77b4',
            'backgroundColor': '#ffffff',
            'secondaryBackgroundColor': '#f0f2f6',
            'textColor': '#262730',
        },
        'dark': {
            'primaryColor': '#ff6b6b',
            'backgroundColor': '#0e1117',
            'secondaryBackgroundColor': '#262730',
            'textColor': '#fafafa',
        }
    }

    config_content = f"""
[theme]
primaryColor = "{theme_settings[theme]['primaryColor']}"
backgroundColor = "{theme_settings[theme]['backgroundColor']}"
secondaryBackgroundColor = "{theme_settings[theme]['secondaryBackgroundColor']}"
textColor = "{theme_settings[theme]['textColor']}"
font = "sans serif"

[server]
headless = true
runOnSave = true
fileWatcherType = "auto"

[browser]
gatherUsageStats = false
"""

    with open(config_file, 'w') as f:
        f.write(config_content)

    return config_file


def main():
    """Main entry point."""
    args = parse_args()

    print("🧠 Brain-in-Jar: Experiment Comparison Dashboard")
    print("=" * 60)

    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed")

    # Check database
    print(f"\n🗄️  Checking database: {args.db}")
    if not check_database(args.db):
        sys.exit(1)
    print("✅ Database accessible")

    # Create Streamlit config
    print(f"\n🎨 Setting up {args.theme} theme...")
    config_file = create_streamlit_config(args.theme)
    print(f"✅ Config created: {config_file}")

    # Get the absolute path to the dashboard script
    script_dir = Path(__file__).parent.parent
    dashboard_script = script_dir / 'src' / 'analysis' / 'comparison_dashboard.py'

    if not dashboard_script.exists():
        print(f"\n❌ Dashboard script not found: {dashboard_script}")
        sys.exit(1)

    # Build Streamlit command
    streamlit_cmd = [
        'streamlit', 'run',
        str(dashboard_script),
        '--server.port', str(args.port),
        '--server.address', args.host,
    ]

    # Add browser option
    if not args.browser:
        streamlit_cmd.extend(['--server.headless', 'true'])

    # Add development mode
    if args.dev:
        streamlit_cmd.append('--')
        streamlit_cmd.append(args.db)

    # Set environment variable for database path
    env = os.environ.copy()
    env['BRAIN_IN_JAR_DB'] = args.db

    # Print startup information
    print("\n" + "=" * 60)
    print("🚀 Starting Dashboard Server")
    print("=" * 60)
    print(f"  Database:  {args.db}")
    print(f"  Host:      {args.host}")
    print(f"  Port:      {args.port}")
    print(f"  Theme:     {args.theme}")
    print(f"  URL:       http://{args.host}:{args.port}")
    print("=" * 60)
    print("\n📊 Dashboard Features:")
    print("  • Multi-experiment comparison")
    print("  • Interactive time-series plots")
    print("  • Statistical significance testing")
    print("  • Export reports (CSV, JSON, Markdown)")
    print("  • Filter by mode, status, date range")
    print("\n💡 Tips:")
    print("  • Use the sidebar to select experiments")
    print("  • Hover over plots for detailed information")
    print("  • Click and drag to zoom into specific regions")
    print("  • Double-click plots to reset zoom")
    print("\n⏹️  Press Ctrl+C to stop the dashboard")
    print("=" * 60 + "\n")

    # Launch Streamlit
    try:
        # Pass database path as argument
        final_cmd = streamlit_cmd + ['--', args.db]

        subprocess.run(final_cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Streamlit not found. Install it with: pip install streamlit")
        sys.exit(1)


if __name__ == '__main__':
    main()
