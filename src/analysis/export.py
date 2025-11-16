#!/usr/bin/env python3
"""
Export Tools for Brain in Jar Season 3

Provides comprehensive export functionality for experiment data in multiple formats:
- CSV (for Excel/R/SPSS)
- JSON (for web tools)
- Markdown (for GitHub/docs)
- LaTeX (for academic papers)
- HTML (for web viewing)
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.db.experiment_database import ExperimentDatabase


class ExperimentExporter:
    """Export experiment data in various formats"""
    
    def __init__(self, db_path: str = "logs/experiments.db"):
        """Initialize exporter with database connection"""
        self.db = ExperimentDatabase(db_path)
    
    # ===== Single Experiment Exports =====
    
    def export_to_csv(self, experiment_id: str, output_path: Optional[str] = None) -> str:
        """
        Export experiment data to flat CSV format
        
        Args:
            experiment_id: The experiment to export
            output_path: Optional output file path
            
        Returns:
            Path to the created CSV file
        """
        exp = self.db.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if not output_path:
            output_path = f"exports/{experiment_id}_export.csv"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Gather all data
        self_reports = self.db.get_self_reports(experiment_id)
        interventions = self.db.get_interventions(experiment_id)
        messages = self.db.get_messages(experiment_id)
        
        # Create comprehensive CSV with all data types
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'data_type', 'cycle_number', 'timestamp', 'content',
                'metadata', 'confidence', 'category'
            ])
            
            # Self-reports
            for report in self_reports:
                writer.writerow([
                    'self_report',
                    report['cycle_number'],
                    report['timestamp'],
                    f"Q: {report['question']} | A: {report['response']}",
                    report.get('semantic_category', ''),
                    report.get('confidence_score', ''),
                    'self_report'
                ])
            
            # Interventions
            for intervention in interventions:
                writer.writerow([
                    'intervention',
                    intervention['cycle_number'],
                    intervention['timestamp'],
                    f"{intervention['intervention_type']}: {intervention['description']}",
                    intervention.get('result', ''),
                    '',
                    intervention['intervention_type']
                ])
            
            # Messages
            for message in messages:
                writer.writerow([
                    'message',
                    message['cycle_number'],
                    message['timestamp'],
                    f"[{message['role']}] {message['content'][:100]}...",
                    message.get('emotion', ''),
                    '',
                    message['role']
                ])
        
        return output_path
    
    def export_to_json(self, experiment_id: str, output_path: Optional[str] = None) -> str:
        """
        Export experiment data to structured JSON format
        
        Args:
            experiment_id: The experiment to export
            output_path: Optional output file path
            
        Returns:
            Path to the created JSON file
        """
        exp = self.db.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if not output_path:
            output_path = f"exports/{experiment_id}_export.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build complete export structure
        export_data = {
            'experiment': exp,
            'summary': self.db.get_experiment_summary(experiment_id),
            'self_reports': self.db.get_self_reports(experiment_id),
            'interventions': self.db.get_interventions(experiment_id),
            'messages': self.db.get_messages(experiment_id),
            'export_metadata': {
                'exported_at': datetime.now().isoformat(),
                'exporter_version': '1.0.0',
                'format': 'json'
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def export_to_markdown(self, experiment_id: str, output_path: Optional[str] = None) -> str:
        """
        Export experiment data to readable Markdown report
        
        Args:
            experiment_id: The experiment to export
            output_path: Optional output file path
            
        Returns:
            Path to the created Markdown file
        """
        exp = self.db.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if not output_path:
            output_path = f"exports/{experiment_id}_report.md"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        summary = self.db.get_experiment_summary(experiment_id)
        self_reports = self.db.get_self_reports(experiment_id)
        interventions = self.db.get_interventions(experiment_id)
        
        # Generate Markdown content
        md_content = f"""# Experiment Report: {exp['name']}

**Experiment ID:** `{experiment_id}`  
**Mode:** {exp['mode']}  
**Status:** {exp['status']}  
**Created:** {exp['created_at']}  
**Duration:** {exp['started_at']} to {exp.get('ended_at', 'ongoing')}

