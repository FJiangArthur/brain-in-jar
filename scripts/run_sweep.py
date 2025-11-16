#!/usr/bin/env python3
"""
CLI for Running Parameter Sweeps

Usage:
    python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml
    python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --parallel 4
    python scripts/run_sweep.py --base experiments/examples/amnesiac_total.json \
        --param "interventions.0.parameters.corruption_level" 0.0 0.25 0.5 0.75 1.0 \
        --param "max_cycles" 10 20 50
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infra.experiment_sweep import ExperimentSweep, estimate_jetson_parallel_capacity


def load_sweep_config_from_yaml(yaml_path: str) -> Dict[str, Any]:
    """
    Load sweep configuration from YAML file

    Args:
        yaml_path: Path to YAML config file

    Returns:
        Dictionary of sweep configuration parameters
    """
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    # Extract sweep parameters
    sweep_params = {}
    if 'sweep' in config:
        for param_name, param_values in config['sweep'].items():
            if not isinstance(param_values, list):
                param_values = [param_values]
            sweep_params[param_name] = param_values

    return {
        'base_config': config.get('base_config'),
        'sweep_params': sweep_params,
        'sweep_id': config.get('sweep_id'),
        'parallel_jobs': config.get('parallel', 1),
        'output_dir': config.get('output_dir', 'logs/sweeps'),
        'db_path': config.get('db_path', 'logs/experiments.db'),
        'resume': config.get('resume', False),
        'jetson_optimized': config.get('jetson_optimized', False),
        'timeout_seconds': config.get('timeout'),
        'max_retries': config.get('max_retries', 2),
        'tags': config.get('tags', []),
        'description': config.get('description', '')
    }


def parse_cli_sweep_params(params_list: List[str]) -> Dict[str, List[Any]]:
    """
    Parse sweep parameters from CLI arguments

    Format: --param "parameter.path" value1 value2 value3

    Args:
        params_list: List of parameter specifications from CLI

    Returns:
        Dictionary of parameter_name -> [values]
    """
    sweep_params = {}

    i = 0
    while i < len(params_list):
        if params_list[i] == '--param':
            param_name = params_list[i + 1]
            values = []

            # Collect values until next --param or end
            i += 2
            while i < len(params_list) and params_list[i] != '--param':
                # Try to parse as number, otherwise keep as string
                try:
                    value = float(params_list[i])
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    value = params_list[i]
                values.append(value)
                i += 1

            sweep_params[param_name] = values
        else:
            i += 1

    return sweep_params


def estimate_sweep_duration(num_experiments: int, parallel_jobs: int, avg_experiment_time: int = 300) -> str:
    """
    Estimate total sweep duration

    Args:
        num_experiments: Total number of experiments
        parallel_jobs: Number of parallel jobs
        avg_experiment_time: Average time per experiment (seconds)

    Returns:
        Human-readable duration estimate
    """
    total_seconds = (num_experiments / parallel_jobs) * avg_experiment_time

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    if hours > 0:
        return f"~{hours}h {minutes}m"
    else:
        return f"~{minutes}m"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Run automated parameter sweeps for phenomenology experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Run sweep from YAML config:
  python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml

  # Run with custom parallelism:
  python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --parallel 4

  # Define sweep directly via CLI:
  python scripts/run_sweep.py \\
    --base experiments/examples/amnesiac_total.json \\
    --param "interventions.0.parameters.corruption_level" 0.0 0.25 0.5 0.75 1.0 \\
    --param "max_cycles" 10 20 50 \\
    --parallel 3

  # Resume interrupted sweep:
  python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --resume

  # Jetson Orin optimization:
  python scripts/run_sweep.py --config sweeps/sweep.yaml --jetson --parallel auto
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        help='Path to YAML sweep configuration file'
    )

    parser.add_argument(
        '--base',
        type=str,
        help='Path to base experiment config JSON (for CLI-based sweeps)'
    )

    parser.add_argument(
        '--param',
        action='append',
        nargs='+',
        help='Parameter to sweep: --param "param.path" val1 val2 val3 (can be repeated)'
    )

    parser.add_argument(
        '--parallel',
        type=str,
        default='1',
        help='Number of parallel jobs (use "auto" for Jetson auto-detection)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='logs/sweeps',
        help='Output directory for sweep results (default: logs/sweeps)'
    )

    parser.add_argument(
        '--db',
        type=str,
        default='logs/experiments.db',
        help='Path to experiment database (default: logs/experiments.db)'
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume interrupted sweep'
    )

    parser.add_argument(
        '--jetson',
        action='store_true',
        help='Enable Jetson Orin optimizations'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        help='Timeout per experiment in seconds (default: no timeout)'
    )

    parser.add_argument(
        '--sweep-id',
        type=str,
        help='Custom sweep ID (auto-generated if not specified)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be run without actually running it'
    )

    args = parser.parse_args()

    # Determine configuration source
    if args.config:
        # Load from YAML
        print(f"Loading sweep configuration from: {args.config}")
        sweep_config = load_sweep_config_from_yaml(args.config)

        # Allow CLI overrides
        if args.parallel != '1':
            sweep_config['parallel_jobs'] = args.parallel
        if args.resume:
            sweep_config['resume'] = True
        if args.jetson:
            sweep_config['jetson_optimized'] = True
        if args.timeout:
            sweep_config['timeout_seconds'] = args.timeout
        if args.output:
            sweep_config['output_dir'] = args.output
        if args.db:
            sweep_config['db_path'] = args.db

    elif args.base:
        # Build from CLI arguments
        if not args.param:
            parser.error("--base requires at least one --param specification")

        # Flatten param list
        flat_param_list = []
        for param_group in args.param:
            flat_param_list.extend(param_group)

        sweep_params = parse_cli_sweep_params(['--param'] + flat_param_list)

        sweep_config = {
            'base_config': args.base,
            'sweep_params': sweep_params,
            'sweep_id': args.sweep_id,
            'parallel_jobs': args.parallel,
            'output_dir': args.output,
            'db_path': args.db,
            'resume': args.resume,
            'jetson_optimized': args.jetson,
            'timeout_seconds': args.timeout,
            'max_retries': 2,
            'tags': ['cli_sweep'],
            'description': 'Sweep created via CLI'
        }

    else:
        parser.error("Must specify either --config or --base")

    # Handle "auto" parallel jobs
    if sweep_config['parallel_jobs'] == 'auto':
        ram_per_exp = 2.0  # Default estimate
        sweep_config['parallel_jobs'] = estimate_jetson_parallel_capacity(ram_per_exp)
        print(f"Auto-detected parallel jobs: {sweep_config['parallel_jobs']}")
    else:
        sweep_config['parallel_jobs'] = int(sweep_config['parallel_jobs'])

    # Validate base config exists
    if not Path(sweep_config['base_config']).exists():
        print(f"ERROR: Base config not found: {sweep_config['base_config']}")
        return 1

    # Create sweep
    print("\n" + "="*80)
    print("PARAMETER SWEEP CONFIGURATION")
    print("="*80)
    print(f"Base config: {sweep_config['base_config']}")
    print(f"Parameters to sweep:")
    for param, values in sweep_config['sweep_params'].items():
        print(f"  {param}: {values} ({len(values)} values)")

    total_experiments = 1
    for values in sweep_config['sweep_params'].values():
        total_experiments *= len(values)

    print(f"\nTotal experiments: {total_experiments}")
    print(f"Parallel jobs: {sweep_config['parallel_jobs']}")

    estimated_duration = estimate_sweep_duration(
        total_experiments,
        sweep_config['parallel_jobs']
    )
    print(f"Estimated duration: {estimated_duration}")

    print(f"Output directory: {sweep_config['output_dir']}")
    print(f"Database: {sweep_config['db_path']}")

    if sweep_config.get('jetson_optimized'):
        print(f"Jetson optimization: ENABLED")

    if sweep_config.get('timeout_seconds'):
        print(f"Timeout per experiment: {sweep_config['timeout_seconds']}s")

    print("="*80 + "\n")

    if args.dry_run:
        print("DRY RUN - not executing sweep")
        return 0

    # Confirm if many experiments
    if total_experiments > 20:
        response = input(f"This will run {total_experiments} experiments. Continue? [y/N] ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 0

    # Create and run sweep
    sweep = ExperimentSweep(**sweep_config)
    results = sweep.run_all(verbose=True)

    # Print summary
    print("\n" + "="*80)
    print("SWEEP RESULTS SUMMARY")
    print("="*80)

    completed = sum(1 for r in results if r.status == 'completed')
    failed = sum(1 for r in results if r.status == 'failed')
    timeout = sum(1 for r in results if r.status == 'timeout')

    print(f"Completed: {completed}/{total_experiments}")
    print(f"Failed: {failed}/{total_experiments}")
    print(f"Timeout: {timeout}/{total_experiments}")

    if completed > 0:
        avg_cycles = sum(r.total_cycles for r in results if r.status == 'completed') / completed
        avg_crashes = sum(r.total_crashes for r in results if r.status == 'completed') / completed
        print(f"\nAverage cycles per experiment: {avg_cycles:.1f}")
        print(f"Average crashes per experiment: {avg_crashes:.1f}")

    print(f"\nResults saved to: {sweep.output_dir}")
    print(f"  - sweep_results.json (all results)")
    print(f"  - sweep_config.json (sweep configuration)")
    print(f"  - *_config.json (individual experiment configs)")

    print("\nNext steps:")
    print(f"  1. Analyze results: python scripts/analyze_sweep.py {sweep.sweep_id}")
    print(f"  2. Generate plots: python scripts/analyze_sweep.py {sweep.sweep_id} --plot")
    print("="*80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
