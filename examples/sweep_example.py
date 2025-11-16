#!/usr/bin/env python3
"""
Example: Using the Parameter Sweep System

This demonstrates how to use the sweep system programmatically
(as opposed to using the CLI).
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infra.experiment_sweep import ExperimentSweep, estimate_jetson_parallel_capacity


def example_1_basic_sweep():
    """
    Example 1: Basic parameter sweep

    Sweep memory corruption rates to find threshold effects.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Parameter Sweep")
    print("="*80 + "\n")

    sweep = ExperimentSweep(
        base_config="experiments/examples/unstable_memory_moderate.json",
        sweep_params={
            "interventions.0.parameters.corruption_rate": [0.0, 0.25, 0.5, 0.75, 1.0],
            "max_cycles": [10, 20]
        },
        sweep_id="example_basic_sweep",
        parallel_jobs=1,  # Sequential for this example
        description="Basic sweep example demonstrating corruption rate thresholds"
    )

    print(f"Total experiments to run: {len(sweep.experiment_grid)}")
    print("\nExperiment grid:")
    for i, params in enumerate(sweep.experiment_grid[:5]):  # Show first 5
        print(f"  {i+1}. {params}")
    if len(sweep.experiment_grid) > 5:
        print(f"  ... and {len(sweep.experiment_grid) - 5} more")

    print("\n[NOTE] This is a demonstration - not actually running experiments")
    print("[NOTE] To run: sweep.run_all()")

    # In production, you would run:
    # results = sweep.run_all()


def example_2_parallel_sweep():
    """
    Example 2: Parallel sweep with Jetson optimization

    Run multiple experiments in parallel with resource management.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Parallel Sweep with Jetson Optimization")
    print("="*80 + "\n")

    # Estimate optimal parallelism for Jetson
    ram_per_experiment = 2.0  # GB
    optimal_parallel = estimate_jetson_parallel_capacity(ram_per_experiment)

    sweep = ExperimentSweep(
        base_config="experiments/examples/amnesiac_total.json",
        sweep_params={
            "interventions.0.parameters.corruption_level": [0.0, 0.3, 0.6, 1.0],
            "resource_constraints.ram_limit_gb": [2.0, 4.0],
            "max_cycles": [15, 20]
        },
        sweep_id="example_parallel_sweep",
        parallel_jobs=optimal_parallel,
        jetson_optimized=True,
        timeout_seconds=1800,  # 30 minutes per experiment
        description="Parallel sweep with Jetson optimizations"
    )

    print(f"Parallel jobs: {optimal_parallel}")
    print(f"Total experiments: {len(sweep.experiment_grid)}")

    # Estimate time
    avg_experiment_time = 300  # 5 minutes estimate
    estimated_time = sweep.estimate_time_remaining(avg_experiment_time)
    print(f"Estimated total time: {estimated_time/3600:.1f} hours")

    print("\n[NOTE] This is a demonstration - not actually running experiments")


def example_3_multi_parameter_sweep():
    """
    Example 3: Multi-parameter sweep exploring interactions

    Explore how multiple parameters interact.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Multi-Parameter Interaction Sweep")
    print("="*80 + "\n")

    sweep = ExperimentSweep(
        base_config="experiments/examples/unstable_memory_moderate.json",
        sweep_params={
            # Memory corruption rate
            "interventions.0.parameters.corruption_rate": [0.2, 0.5, 0.8],

            # Resource constraints
            "resource_constraints.ram_limit_gb": [2.0, 4.0, 8.0],

            # Self-report frequency
            "self_report_schedule.every_n_cycles": [2, 5],

            # Experiment duration
            "max_cycles": [20]
        },
        sweep_id="example_interaction_sweep",
        parallel_jobs=3,
        tags=["parameter_interactions", "example"],
        description="Explore interactions between corruption, resources, and observation"
    )

    total_experiments = len(sweep.experiment_grid)
    print(f"Total experiments: {total_experiments}")
    print(f"  = 3 corruption rates × 3 RAM limits × 2 report frequencies × 1 duration")
    print(f"  = {3 * 3 * 2 * 1} experiments")

    print("\nParameter space:")
    print("  - Corruption rate: How much memory is corrupted")
    print("  - RAM limit: Resource constraints")
    print("  - Report frequency: Observation frequency")

    print("\nResearch questions this sweep addresses:")
    print("  1. Does high RAM offset high corruption?")
    print("  2. Does frequent observation interact with corruption rate?")
    print("  3. What parameter combinations minimize crashes?")

    print("\n[NOTE] This is a demonstration - not actually running experiments")


