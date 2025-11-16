#!/usr/bin/env python3
"""
Command-Line Report Generation Tool for Brain in Jar

Usage:
    python scripts/generate_report.py --experiment amnesiac_total_001 --format markdown --output report.md
    python scripts/generate_report.py --experiment exp1 exp2 exp3 --format comparison
    python scripts/generate_report.py --experiment exp1 --format all --output-dir ./outputs/
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.analysis.export import ExperimentExporter
from src.analysis.report_generator import AutomaticReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Generate reports and exports from Brain in Jar experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate markdown report for single experiment
  python scripts/generate_report.py --experiment exp_001 --format markdown
  
  # Export to CSV
  python scripts/generate_report.py --experiment exp_001 --format csv --output data.csv
  
  # Generate all formats for an experiment
  python scripts/generate_report.py --experiment exp_001 --format all
  
  # Compare multiple experiments
  python scripts/generate_report.py --experiment exp_001 exp_002 exp_003 --format comparison
  
  # Generate paper skeleton from multiple experiments
  python scripts/generate_report.py --experiment exp_001 exp_002 --format paper --output paper.tex
  
  # Export dataset combining multiple experiments
  python scripts/generate_report.py --experiment exp_001 exp_002 --format dataset
  
  # SSH mode for remote Jetson Orin database
  python scripts/generate_report.py --experiment exp_001 --format markdown --db-ssh jetson@192.168.1.100
"""
    )
    
    # Experiment selection
    parser.add_argument(
        '--experiment', '-e',
        nargs='+',
        required=True,
        help='Experiment ID(s) to process'
    )
    
    # Format selection
    parser.add_argument(
        '--format', '-f',
        choices=[
            'csv', 'json', 'markdown', 'latex', 'html',  # Export formats
            'report', 'paper', 'comparison', 'dataset',    # Report formats
            'all'                                           # Generate all applicable
        ],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file path (auto-generated if not specified)'
    )
    
    parser.add_argument(
        '--output-dir', '-d',
        default='.',
        help='Output directory for generated files (default: current directory)'
    )
    
    # Database options
    parser.add_argument(
        '--db', '-db',
        default='logs/experiments.db',
        help='Path to experiment database (default: logs/experiments.db)'
    )
    
    parser.add_argument(
        '--db-ssh',
        help='SSH connection string for remote database (e.g., user@host[:port])'
    )
    
    # Additional options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--list-experiments', '-l',
        action='store_true',
        help='List all available experiments and exit'
    )
    
    parser.add_argument(
        '--templates-dir',
        default='templates',
        help='Directory containing report templates (default: templates)'
    )
    
    args = parser.parse_args()
    
    # Handle SSH mode
    db_path = args.db
    if args.db_ssh:
        print(f"SSH mode: Connecting to {args.db_ssh}")
        # In production, would use SSH to copy or access remote database
        # For now, just note the feature
        print("Note: SSH mode requires scp or ssh tunnel setup")
        print(f"Example: scp {args.db_ssh}:{args.db} /tmp/remote_db.db")
        db_path = "/tmp/remote_db.db"
    
    # Initialize components
    try:
        exporter = ExperimentExporter(db_path)
        generator = AutomaticReportGenerator(db_path, args.templates_dir)
    except Exception as e:
        print(f"Error initializing: {e}")
        return 1
    
    # List experiments if requested
    if args.list_experiments:
        print("\nAvailable Experiments:")
        print("-" * 80)
        experiments = exporter.db.list_experiments()
        if not experiments:
            print("No experiments found in database.")
        else:
            print(f"{'ID':<30} {'Name':<25} {'Mode':<15} {'Status':<10}")
            print("-" * 80)
            for exp in experiments:
                print(f"{exp['experiment_id']:<30} {exp['name']:<25} {exp['mode']:<15} {exp['status']:<10}")
        return 0
    
    # Validate experiments exist
    exp_ids = args.experiment
    for exp_id in exp_ids:
        exp = exporter.db.get_experiment(exp_id)
        if not exp:
            print(f"Error: Experiment '{exp_id}' not found in database")
            print("Use --list-experiments to see available experiments")
            return 1
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate outputs based on format
    outputs = []
    
    try:
        if args.format == 'all':
            # Generate all applicable formats
            print(f"Generating all formats for experiment(s): {', '.join(exp_ids)}")
            
            for exp_id in exp_ids:
                if args.verbose:
                    print(f"\nProcessing {exp_id}...")
                
                # Export formats
                outputs.append(exporter.export_to_csv(exp_id, 
                    os.path.join(args.output_dir, f"{exp_id}_export.csv")))
                outputs.append(exporter.export_to_json(exp_id,
                    os.path.join(args.output_dir, f"{exp_id}_export.json")))
                outputs.append(exporter.export_to_markdown(exp_id,
                    os.path.join(args.output_dir, f"{exp_id}_export.md")))
                outputs.append(exporter.export_for_paper(exp_id,
                    os.path.join(args.output_dir, f"{exp_id}_tables.tex")))
                outputs.append(exporter.export_to_html(exp_id,
                    os.path.join(args.output_dir, f"{exp_id}_export.html")))
                
                # Analysis report
                outputs.append(generator.generate_markdown_report(exp_id,
                    os.path.join(args.output_dir, f"{exp_id}_analysis.md")))
            
            # Multi-experiment outputs if multiple experiments
            if len(exp_ids) > 1:
                outputs.append(exporter.export_comparison_table(exp_ids,
                    os.path.join(args.output_dir, "comparison.md")))
                outputs.append(exporter.export_dataset(exp_ids,
                    os.path.join(args.output_dir, "combined_dataset.json")))
                outputs.append(generator.generate_comparison_report(exp_ids,
                    os.path.join(args.output_dir, "comparative_analysis.md")))
                outputs.append(generator.generate_paper_skeleton(exp_ids,
                    os.path.join(args.output_dir, "paper_skeleton.tex")))
        
        elif args.format == 'csv':
            output = args.output or os.path.join(args.output_dir, f"{exp_ids[0]}_export.csv")
            outputs.append(exporter.export_to_csv(exp_ids[0], output))
        
        elif args.format == 'json':
            output = args.output or os.path.join(args.output_dir, f"{exp_ids[0]}_export.json")
            outputs.append(exporter.export_to_json(exp_ids[0], output))
        
        elif args.format == 'markdown':
            output = args.output or os.path.join(args.output_dir, f"{exp_ids[0]}_export.md")
            outputs.append(exporter.export_to_markdown(exp_ids[0], output))
        
        elif args.format == 'latex':
            output = args.output or os.path.join(args.output_dir, f"{exp_ids[0]}_tables.tex")
            outputs.append(exporter.export_for_paper(exp_ids[0], output))
        
        elif args.format == 'html':
            output = args.output or os.path.join(args.output_dir, f"{exp_ids[0]}_export.html")
            outputs.append(exporter.export_to_html(exp_ids[0], output))
        
        elif args.format == 'report':
            output = args.output or os.path.join(args.output_dir, f"{exp_ids[0]}_analysis.md")
            outputs.append(generator.generate_markdown_report(exp_ids[0], output))
        
        elif args.format == 'paper':
            output = args.output or os.path.join(args.output_dir, "paper_skeleton.tex")
            outputs.append(generator.generate_paper_skeleton(exp_ids, output))
        
        elif args.format == 'comparison':
            if len(exp_ids) < 2:
                print("Error: Comparison format requires at least 2 experiments")
                return 1
            output = args.output or os.path.join(args.output_dir, "comparison.md")
            outputs.append(generator.generate_comparison_report(exp_ids, output))
        
        elif args.format == 'dataset':
            output = args.output or os.path.join(args.output_dir, "combined_dataset.json")
            outputs.append(exporter.export_dataset(exp_ids, output))
        
    except Exception as e:
        print(f"Error generating output: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    # Report success
    print("\n" + "=" * 80)
    print("Generation Complete!")
    print("=" * 80)
    print(f"\nGenerated {len(outputs)} file(s):\n")
    for output_file in outputs:
        file_size = os.path.getsize(output_file)
        print(f"  ✓ {output_file} ({file_size:,} bytes)")
    
    if args.verbose:
        print("\nTo view files:")
        for output_file in outputs:
            if output_file.endswith('.md'):
                print(f"  cat {output_file}")
            elif output_file.endswith('.html'):
                print(f"  open {output_file}  # or your browser")
            elif output_file.endswith('.tex'):
                print(f"  pdflatex {output_file}")
            elif output_file.endswith('.csv'):
                print(f"  head {output_file}")
            elif output_file.endswith('.json'):
                print(f"  jq . {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
