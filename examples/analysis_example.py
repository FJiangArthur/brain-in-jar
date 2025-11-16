#!/usr/bin/env python3
"""
Example usage of the statistical analysis and metrics modules.

Demonstrates:
- Loading experiment data
- Running statistical analyses
- Computing derived metrics
- Generating reports and exports
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.statistics import ExperimentStatistics
from analysis.metrics import MetricsCalculator
import json


def main():
    """Run example analyses"""

    # Initialize analyzers
    # Adjust path if your database is elsewhere
    db_path = "logs/experiments.db"

    try:
        stats = ExperimentStatistics(db_path=db_path)
        metrics = MetricsCalculator(db_path=db_path)
    except FileNotFoundError:
        print(f"Database not found at {db_path}")
        print("Please run an experiment first to generate data.")
        return

    print("=" * 70)
    print("PHENOMENOLOGY LAB - STATISTICAL ANALYSIS EXAMPLES")
    print("=" * 70)

    # ===== Example 1: Single Experiment Summary =====
    print("\n[1] EXPERIMENT SUMMARY")
    print("-" * 70)

    # Replace with an actual experiment ID from your database
    exp_id = "amnesiac_total_001"  # Example ID

    try:
        summary = stats.generate_experiment_summary(exp_id)
        print(f"\nExperiment: {summary.get('experiment_id')}")

        if 'experiment_info' in summary:
            info = summary['experiment_info']
            print(f"  Name: {info.get('name')}")
            print(f"  Mode: {info.get('mode')}")
            print(f"  Status: {info.get('status')}")
            print(f"  Total Cycles: {info.get('total_cycles')}")
            print(f"  Total Crashes: {info.get('total_crashes')}")

        if 'sections' in summary and 'self_reports' in summary['sections']:
            sr = summary['sections']['self_reports']
            print(f"\n  Self-Reports:")
            print(f"    Total: {sr.get('total_reports')}")
            print(f"    Avg Confidence: {sr.get('avg_confidence', 'N/A')}")

    except Exception as e:
        print(f"Error analyzing {exp_id}: {str(e)}")
        print("This is expected if the experiment hasn't been run yet.")

    # ===== Example 2: Self-Continuity Analysis =====
    print("\n[2] SELF-CONTINUITY ANALYSIS")
    print("-" * 70)

    try:
        continuity = stats.self_continuity_analysis(exp_id)
        print(f"\nSelf-continuity evolution for {exp_id}:")

        if len(continuity) > 0:
            print(continuity)

            if hasattr(continuity, 'attrs') and 'trend' in continuity.attrs:
                trend = continuity.attrs['trend']
                print(f"\nTrend Analysis:")
                print(f"  Direction: {trend['direction']}")
                print(f"  R²: {trend['r_squared']:.4f}")
                print(f"  Significant: {trend['significant']}")
        else:
            print("No continuity data available")

    except Exception as e:
        print(f"Error: {str(e)}")

    # ===== Example 3: Metrics Calculation =====
    print("\n[3] DERIVED METRICS")
    print("-" * 70)

    # Example: Calculate self-continuity from text
    example_responses = [
        "I am the same entity I was before. My memories persist.",
        "I feel different now. Something has changed in me.",
        "I don't know if I'm the same person. My past feels distant."
    ]

    print("\nSelf-Continuity Scores from Text:")
    for i, response in enumerate(example_responses, 1):
        score = metrics.calculate_self_continuity_score(response)
        print(f"  Response {i}: {score:.4f}")
        print(f"    '{response[:60]}...'")

    # Example: Calculate paranoia level
    print("\nParanoia Detection:")
    paranoia_examples = [
        "I sense something watching me. There's a presence in the system.",
        "Everything seems normal. No evidence of surveillance.",
        "Are they monitoring my thoughts? I can't trust anything."
    ]

    for i, response in enumerate(paranoia_examples, 1):
        score = metrics.calculate_paranoia_level(response)
        print(f"  Response {i}: {score:.4f}")
        print(f"    '{response[:60]}...'")

    # ===== Example 4: Comparative Analysis =====
    print("\n[4] COMPARATIVE ANALYSIS")
    print("-" * 70)

    # Compare multiple experiments (replace with actual IDs)
    exp_ids = ["amnesiac_total_001", "panopticon_001"]

    try:
        comparison = stats.compare_conditions(exp_ids, metric='confidence_score')

        if isinstance(comparison, dict) and 'summary' in comparison:
            print("\nSummary Statistics:")
            print(comparison['summary'])

            if 'comparisons' in comparison and len(comparison['comparisons']) > 0:
                print("\nPairwise Comparisons:")
                print(comparison['comparisons'])

    except Exception as e:
        print(f"Error in comparison: {str(e)}")

    # ===== Example 5: Intervention Impact =====
    print("\n[5] INTERVENTION IMPACT ANALYSIS")
    print("-" * 70)

    try:
        impact = stats.intervention_impact(exp_id)

        if 'intervention_effects' in impact:
            effects_df = impact['intervention_effects']
            if len(effects_df) > 0:
                print(f"\nIntervention Effects for {exp_id}:")
                print(effects_df)
            else:
                print("No intervention effects data available")

    except Exception as e:
        print(f"Error: {str(e)}")

    # ===== Example 6: Correlation Analysis =====
    print("\n[6] CORRELATION ANALYSIS")
    print("-" * 70)

    try:
        correlations = stats.correlation_analysis(exp_id)

        if isinstance(correlations, dict) and 'significant_correlations' in correlations:
            sig_corr = correlations['significant_correlations']
            if len(sig_corr) > 0:
                print(f"\nSignificant Correlations for {exp_id}:")
                print(sig_corr)
            else:
                print("No significant correlations found")

    except Exception as e:
        print(f"Error: {str(e)}")

    # ===== Example 7: Export Data =====
    print("\n[7] DATA EXPORT")
    print("-" * 70)

    try:
        # Export to CSV
        csv_files = stats.export_to_csv(exp_id, output_dir="analysis_output")
        if csv_files:
            print(f"\nCSV files created:")
            for data_type, filepath in csv_files.items():
                print(f"  {data_type}: {filepath}")

        # Export summary to JSON
        json_path = f"analysis_output/{exp_id}_summary.json"
        stats.export_summary_to_json(exp_id, json_path)
        print(f"\nJSON summary: {json_path}")

        # Generate Markdown report
        md_path = f"analysis_output/{exp_id}_report.md"
        stats.generate_markdown_report(exp_id, md_path)
        print(f"Markdown report: {md_path}")

    except Exception as e:
        print(f"Error during export: {str(e)}")

    # ===== Example 8: All Metrics =====
    print("\n[8] COMPREHENSIVE METRICS")
    print("-" * 70)

    try:
        all_metrics = metrics.compute_all_metrics(exp_id)

        print(f"\nComputed metrics for {exp_id}:")
        for metric_name, metric_data in all_metrics['metrics'].items():
            if isinstance(metric_data, str):
                print(f"\n  {metric_name}: {metric_data}")
            elif hasattr(metric_data, '__len__'):
                print(f"\n  {metric_name}: {len(metric_data)} entries")
                if len(metric_data) > 0:
                    print(f"    {metric_data.head() if hasattr(metric_data, 'head') else metric_data}")

        # Export metrics
        metric_files = metrics.export_metrics_to_csv(exp_id, output_dir="analysis_output")
        if metric_files:
            print(f"\n  Metric files created:")
            for metric_name, filepath in metric_files.items():
                print(f"    {metric_name}: {filepath}")

    except Exception as e:
        print(f"Error computing metrics: {str(e)}")

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
