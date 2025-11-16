#!/usr/bin/env python3
"""
Analyze Parameter Sweep Results

Convenient CLI for sweep analysis and visualization.

Usage:
    python scripts/analyze_sweep.py <sweep_id>
    python scripts/analyze_sweep.py <sweep_id> --output report.txt
    python scripts/analyze_sweep.py <sweep_id> --plot --viz-script
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infra.sweep_analysis import SweepAnalyzer, create_visualization_script


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze parameter sweep results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Show analysis report:
  python scripts/analyze_sweep.py sweep_unstable_memory_20251116_143022

  # Save report to file:
  python scripts/analyze_sweep.py sweep_unstable_memory_20251116_143022 --output report.txt

  # Export plot data:
  python scripts/analyze_sweep.py sweep_unstable_memory_20251116_143022 --plot

  # Generate visualization script:
  python scripts/analyze_sweep.py sweep_unstable_memory_20251116_143022 --viz-script

  # Full analysis pipeline:
  python scripts/analyze_sweep.py sweep_unstable_memory_20251116_143022 --plot --viz-script --output report.txt
        """
    )

    parser.add_argument(
        'sweep_id',
        help='Sweep ID to analyze'
    )

    parser.add_argument(
        '--sweep-dir',
        default='logs/sweeps',
        help='Sweep directory (default: logs/sweeps)'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output path for report (default: print to stdout)'
    )

    parser.add_argument(
        '--plot',
        action='store_true',
        help='Export plot data to JSON'
    )

    parser.add_argument(
        '--viz-script',
        action='store_true',
        help='Generate matplotlib visualization script'
    )

    parser.add_argument(
        '--compare-param',
        help='Parameter to compare in detail'
    )

    parser.add_argument(
        '--metric',
        default='crash_rate',
        help='Metric to analyze (default: crash_rate)'
    )

    args = parser.parse_args()

    try:
        # Create analyzer
        print(f"Loading sweep: {args.sweep_id}")
        analyzer = SweepAnalyzer(args.sweep_id, args.sweep_dir)

        # Generate report
        print("Generating analysis report...")
        report = analyzer.generate_summary_report()

        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")
        else:
            print("\n" + report)

        # Export plot data if requested
        if args.plot:
            plot_path = analyzer.sweep_path / "plot_data.json"
            analyzer.export_for_plotting(str(plot_path))
            print(f"\nPlot data exported to: {plot_path}")

        # Generate visualization script if requested
        if args.viz_script:
            create_visualization_script(args.sweep_id)
            print(f"\nVisualization script created!")
            print(f"Run: python scripts/plot_{args.sweep_id}.py")

        # Detailed parameter comparison if requested
        if args.compare_param:
            print("\n" + "="*80)
            print(f"DETAILED COMPARISON: {args.compare_param}")
            print("="*80)

            stats = analyzer.compute_parameter_statistics(args.compare_param, args.metric)

            for param_value in sorted(stats.keys()):
                s = stats[param_value]
                print(f"\n{args.compare_param} = {param_value}:")
                print(f"  {args.metric} mean: {s['mean']:.4f} ± {s['std']:.4f}")
                print(f"  range: [{s['min']:.4f}, {s['max']:.4f}]")
                print(f"  median: {s['median']:.4f}")
                print(f"  samples: {s['count']}")

            # Detect thresholds
            thresholds = analyzer.detect_threshold_effects(args.compare_param, args.metric)
            if thresholds:
                print(f"\nThreshold effects detected:")
                for before, after, change in thresholds:
                    print(f"  {before} -> {after}: {change:.1%} change")
            else:
                print(f"\nNo significant threshold effects detected.")

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print(f"\nAvailable sweeps in {args.sweep_dir}:")
        sweep_dir = Path(args.sweep_dir)
        if sweep_dir.exists():
            sweeps = [d.name for d in sweep_dir.iterdir() if d.is_dir()]
            for sweep in sorted(sweeps):
                print(f"  - {sweep}")
        return 1

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
