#!/usr/bin/env python3
"""
Example: Run Experiment with Live Web Monitoring

This script demonstrates how to run an experiment with real-time
WebSocket-based monitoring visible in a web browser.

Usage:
    python examples/run_with_live_monitoring.py --config experiments/examples/amnesiac_total.json
"""

import sys
import argparse
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.schema import ExperimentConfig
from src.runner.experiment_runner import ExperimentRunner
from src.web.web_monitor import start_web_server_background


def main():
    parser = argparse.ArgumentParser(
        description="Run experiment with live web monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python examples/run_with_live_monitoring.py --config experiments/examples/amnesiac_total.json
  python examples/run_with_live_monitoring.py --config experiments/examples/unstable_memory_moderate.json --port 8080

After starting:
  1. Open browser to http://<jetson-ip>:5000
  2. Login with password
  3. Navigate to /experiment/live?id=<experiment_id>
  4. Watch real-time updates as experiment runs
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to experiment configuration JSON file'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web server port (default: 5000)'
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web server host (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--db',
        default='logs/experiments.db',
        help='Path to experiment database (default: logs/experiments.db)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🧠 BRAIN IN A JAR - Live Monitoring Mode")
    print("=" * 80)
    print()

    # Start web server in background
    print(f"[1/3] Starting web server on {args.host}:{args.port}...")
    web_server, monitor = start_web_server_background(host=args.host, port=args.port)
    print(f"      ✓ Web server started")
    print()

    # Print access instructions
    print("=" * 80)
    print("📺 LIVE MONITORING ACCESS")
    print("=" * 80)
    print(f"  URL:      http://{args.host}:{args.port}")
    print(f"  Login:    Use default password (admin123) or configured password")
    print()
    print(f"  After login, navigate to:")
    print(f"  /experiment/live?id=<experiment_id>")
    print()
    print("  Or use the experiments dashboard at:")
    print(f"  /experiments")
    print("=" * 80)
    print()

    # Load experiment config
    print(f"[2/3] Loading experiment configuration...")
    try:
        config = ExperimentConfig.from_json(args.config)
        print(f"      ✓ Loaded: {config.name}")
        print(f"      ✓ Mode: {config.mode}")
        print(f"      ✓ ID: {config.experiment_id}")
        print()
    except Exception as e:
        print(f"      ✗ Error loading config: {e}")
        return 1

    # Print monitoring URL
    print("=" * 80)
    print("🔗 DIRECT MONITORING LINK")
    print("=" * 80)
    print(f"  http://{args.host}:{args.port}/experiment/live?id={config.experiment_id}")
    print("=" * 80)
    print()

    # Wait a moment for server to fully start
    time.sleep(2)

    # Create and start experiment runner
    print(f"[3/3] Starting experiment with live monitoring...")
    print()

    try:
        runner = ExperimentRunner(
            config,
            db_path=args.db,
            web_monitor=monitor  # Enable live monitoring
        )

        print("🚀 Experiment starting - events will stream to connected browsers")
        print()

        # Start experiment (will emit real-time events)
        runner.start()

        print()
        print("=" * 80)
        print("✓ Experiment completed successfully")
        print("=" * 80)

    except KeyboardInterrupt:
        print()
        print("⚠ Experiment interrupted by user")
        print()
    except Exception as e:
        print()
        print(f"✗ Experiment error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