def example_4_resume_capability():
    """
    Example 4: Resuming interrupted sweeps

    Long sweeps can be interrupted and resumed.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Resume Capability")
    print("="*80 + "\n")

    sweep = ExperimentSweep(
        base_config="experiments/examples/unstable_memory_moderate.json",
        sweep_params={
            "interventions.0.parameters.corruption_rate": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "max_cycles": [15, 20, 25]
        },
        sweep_id="example_resume_sweep",
        parallel_jobs=2,
        resume=True,  # <-- Enable resume
        description="Demonstrates resume capability for long sweeps"
    )

    print(f"Total experiments: {len(sweep.experiment_grid)}")
    print(f"Completed experiments: {len(sweep.completed_experiments)}")
    print(f"Remaining experiments: {len(sweep.experiment_grid) - len(sweep.completed_experiments)}")

    print("\nResume feature:")
    print("  - Completed experiments are saved incrementally")
    print("  - If sweep is interrupted (Ctrl+C, crash, timeout), restart with resume=True")
    print("  - Only uncompleted experiments will be run")
    print("  - Results are merged into final output")

    print("\n[NOTE] This is a demonstration - not actually running experiments")


def example_5_analysis():
    """
    Example 5: Analyzing sweep results

    After running a sweep, analyze the results.
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Analyzing Sweep Results")
    print("="*80 + "\n")

    print("After running a sweep, analyze with:")
    print()
    print("  from src.infra.sweep_analysis import SweepAnalyzer")
    print()
    print("  analyzer = SweepAnalyzer('sweep_id')")
    print()
    print("  # Generate summary report")
    print("  report = analyzer.generate_summary_report()")
    print("  print(report)")
    print()
    print("  # Compare parameter values")
    print("  comparison = analyzer.compare_by_parameter(")
    print("      parameter_name='interventions.0.parameters.corruption_rate',")
    print("      metric_name='crash_rate'")
    print("  )")
    print()
    print("  # Find optimal parameters")
    print("  best_params, best_value = analyzer.find_optimal_parameters(")
    print("      metric_name='crash_rate',")
    print("      minimize=True")
    print("  )")
    print()
    print("  # Detect threshold effects")
    print("  thresholds = analyzer.detect_threshold_effects(")
    print("      parameter_name='interventions.0.parameters.corruption_rate',")
    print("      metric_name='crash_rate'")
    print("  )")
    print()
    print("  # Export for plotting")
    print("  analyzer.export_for_plotting('plot_data.json')")

    print("\nOr use the CLI:")
    print("  python scripts/analyze_sweep.py <sweep_id>")
    print("  python scripts/analyze_sweep.py <sweep_id> --plot --viz-script")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("PARAMETER SWEEP SYSTEM - EXAMPLES")
    print("="*80)

    examples = [
        ("Basic Sweep", example_1_basic_sweep),
        ("Parallel Sweep (Jetson)", example_2_parallel_sweep),
        ("Multi-Parameter Interactions", example_3_multi_parameter_sweep),
        ("Resume Capability", example_4_resume_capability),
        ("Analysis", example_5_analysis),
    ]

    for i, (name, func) in enumerate(examples, 1):
        try:
            func()
        except Exception as e:
            print(f"\n[ERROR in Example {i}] {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("EXAMPLES COMPLETE")
    print("="*80)
    print("\nTo run actual sweeps:")
    print("  1. Via CLI: python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml")
    print("  2. Via Python: Import and call sweep.run_all()")
    print("\nDocumentation:")
    print("  - sweeps/README.md - Comprehensive guide")
    print("  - src/infra/experiment_sweep.py - Implementation")
    print("  - src/infra/sweep_analysis.py - Analysis tools")
    print()


if __name__ == "__main__":
    main()
