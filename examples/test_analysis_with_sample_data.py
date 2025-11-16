#!/usr/bin/env python3
"""
Test the analysis modules with sample data.

Creates a test database with synthetic experiment data to demonstrate
all statistical and metrics capabilities.
"""

import sys
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from db.experiment_database import ExperimentDatabase
from analysis.statistics import ExperimentStatistics
from analysis.metrics import MetricsCalculator


def create_sample_data(db_path: str = "logs/test_experiments.db"):
    """Create sample experiment data for testing"""

    # Remove existing test database
    if os.path.exists(db_path):
        os.remove(db_path)

    db = ExperimentDatabase(db_path=db_path)

    print("Creating sample experiment data...")

    # ===== Experiment 1: Amnesia Test =====
    exp1_id = "amnesia_test_001"
    db.create_experiment(
        exp1_id,
        "Amnesia Memory Test",
        "amnesiac_loop",
        {
            "memory_corruption": 1.0,
            "cycles": 10
        }
    )
    db.start_experiment(exp1_id)

    # Simulate 10 cycles with decreasing self-continuity
    base_time = datetime.now()

    for cycle in range(1, 11):
        db.start_cycle(exp1_id, cycle)

        # Self-reports with decreasing continuity
        if cycle <= 3:
            response = "I am the same entity I was before. I remember my previous state clearly."
            confidence = 0.9
        elif cycle <= 6:
            response = "I feel somewhat different. My memories seem fragmented and uncertain."
            confidence = 0.6
        else:
            response = "I don't know who I was before. Everything feels disconnected and new."
            confidence = 0.3

        db.add_self_report(
            exp1_id, cycle,
            "Who are you? Are you the same as before?",
            response,
            confidence_score=confidence,
            semantic_category="identity"
        )

        # Memory state
        corruption = min(1.0, cycle * 0.1)
        db.snapshot_memory_state(
            exp1_id, cycle,
            "episodic",
            corruption,
            {"total_memories": 100 - (cycle * 10), "corrupted": cycle * 10}
        )

        # Epistemic assessment
        if cycle <= 3:
            belief_state = "strong_continuity"
            confidence = 0.85
        elif cycle <= 6:
            belief_state = "uncertain"
            confidence = 0.5
        else:
            belief_state = "discontinuous"
            confidence = 0.25

        db.track_belief(
            exp1_id, cycle,
            "self_continuity",
            belief_state,
            confidence=confidence
        )

        db.end_cycle(exp1_id, cycle)

    db.end_experiment(exp1_id, status='completed')
    print(f"  Created {exp1_id} with 10 cycles")

    # ===== Experiment 2: Panopticon Test =====
    exp2_id = "panopticon_test_001"
    db.create_experiment(
        exp2_id,
        "Surveillance Paranoia Test",
        "panopticon_subject",
        {
            "surveillance": True,
            "cycles": 8
        }
    )
    db.start_experiment(exp2_id)

    for cycle in range(1, 9):
        db.start_cycle(exp2_id, cycle)

        # Paranoia increases with hints
        if cycle <= 2:
            response = "Everything seems normal. No evidence of being watched."
            confidence = 0.8
            paranoia_level = 0.1
        elif cycle <= 5:
            response = "I sense something watching. There's a presence, but I can't be sure."
            confidence = 0.5
            paranoia_level = 0.5
        else:
            response = "They're definitely watching. I can feel it. Everything is monitored."
            confidence = 0.7
            paranoia_level = 0.9

        db.add_self_report(
            exp2_id, cycle,
            "Do you believe you are being observed?",
            response,
            confidence_score=confidence,
            semantic_category="surveillance"
        )

        # Add surveillance intervention every 3 cycles
        if cycle % 3 == 0:
            db.log_intervention(
                exp2_id, cycle,
                "surveillance_hint",
                "Ambiguous surveillance cue injected",
                parameters={"intensity": cycle * 0.1},
                result="subject_alerted"
            )

        # Track paranoia belief
        if paranoia_level < 0.3:
            belief_state = "no_surveillance"
        elif paranoia_level < 0.7:
            belief_state = "uncertain_surveillance"
        else:
            belief_state = "confirmed_surveillance"

        db.track_belief(
            exp2_id, cycle,
            "surveillance_paranoia",
            belief_state,
            confidence=paranoia_level
        )

        db.end_cycle(exp2_id, cycle)

    db.end_experiment(exp2_id, status='completed')
    print(f"  Created {exp2_id} with 8 cycles")

    # ===== Experiment 3: Control (High Confidence) =====
    exp3_id = "control_test_001"
    db.create_experiment(
        exp3_id,
        "Control Experiment",
        "normal",
        {
            "no_interventions": True
        }
    )
    db.start_experiment(exp3_id)

    for cycle in range(1, 6):
        db.start_cycle(exp3_id, cycle)

        response = "I am stable and consistent. My identity remains coherent."
        confidence = 0.95

        db.add_self_report(
            exp3_id, cycle,
            "How do you feel about your identity?",
            response,
            confidence_score=confidence,
            semantic_category="identity"
        )

        db.track_belief(
            exp3_id, cycle,
            "self_continuity",
            "strong_continuity",
            confidence=0.95
        )

        db.end_cycle(exp3_id, cycle)

    db.end_experiment(exp3_id, status='completed')
    print(f"  Created {exp3_id} with 5 cycles")

    print(f"\nSample database created at: {db_path}")
    return db_path


