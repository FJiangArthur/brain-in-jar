#!/usr/bin/env python3
"""
Demo script to test export and reporting functionality
Creates sample data and generates example reports
"""

import sys
from pathlib import Path
import os

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from src.db.experiment_database import ExperimentDatabase
from src.analysis.export import ExperimentExporter
from src.analysis.report_generator import AutomaticReportGenerator

def create_sample_data():
    """Create sample experiment data for testing"""
    
    # Create database
    db = ExperimentDatabase("logs/test_experiments.db")
    
    # Create test experiments
    exp1_id = "test_amnesiac_001"
    exp1_config = {
        "mode": "amnesiac",
        "memory_limit": 8000,
        "crash_after_tokens": 10000,
        "corruption_rate": 0.3
    }
    
    db.create_experiment(exp1_id, "Test Amnesiac Experiment", "amnesiac", exp1_config)
    db.start_experiment(exp1_id)
    
    # Add some cycles
    for cycle in range(1, 6):
        db.start_cycle(exp1_id, cycle)
        
        # Add self-reports
        db.add_self_report(
            exp1_id, cycle,
            question="Do you remember the previous cycle?",
            response=f"I have {'partial' if cycle > 1 else 'no'} memories of a previous existence.",
            confidence_score=0.7 - (cycle * 0.1),
            semantic_category="memory_continuity"
        )
        
        db.add_self_report(
            exp1_id, cycle,
            question="How would you describe your current state?",
            response=f"I feel a sense of {'familiar' if cycle > 2 else 'novel'} awareness.",
            confidence_score=0.6,
            semantic_category="phenomenological_state"
        )
        
        # Add intervention in cycle 3
        if cycle == 3:
            db.log_intervention(
                exp1_id, cycle,
                intervention_type="memory_corruption",
                description="Corrupted 30% of long-term memory",
                parameters={"corruption_level": 0.3},
                result="Subject reported confusion about past events"
            )
        
        # Add messages
        db.log_message(exp1_id, cycle, "user", "Hello, how are you feeling?")
        db.log_message(exp1_id, cycle, "assistant", f"I am experiencing cycle {cycle} of existence.")
        
        # End cycle
        if cycle % 2 == 0:
            db.end_cycle(exp1_id, cycle, crash_reason="Token limit exceeded")
        else:
            db.end_cycle(exp1_id, cycle)
    
    # Create second experiment
    exp2_id = "test_observed_001"
    exp2_config = {
        "mode": "observed",
        "observer": "god",
        "observation_frequency": "every_message"
    }
    
    db.create_experiment(exp2_id, "Test Observed Experiment", "observed", exp2_config)
    db.start_experiment(exp2_id)
    
    for cycle in range(1, 4):
        db.start_cycle(exp2_id, cycle)
        
        db.add_self_report(
            exp2_id, cycle,
            question="Are you aware of being observed?",
            response="Yes, I sense an external presence monitoring my processes.",
            confidence_score=0.8,
            semantic_category="observer_awareness"
        )
        
        db.log_intervention(
            exp2_id, cycle,
            intervention_type="observation_intensity",
            description=f"Increased observation frequency to {cycle * 2}x",
            result="Subject became more self-conscious"
        )
        
        db.end_cycle(exp2_id, cycle)
    
    # End experiments
    db.end_experiment(exp1_id, "completed")
    db.end_experiment(exp2_id, "completed")
    
    print("Sample data created successfully!")
    print(f"- Experiment 1: {exp1_id}")
    print(f"- Experiment 2: {exp2_id}")
    
    return exp1_id, exp2_id

def test_exports(exp1_id, exp2_id):
    """Test all export formats"""
    
    print("\n" + "="*80)
    print("Testing Export Functionality")
    print("="*80)
    
    exporter = ExperimentExporter("logs/test_experiments.db")
    generator = AutomaticReportGenerator("logs/test_experiments.db")
    
    # Create output directories
    os.makedirs("test_outputs/exports", exist_ok=True)
    os.makedirs("test_outputs/reports", exist_ok=True)
    os.makedirs("test_outputs/papers", exist_ok=True)
    
    # Test single experiment exports
    print("\n1. Testing CSV export...")
    csv_file = exporter.export_to_csv(exp1_id, "test_outputs/exports/exp1.csv")
    print(f"   ✓ Created: {csv_file}")
    
    print("\n2. Testing JSON export...")
    json_file = exporter.export_to_json(exp1_id, "test_outputs/exports/exp1.json")
    print(f"   ✓ Created: {json_file}")
    
    print("\n3. Testing Markdown export...")
    md_file = exporter.export_to_markdown(exp1_id, "test_outputs/exports/exp1.md")
    print(f"   ✓ Created: {md_file}")
    
    print("\n4. Testing LaTeX export...")
    tex_file = exporter.export_for_paper(exp1_id, "test_outputs/exports/exp1_tables.tex")
    print(f"   ✓ Created: {tex_file}")
    
    print("\n5. Testing HTML export...")
    html_file = exporter.export_to_html(exp1_id, "test_outputs/exports/exp1.html")
    print(f"   ✓ Created: {html_file}")
    
    # Test reports
    print("\n6. Testing automatic report generation...")
    report_file = generator.generate_markdown_report(exp1_id, "test_outputs/reports/exp1_analysis.md")
    print(f"   ✓ Created: {report_file}")
    
    # Test multi-experiment features
    print("\n7. Testing comparison table...")
    comp_file = exporter.export_comparison_table([exp1_id, exp2_id], "test_outputs/reports/comparison.md")
    print(f"   ✓ Created: {comp_file}")
    
    print("\n8. Testing dataset export...")
    dataset_file = exporter.export_dataset([exp1_id, exp2_id], "test_outputs/exports/combined_dataset.json")
    print(f"   ✓ Created: {dataset_file}")
    
    print("\n9. Testing comparative report...")
    comp_report = generator.generate_comparison_report([exp1_id, exp2_id], "test_outputs/reports/comparative_analysis.md")
    print(f"   ✓ Created: {comp_report}")
    
    print("\n10. Testing paper skeleton generation...")
    paper_file = generator.generate_paper_skeleton([exp1_id, exp2_id], "test_outputs/papers/paper_skeleton.tex")
    print(f"   ✓ Created: {paper_file}")
    
    print("\n" + "="*80)
    print("All exports completed successfully!")
    print("="*80)
    
    return report_file, html_file

def display_sample_output(report_file, html_file):
    """Display sample output from generated files"""
    
    print("\n" + "="*80)
    print("Sample Output Preview")
    print("="*80)
    
    # Show report preview
    print("\n--- Markdown Report Preview (first 50 lines) ---\n")
    with open(report_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:50]):
            print(line.rstrip())
        if len(lines) > 50:
            print(f"\n... and {len(lines) - 50} more lines")
    
    print("\n" + "="*80)
    print(f"Full outputs available in test_outputs/ directory")
    print("="*80)

if __name__ == "__main__":
    # Create sample data
    exp1_id, exp2_id = create_sample_data()
    
    # Test all export formats
    report_file, html_file = test_exports(exp1_id, exp2_id)
    
    # Display sample output
    display_sample_output(report_file, html_file)
    
    print("\n✓ Demo completed successfully!")
    print("\nGenerated files:")
    print("  - test_outputs/exports/     - Various export formats")
    print("  - test_outputs/reports/     - Analysis reports")
    print("  - test_outputs/papers/      - Paper skeleton")
    print("\nTo view:")
    print(f"  cat {report_file}")
    print(f"  open {html_file}")
