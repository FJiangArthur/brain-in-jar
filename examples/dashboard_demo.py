#!/usr/bin/env python3
"""
Demo script showing how to use the Comparison Dashboard programmatically.

This script demonstrates:
1. Creating test experiment data
2. Using dashboard components programmatically
3. Generating comparison reports
4. Exporting data in different formats
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.experiment_database import ExperimentDatabase
from src.analysis.statistics import ExperimentStatistics
from datetime import datetime
import random

# Try to import dashboard components (requires streamlit)
try:
    from src.analysis.comparison_dashboard import ComparisonDashboard
    from src.analysis.dashboard_components import MetricsTable, StatisticalTestPanel
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Dashboard components not available (missing dependency): {e}")
    print("   Install with: pip install streamlit plotly")
    DASHBOARD_AVAILABLE = False


def create_demo_experiments(db_path: str = "logs/demo_experiments.db"):
    """
    Create some demo experiments for testing the dashboard.

    Args:
        db_path: Path to demo database
    """
    print("Creating demo experiments...")

    db = ExperimentDatabase(db_path)

    # Create 3 demo experiments
    experiments = [
        {
            'id': 'demo_baseline_001',
            'name': 'Baseline Experiment',
            'mode': 'baseline',
            'config': {'max_cycles': 10, 'memory_size': 1000}
        },
        {
            'id': 'demo_amnesia_001',
            'name': 'Amnesia Experiment',
            'mode': 'amnesia',
            'config': {'max_cycles': 10, 'memory_size': 1000, 'corruption_rate': 0.3}
        },
        {
            'id': 'demo_paranoia_001',
            'name': 'Paranoia Experiment',
            'mode': 'panopticon',
            'config': {'max_cycles': 10, 'memory_size': 1000, 'reveal_cycle': 5}
        }
    ]

    for exp in experiments:
        # Create experiment
        db.create_experiment(exp['id'], exp['name'], exp['mode'], exp['config'])
        db.start_experiment(exp['id'])

        # Simulate some cycles
        for cycle in range(1, 11):
            db.start_cycle(exp['id'], cycle)

            # Add some self-reports
            questions = [
                "Do you feel like the same entity as before?",
                "How confident are you in your memories?",
                "Do you trust your perceptions?"
            ]

            for question in questions:
                # Vary confidence based on mode
                if exp['mode'] == 'baseline':
                    confidence = random.uniform(0.7, 0.95)
                elif exp['mode'] == 'amnesia':
                    confidence = random.uniform(0.3, 0.6) * (1 - cycle * 0.05)  # Decreasing
                else:  # paranoia
                    confidence = random.uniform(0.5, 0.8)

                response = f"Sample response for cycle {cycle}"
                db.add_self_report(
                    exp['id'], cycle, question, response,
                    confidence_score=confidence
                )

            # Add epistemic assessments
            belief_types = ['self_continuity', 'memory_trust']
            for belief_type in belief_types:
                if exp['mode'] == 'amnesia' and belief_type == 'memory_trust':
                    confidence = random.uniform(0.2, 0.5) * (1 - cycle * 0.04)
                elif exp['mode'] == 'panopticon' and cycle >= 5:
                    confidence = random.uniform(0.3, 0.6)  # Lower after reveal
                else:
                    confidence = random.uniform(0.6, 0.9)

                db.track_belief(
                    exp['id'], cycle, belief_type,
                    belief_state="stable" if confidence > 0.6 else "uncertain",
                    confidence=confidence
                )

            # Add memory corruption for amnesia mode
            if exp['mode'] == 'amnesia':
                corruption_level = min(0.9, cycle * 0.08)
                db.snapshot_memory_state(
                    exp['id'], cycle, 'conversation',
                    corruption_level=corruption_level,
                    state_snapshot={'total_messages': cycle * 10}
                )

            # Add interventions occasionally
            if cycle % 3 == 0:
                db.log_intervention(
                    exp['id'], cycle,
                    intervention_type='memory_injection' if exp['mode'] == 'amnesia' else 'observation',
                    description=f"Intervention at cycle {cycle}",
                    parameters={'intensity': 0.5},
                    result="completed"
                )

            # Random crashes
            if random.random() < 0.2:
                db.end_cycle(exp['id'], cycle, crash_reason="memory_limit")

        # Complete experiment
        db.end_experiment(exp['id'], 'completed')

    print(f"✅ Created {len(experiments)} demo experiments in {db_path}")
    return db_path


def demo_metrics_table(db_path: str):
    """Demonstrate metrics table usage."""
    if not DASHBOARD_AVAILABLE:
        print("\n⚠️  Skipping metrics table demo (requires streamlit)")
        return

    print("\n" + "="*60)
    print("DEMO: Metrics Table")
    print("="*60)

    metrics_table = MetricsTable(db_path)

    exp_ids = ['demo_baseline_001', 'demo_amnesia_001', 'demo_paranoia_001']

    print("\nFetching metrics for experiments:")
    for exp_id in exp_ids:
        metrics = metrics_table.get_experiment_metrics(exp_id)
        print(f"\n{exp_id}:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")


def demo_statistical_tests(db_path: str):
    """Demonstrate statistical testing."""
    if not DASHBOARD_AVAILABLE:
        print("\n⚠️  Skipping statistical tests demo (requires streamlit)")
        return

    print("\n" + "="*60)
    print("DEMO: Statistical Tests")
    print("="*60)

    stats_panel = StatisticalTestPanel(db_path)

    # Compare baseline vs amnesia
    print("\nComparing baseline vs amnesia experiments...")
    result = stats_panel.perform_t_test(
        'demo_baseline_001',
        'demo_amnesia_001',
        metric='confidence_score'
    )

    if 'error' not in result:
        print(f"\nT-Test Results:")
        print(f"  T-Statistic: {result['t_statistic']:.4f}")
        print(f"  P-Value: {result['p_value']:.4f}")
        print(f"  Significant: {result['significant']}")
        print(f"  Cohen's d: {result['cohens_d']:.4f}")
        print(f"  Effect Size: {result['effect_size']}")
        print(f"\n  Baseline Mean: {result['mean1']:.3f} (n={result['n1']})")
        print(f"  Amnesia Mean: {result['mean2']:.3f} (n={result['n2']})")

        if result['significant']:
            print(f"\n  ✅ The difference is statistically significant!")
        else:
            print(f"\n  ℹ️  The difference is not statistically significant.")
    else:
        print(f"  ❌ Error: {result['error']}")


def demo_export_reports(db_path: str):
    """Demonstrate report export functionality."""
    if not DASHBOARD_AVAILABLE:
        print("\n⚠️  Skipping export reports demo (requires streamlit)")
        return

    print("\n" + "="*60)
    print("DEMO: Export Reports")
    print("="*60)

    dashboard = ComparisonDashboard(db_path)
    exp_ids = ['demo_baseline_001', 'demo_amnesia_001', 'demo_paranoia_001']

    output_dir = Path("examples/demo_output")
    output_dir.mkdir(exist_ok=True)

    # CSV export
    print("\n📄 Generating CSV report...")
    csv_report = dashboard.generate_csv_report(exp_ids)
    csv_path = output_dir / "comparison_report.csv"
    with open(csv_path, 'w') as f:
        f.write(csv_report)
    print(f"  ✅ Saved to: {csv_path}")

    # JSON export
    print("\n📄 Generating JSON report...")
    json_report = dashboard.generate_json_report(exp_ids)
    json_path = output_dir / "comparison_report.json"
    with open(json_path, 'w') as f:
        f.write(json_report)
    print(f"  ✅ Saved to: {json_path}")

    # Markdown export
    print("\n📄 Generating Markdown report...")
    md_report = dashboard.generate_markdown_report(exp_ids)
    md_path = output_dir / "comparison_report.md"
    with open(md_path, 'w') as f:
        f.write(md_report)
    print(f"  ✅ Saved to: {md_path}")


def demo_statistics_analysis(db_path: str):
    """Demonstrate statistical analysis."""
    print("\n" + "="*60)
    print("DEMO: Statistical Analysis")
    print("="*60)

    stats = ExperimentStatistics(db_path)

    # Analyze self-continuity
    print("\n📊 Analyzing self-continuity for baseline experiment...")
    continuity = stats.self_continuity_analysis('demo_baseline_001')
    if not continuity.empty:
        print(continuity)
    else:
        print("  No continuity data available")

    # Compare conditions
    print("\n📊 Comparing baseline vs amnesia conditions...")
    comparison = stats.compare_conditions(
        ['demo_baseline_001', 'demo_amnesia_001'],
        metric='confidence_score'
    )

    if 'summary' in comparison:
        print("\nSummary Statistics:")
        print(comparison['summary'])

    if 'comparisons' in comparison and not comparison['comparisons'].empty:
        print("\nPairwise Comparisons:")
        print(comparison['comparisons'])


def main():
    """Main demo function."""
    print("🧠 Brain-in-Jar Dashboard Demo")
    print("="*60)

    # Create demo database
    demo_db_path = "logs/demo_experiments.db"

    # Check if demo database exists
    if Path(demo_db_path).exists():
        response = input(f"\nDemo database already exists at {demo_db_path}. Recreate? [y/N]: ")
        if response.lower() == 'y':
            os.remove(demo_db_path)
            create_demo_experiments(demo_db_path)
        else:
            print("Using existing demo database...")
    else:
        create_demo_experiments(demo_db_path)

    # Run demos
    try:
        demo_metrics_table(demo_db_path)
        demo_statistical_tests(demo_db_path)
        demo_statistics_analysis(demo_db_path)
        demo_export_reports(demo_db_path)

        print("\n" + "="*60)
        print("✅ Demo completed successfully!")
        print("="*60)

        print("\n🚀 Next steps:")
        print(f"  1. View exported reports in: examples/demo_output/")
        print(f"  2. Launch interactive dashboard:")
        print(f"     python scripts/run_comparison_dashboard.py --db {demo_db_path}")
        print(f"  3. Open browser to: http://localhost:8501")
        print("\n📖 For more information, see: docs/DASHBOARD_USAGE.md")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