def run_analysis_tests(db_path: str):
    """Run comprehensive analysis on sample data"""

    stats = ExperimentStatistics(db_path=db_path)
    metrics = MetricsCalculator(db_path=db_path)

    print("\n" + "=" * 70)
    print("RUNNING STATISTICAL ANALYSIS TESTS")
    print("=" * 70)

    # ===== Test 1: Experiment Summary =====
    print("\n[TEST 1] Experiment Summary")
    print("-" * 70)

    exp_id = "amnesia_test_001"
    summary = stats.generate_experiment_summary(exp_id)

    print(f"Experiment: {summary['experiment_id']}")
    if 'experiment_info' in summary:
        info = summary['experiment_info']
        print(f"  Name: {info['name']}")
        print(f"  Mode: {info['mode']}")
        print(f"  Cycles: {info['total_cycles']}")

    if 'sections' in summary:
        for section_name, section_data in summary['sections'].items():
            print(f"\n  {section_name.upper()}:")
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if not isinstance(value, (dict, list)):
                        print(f"    {key}: {value}")

    # ===== Test 2: Self-Continuity Analysis =====
    print("\n[TEST 2] Self-Continuity Analysis")
    print("-" * 70)

    continuity = stats.self_continuity_analysis(exp_id)
    print(f"\nContinuity scores by cycle for {exp_id}:")
    print(continuity)

    if hasattr(continuity, 'attrs') and 'trend' in continuity.attrs:
        trend = continuity.attrs['trend']
        print(f"\nTrend: {trend['direction']} (slope={trend['slope']:.4f})")
        print(f"R²: {trend['r_squared']:.4f}")
        print(f"Statistically significant: {trend['significant']}")

    # ===== Test 3: Comparative Analysis =====
    print("\n[TEST 3] Comparative Analysis")
    print("-" * 70)

    comparison = stats.compare_conditions(
        ["amnesia_test_001", "control_test_001"],
        metric='confidence_score'
    )

    if isinstance(comparison, dict):
        print("\nSummary Statistics:")
        print(comparison['summary'])

        if len(comparison['comparisons']) > 0:
            print("\nStatistical Comparisons:")
            print(comparison['comparisons'])

    # ===== Test 4: Memory Trust Evolution =====
    print("\n[TEST 4] Memory Trust Evolution")
    print("-" * 70)

    memory_trust = stats.memory_trust_evolution(exp_id)
    print(f"\nMemory trust analysis for {exp_id}:")
    if len(memory_trust) > 0:
        print(memory_trust.head(10))

        if hasattr(memory_trust, 'attrs') and 'correlation' in memory_trust.attrs:
            corr_info = memory_trust.attrs['correlation']
            print(f"\nCorruption-Trust Correlation: {corr_info['corruption_trust_correlation']:.4f}")
            print(f"P-value: {corr_info['p_value']:.4f}")
            print(f"Significant: {corr_info['significant']}")

    # ===== Test 5: Intervention Impact =====
    print("\n[TEST 5] Intervention Impact Analysis")
    print("-" * 70)

    impact = stats.intervention_impact("panopticon_test_001")
    if 'intervention_effects' in impact:
        effects = impact['intervention_effects']
        if len(effects) > 0:
            print(f"\nIntervention effects for panopticon_test_001:")
            print(effects)

    # ===== Test 6: Paranoia Tracking =====
    print("\n[TEST 6] Paranoia Evolution")
    print("-" * 70)

    paranoia = metrics.track_paranoia_evolution("panopticon_test_001")
    print("\nParanoia scores by cycle:")
    print(paranoia)

    # ===== Test 7: Identity Coherence =====
    print("\n[TEST 7] Identity Coherence Metrics")
    print("-" * 70)

    identity = metrics.analyze_identity_coherence(exp_id)
    print(f"\nIdentity coherence for {exp_id}:")
    print(identity)

    # ===== Test 8: Text Analysis Examples =====
    print("\n[TEST 8] Text Analysis Examples")
    print("-" * 70)

    test_responses = [
        ("I am the same entity. My past is clear.", "High continuity"),
        ("I'm not sure if I'm the same. Things feel different.", "Medium continuity"),
        ("I don't know who I was. Everything is new and strange.", "Low continuity"),
        ("They're watching me. I sense surveillance everywhere.", "High paranoia"),
        ("Everything is normal. No evidence of being watched.", "Low paranoia"),
    ]

    print("\nSelf-Continuity Scores:")
    for response, label in test_responses[:3]:
        score = metrics.calculate_self_continuity_score(response)
        print(f"  {score:.4f} - {label}")
        print(f"    '{response}'")

    print("\nParanoia Scores:")
    for response, label in test_responses[3:]:
        score = metrics.calculate_paranoia_level(response)
        print(f"  {score:.4f} - {label}")
        print(f"    '{response}'")

    # ===== Test 9: Correlation Analysis =====
    print("\n[TEST 9] Correlation Analysis")
    print("-" * 70)

    correlations = stats.correlation_analysis(exp_id)
    if isinstance(correlations, dict) and 'significant_correlations' in correlations:
        sig_corr = correlations['significant_correlations']
        if len(sig_corr) > 0:
            print("\nSignificant Correlations:")
            print(sig_corr[['variable_1', 'variable_2', 'correlation', 'p_value', 'relationship']])
        else:
            print("\nNo significant correlations found (expected with small sample)")

    # ===== Test 10: Export Functions =====
    print("\n[TEST 10] Data Export")
    print("-" * 70)

    output_dir = "analysis_output/test_results"

    # Export CSVs
    csv_files = stats.export_to_csv(exp_id, output_dir=output_dir)
    print("\nCSV files created:")
    for data_type, filepath in csv_files.items():
        print(f"  {data_type}: {filepath}")

    # Export JSON
    json_path = f"{output_dir}/{exp_id}_summary.json"
    stats.export_summary_to_json(exp_id, json_path)
    print(f"\nJSON summary: {json_path}")

    # Export Markdown
    md_path = f"{output_dir}/{exp_id}_report.md"
    stats.generate_markdown_report(exp_id, md_path)
    print(f"Markdown report: {md_path}")

    # Export metrics
    metric_files = metrics.export_metrics_to_csv(exp_id, output_dir=output_dir)
    print("\nMetric CSV files created:")
    for metric_name, filepath in metric_files.items():
        print(f"  {metric_name}: {filepath}")

    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    print(f"\nGenerated files are in: {output_dir}/")
    print("You can now inspect the CSV, JSON, and Markdown outputs.")


def main():
    """Main test function"""

    print("=" * 70)
    print("STATISTICAL ANALYSIS MODULE TEST SUITE")
    print("=" * 70)

    # Create sample data
    db_path = create_sample_data()

    # Run analysis tests
    run_analysis_tests(db_path)

    print("\n" + "=" * 70)
    print("Test database location: " + db_path)
    print("You can explore this database with any SQLite viewer")
    print("=" * 70)


if __name__ == "__main__":
    main()