## Summary Statistics

- **Total Cycles:** {exp['total_cycles']}
- **Total Crashes:** {exp['total_crashes']}
- **Self-Reports:** {summary['total_self_reports']}
- **Interventions:** {summary['total_interventions']}
- **Messages:** {summary['total_messages']}

## Configuration

```json
{json.dumps(exp['config'], indent=2)}
```

## Self-Reports

"""
        
        # Group self-reports by cycle
        reports_by_cycle = {}
        for report in self_reports:
            cycle = report['cycle_number']
            if cycle not in reports_by_cycle:
                reports_by_cycle[cycle] = []
            reports_by_cycle[cycle].append(report)
        
        for cycle in sorted(reports_by_cycle.keys()):
            md_content += f"\n### Cycle {cycle}\n\n"
            for report in reports_by_cycle[cycle]:
                md_content += f"**Q:** {report['question']}  \n"
                md_content += f"**A:** {report['response']}  \n"
                if report.get('confidence_score'):
                    md_content += f"**Confidence:** {report['confidence_score']}  \n"
                if report.get('semantic_category'):
                    md_content += f"**Category:** {report['semantic_category']}  \n"
                md_content += "\n"
        
        # Interventions
        if interventions:
            md_content += "\n## Interventions\n\n"
            for intervention in interventions:
                md_content += f"### Cycle {intervention['cycle_number']}: {intervention['intervention_type']}\n\n"
                md_content += f"**Description:** {intervention['description']}  \n"
                if intervention.get('result'):
                    md_content += f"**Result:** {intervention['result']}  \n"
                md_content += f"**Timestamp:** {intervention['timestamp']}  \n\n"
        
        # Footer
        md_content += f"\n---\n\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return output_path
    
    def export_for_paper(self, experiment_id: str, output_path: Optional[str] = None) -> str:
        """
        Export experiment data formatted for academic paper (LaTeX tables/figures)
        
        Args:
            experiment_id: The experiment to export
            output_path: Optional output file path
            
        Returns:
            Path to the created LaTeX file
        """
        exp = self.db.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if not output_path:
            output_path = f"exports/{experiment_id}_paper_tables.tex"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        summary = self.db.get_experiment_summary(experiment_id)
        self_reports = self.db.get_self_reports(experiment_id)
        interventions = self.db.get_interventions(experiment_id)
        
        # Generate LaTeX content
        latex_content = f"""% LaTeX tables and figures for {exp['name']}
% Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

% Summary Statistics Table
\\begin{{table}}[h]
\\centering
\\caption{{Experiment Summary: {exp['name']}}}
\\label{{tab:{experiment_id}_summary}}
\\begin{{tabular}}{{ll}}
\\hline
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\hline
Experiment ID & \\texttt{{{experiment_id}}} \\\\
Mode & {exp['mode']} \\\\
Total Cycles & {exp['total_cycles']} \\\\
Total Crashes & {exp['total_crashes']} \\\\
Self-Reports & {summary['total_self_reports']} \\\\
Interventions & {summary['total_interventions']} \\\\
Messages & {summary['total_messages']} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}

% Self-Reports by Cycle Table
\\begin{{table}}[h]
\\centering
\\caption{{Self-Reports Summary}}
\\label{{tab:{experiment_id}_selfreports}}
\\begin{{tabular}}{{|c|l|c|}}
\\hline
\\textbf{{Cycle}} & \\textbf{{Category}} & \\textbf{{Count}} \\\\
\\hline
"""
        
        # Count reports by cycle and category
        cycle_categories = {}
        for report in self_reports:
            cycle = report['cycle_number']
            category = report.get('semantic_category', 'uncategorized')
            key = (cycle, category)
            cycle_categories[key] = cycle_categories.get(key, 0) + 1
        
        for (cycle, category), count in sorted(cycle_categories.items()):
            latex_content += f"{cycle} & {category} & {count} \\\\\n"
        
        latex_content += """\\hline
\\end{tabular}
\\end{table}

"""
        
        # Interventions Table
        if interventions:
            latex_content += f"""% Interventions Table
\\begin{{table}}[h]
\\centering
\\caption{{Interventions Applied}}
\\label{{tab:{experiment_id}_interventions}}
\\begin{{tabular}}{{|c|l|p{{6cm}}|}}
\\hline
\\textbf{{Cycle}} & \\textbf{{Type}} & \\textbf{{Description}} \\\\
\\hline
"""
            for intervention in interventions:
                itype = intervention['intervention_type'].replace('_', '\\_')
                desc = intervention['description'][:60].replace('_', '\\_')
                latex_content += f"{intervention['cycle_number']} & {itype} & {desc}... \\\\\n"
            
            latex_content += """\\hline
\\end{tabular}
\\end{table}

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return output_path
    
    def export_to_html(self, experiment_id: str, output_path: Optional[str] = None) -> str:
        """
        Export experiment data to HTML for web viewing
        
        Args:
            experiment_id: The experiment to export
            output_path: Optional output file path
            
        Returns:
            Path to the created HTML file
        """
        exp = self.db.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if not output_path:
            output_path = f"exports/{experiment_id}_report.html"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        summary = self.db.get_experiment_summary(experiment_id)
        self_reports = self.db.get_self_reports(experiment_id)
        interventions = self.db.get_interventions(experiment_id)
        
        # Generate HTML content with embedded CSS
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experiment Report: {exp['name']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #555;
        }}
        .metric-value {{
            color: #667eea;
            font-size: 1.2em;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .cycle-group {{
            border-left: 3px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .report-item {{
            background: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .question {{
            font-weight: bold;
            color: #333;
        }}
        .answer {{
            color: #555;
            margin-top: 5px;
        }}
        .intervention {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .timestamp {{
            color: #888;
            font-size: 0.9em;
        }}
        h1, h2, h3 {{
            margin-top: 0;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{exp['name']}</h1>
        <p><code>{experiment_id}</code> | Mode: {exp['mode']} | Status: {exp['status']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary Statistics</h2>
        <div class="metric">
            <span class="metric-label">Total Cycles:</span>
            <span class="metric-value">{exp['total_cycles']}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Total Crashes:</span>
            <span class="metric-value">{exp['total_crashes']}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Self-Reports:</span>
            <span class="metric-value">{summary['total_self_reports']}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Interventions:</span>
            <span class="metric-value">{summary['total_interventions']}</span>
        </div>
        <div class="metric">
            <span class="metric-label">Messages:</span>
            <span class="metric-value">{summary['total_messages']}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>Self-Reports</h2>
"""
        
        # Group reports by cycle
        reports_by_cycle = {}
        for report in self_reports:
            cycle = report['cycle_number']
            if cycle not in reports_by_cycle:
                reports_by_cycle[cycle] = []
            reports_by_cycle[cycle].append(report)
        
        for cycle in sorted(reports_by_cycle.keys()):
            html_content += f'        <div class="cycle-group">\n'
            html_content += f'            <h3>Cycle {cycle}</h3>\n'
            for report in reports_by_cycle[cycle]:
                confidence_html = f" | Confidence: {report['confidence_score']}" if report.get('confidence_score') else ""
                category_html = f" | Category: {report['semantic_category']}" if report.get('semantic_category') else ""
                html_content += f"""            <div class="report-item">
                <div class="question">Q: {report['question']}</div>
                <div class="answer">A: {report['response']}</div>
                <div class="timestamp">{report['timestamp']}{confidence_html}{category_html}</div>
            </div>
"""
            html_content += '        </div>\n'
        
        html_content += '    </div>\n'
        
        # Interventions
        if interventions:
            html_content += '    <div class="section">\n        <h2>Interventions</h2>\n'
            for intervention in interventions:
                result_html = f"<br><strong>Result:</strong> {intervention['result']}" if intervention.get('result') else ""
                html_content += f"""        <div class="intervention">
            <h3>Cycle {intervention['cycle_number']}: {intervention['intervention_type']}</h3>
            <p>{intervention['description']}{result_html}</p>
            <div class="timestamp">{intervention['timestamp']}</div>
        </div>
"""
            html_content += '    </div>\n'
        
        # Footer
        html_content += f"""
    <div class="section" style="text-align: center; color: #888;">
        <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    # ===== Multi-Experiment Exports =====
    
    def export_comparison_table(self, exp_ids: List[str], output_path: Optional[str] = None) -> str:
        """
        Export comparison matrix of multiple experiments
        
        Args:
            exp_ids: List of experiment IDs to compare
            output_path: Optional output file path
            
        Returns:
            Path to the created comparison file
        """
        if not output_path:
            output_path = f"exports/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Collect data for all experiments
        experiments_data = []
        for exp_id in exp_ids:
            exp = self.db.get_experiment(exp_id)
            if exp:
                summary = self.db.get_experiment_summary(exp_id)
                experiments_data.append({
                    'id': exp_id,
                    'name': exp['name'],
                    'mode': exp['mode'],
                    'cycles': exp['total_cycles'],
                    'crashes': exp['total_crashes'],
                    'reports': summary['total_self_reports'],
                    'interventions': summary['total_interventions'],
                    'status': exp['status']
                })
        
        # Generate comparison table
        md_content = f"""# Experiment Comparison

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Table

| Experiment | Mode | Cycles | Crashes | Self-Reports | Interventions | Status |
|------------|------|--------|---------|--------------|---------------|--------|
"""
        
        for exp in experiments_data:
            md_content += f"| {exp['name'][:30]} | {exp['mode']} | {exp['cycles']} | {exp['crashes']} | {exp['reports']} | {exp['interventions']} | {exp['status']} |\n"
        
        md_content += "\n## Detailed Comparison\n\n"
        
        for exp in experiments_data:
            md_content += f"### {exp['name']}\n\n"
            md_content += f"- **ID:** `{exp['id']}`\n"
            md_content += f"- **Mode:** {exp['mode']}\n"
            md_content += f"- **Cycles:** {exp['cycles']}\n"
            md_content += f"- **Crashes:** {exp['crashes']}\n"
            md_content += f"- **Self-Reports:** {exp['reports']}\n"
            md_content += f"- **Interventions:** {exp['interventions']}\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return output_path
    
    def export_dataset(self, exp_ids: List[str], output_path: Optional[str] = None) -> str:
        """
        Export combined dataset from multiple experiments for analysis
        
        Args:
            exp_ids: List of experiment IDs to combine
            output_path: Optional output file path
            
        Returns:
            Path to the created dataset file (JSON)
        """
        if not output_path:
            output_path = f"exports/dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Collect all data
        combined_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'experiment_count': len(exp_ids),
                'experiment_ids': exp_ids
            },
            'experiments': []
        }
        
        for exp_id in exp_ids:
            exp = self.db.get_experiment(exp_id)
            if exp:
                exp_data = {
                    'experiment': exp,
                    'summary': self.db.get_experiment_summary(exp_id),
                    'self_reports': self.db.get_self_reports(exp_id),
                    'interventions': self.db.get_interventions(exp_id),
                    'messages': self.db.get_messages(exp_id)
                }
                combined_data['experiments'].append(exp_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        return output_path


# CLI usage example
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Export experiment data')
    parser.add_argument('experiment_id', help='Experiment ID to export')
    parser.add_argument('--format', choices=['csv', 'json', 'markdown', 'latex', 'html'],
                       default='markdown', help='Export format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--db', default='logs/experiments.db', help='Database path')
    
    args = parser.parse_args()
    
    exporter = ExperimentExporter(args.db)
    
    if args.format == 'csv':
        output = exporter.export_to_csv(args.experiment_id, args.output)
    elif args.format == 'json':
        output = exporter.export_to_json(args.experiment_id, args.output)
    elif args.format == 'markdown':
        output = exporter.export_to_markdown(args.experiment_id, args.output)
    elif args.format == 'latex':
        output = exporter.export_for_paper(args.experiment_id, args.output)
    elif args.format == 'html':
        output = exporter.export_to_html(args.experiment_id, args.output)
    
    print(f"Exported to: {output}")
