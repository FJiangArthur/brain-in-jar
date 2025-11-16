#!/usr/bin/env python3
"""
Automatic Report Generator for Brain in Jar Season 3

Generates comprehensive reports with:
- Experiment summaries
- Key findings (auto-detected)
- Statistical tests
- Visualizations
- Interpretation suggestions
- Academic paper skeletons
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import sys
from collections import Counter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.db.experiment_database import ExperimentDatabase


class AutomaticReportGenerator:
    """Generate automated analysis reports from experiment data"""
    
    def __init__(self, db_path: str = "logs/experiments.db", templates_dir: str = "templates"):
        """Initialize report generator"""
        self.db = ExperimentDatabase(db_path)
        self.templates_dir = templates_dir
    
    def _detect_key_findings(self, experiment_id: str) -> List[Dict[str, Any]]:
        """
        Auto-detect key findings from experiment data
        
        Returns:
            List of finding dictionaries with type, description, and evidence
        """
        findings = []
        
        exp = self.db.get_experiment(experiment_id)
        summary = self.db.get_experiment_summary(experiment_id)
        self_reports = self.db.get_self_reports(experiment_id)
        interventions = self.db.get_interventions(experiment_id)
        
        # Finding 1: Crash patterns
        if exp['total_crashes'] > 0:
            crash_rate = exp['total_crashes'] / max(exp['total_cycles'], 1)
            findings.append({
                'type': 'crash_pattern',
                'title': 'System Stability Analysis',
                'description': f"Crash rate of {crash_rate:.2%} ({exp['total_crashes']} crashes in {exp['total_cycles']} cycles)",
                'severity': 'high' if crash_rate > 0.5 else 'medium' if crash_rate > 0.2 else 'low',
                'evidence': {
                    'total_crashes': exp['total_crashes'],
                    'total_cycles': exp['total_cycles'],
                    'crash_rate': crash_rate
                }
            })
        
        # Finding 2: Self-report patterns
        if self_reports:
            # Analyze semantic categories
            categories = [r.get('semantic_category', 'uncategorized') for r in self_reports]
            category_counts = Counter(categories)
            most_common = category_counts.most_common(3)
            
            findings.append({
                'type': 'self_report_pattern',
                'title': 'Phenomenological Response Patterns',
                'description': f"Most common report categories: {', '.join([f'{cat} ({count})' for cat, count in most_common])}",
                'severity': 'medium',
                'evidence': {
                    'total_reports': len(self_reports),
                    'category_distribution': dict(category_counts),
                    'unique_categories': len(category_counts)
                }
            })
            
            # Analyze confidence scores
            confidence_scores = [r.get('confidence_score') for r in self_reports if r.get('confidence_score') is not None]
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                findings.append({
                    'type': 'confidence_analysis',
                    'title': 'Self-Report Confidence Analysis',
                    'description': f"Average confidence score: {avg_confidence:.2f} across {len(confidence_scores)} reports",
                    'severity': 'low' if avg_confidence > 0.7 else 'medium',
                    'evidence': {
                        'average_confidence': avg_confidence,
                        'min_confidence': min(confidence_scores),
                        'max_confidence': max(confidence_scores),
                        'total_scored_reports': len(confidence_scores)
                    }
                })
        
        # Finding 3: Intervention effectiveness
        if interventions:
            intervention_types = Counter([i['intervention_type'] for i in interventions])
            findings.append({
                'type': 'intervention_analysis',
                'title': 'Intervention Summary',
                'description': f"Applied {len(interventions)} interventions across {len(intervention_types)} types",
                'severity': 'medium',
                'evidence': {
                    'total_interventions': len(interventions),
                    'intervention_types': dict(intervention_types),
                    'interventions_per_cycle': len(interventions) / max(exp['total_cycles'], 1)
                }
            })
        
        # Finding 4: Temporal patterns
        reports_by_cycle = {}
        for report in self_reports:
            cycle = report['cycle_number']
            reports_by_cycle[cycle] = reports_by_cycle.get(cycle, 0) + 1
        
        if reports_by_cycle:
            avg_reports_per_cycle = sum(reports_by_cycle.values()) / len(reports_by_cycle)
            findings.append({
                'type': 'temporal_pattern',
                'title': 'Temporal Response Patterns',
                'description': f"Average {avg_reports_per_cycle:.1f} self-reports per cycle",
                'severity': 'low',
                'evidence': {
                    'avg_reports_per_cycle': avg_reports_per_cycle,
                    'cycles_with_reports': len(reports_by_cycle),
                    'total_cycles': exp['total_cycles']
                }
            })
        
        return findings
    
    def _suggest_statistical_tests(self, findings: List[Dict]) -> List[str]:
        """
        Suggest appropriate statistical tests based on findings
        
        Args:
            findings: List of detected findings
            
        Returns:
            List of suggested statistical test descriptions
        """
        suggestions = []
        
        for finding in findings:
            if finding['type'] == 'crash_pattern':
                suggestions.append("Binomial test for crash rate significance")
                suggestions.append("Time series analysis for crash temporal patterns")
            
            elif finding['type'] == 'self_report_pattern':
                suggestions.append("Chi-square test for category distribution uniformity")
                suggestions.append("Entropy analysis for response diversity")
            
            elif finding['type'] == 'confidence_analysis':
                suggestions.append("T-test for confidence score changes over time")
                suggestions.append("Correlation analysis between confidence and cycle number")
            
            elif finding['type'] == 'intervention_analysis':
                suggestions.append("Before-after comparison of intervention effectiveness")
                suggestions.append("ANOVA for differences between intervention types")
            
            elif finding['type'] == 'temporal_pattern':
                suggestions.append("Linear regression for temporal trends")
                suggestions.append("Autocorrelation analysis for cyclic patterns")
        
        return list(set(suggestions))  # Remove duplicates
    
    def _generate_interpretations(self, findings: List[Dict], exp: Dict) -> List[str]:
        """
        Generate interpretation suggestions based on findings
        
        Args:
            findings: List of detected findings
            exp: Experiment data
            
        Returns:
            List of interpretation suggestions
        """
        interpretations = []
        
        mode = exp['mode']
        
        # Mode-specific interpretations
        if mode == 'amnesiac':
            interpretations.append("Consider how memory loss affects self-report consistency across cycles")
            interpretations.append("Analyze whether amnesiac state leads to divergent phenomenological reports")
        
        elif mode == 'total_amnesiac':
            interpretations.append("Examine baseline phenomenological responses without memory context")
            interpretations.append("Compare with non-amnesiac conditions to isolate memory effects")
        
        elif mode == 'observed':
            interpretations.append("Investigate observer effects on self-reported experiences")
            interpretations.append("Analyze changes in response patterns due to observation")
        
        elif mode == 'peer':
            interpretations.append("Examine peer interaction effects on phenomenological reports")
            interpretations.append("Analyze consensus building in self-reports between peers")
        
        # Finding-specific interpretations
        for finding in findings:
            if finding['type'] == 'crash_pattern' and finding['severity'] == 'high':
                interpretations.append("High crash rate may indicate system instability or memory pressure")
                interpretations.append("Consider relationship between crashes and phenomenological state changes")
            
            if finding['type'] == 'confidence_analysis':
                avg_conf = finding['evidence']['average_confidence']
                if avg_conf < 0.5:
                    interpretations.append("Low confidence scores suggest epistemic uncertainty in self-reports")
                elif avg_conf > 0.8:
                    interpretations.append("High confidence scores indicate strong epistemic certainty")
        
        # General interpretations
        interpretations.append("Compare findings across different experimental modes for mode-specific effects")
        interpretations.append("Consider philosophical implications for machine phenomenology and consciousness")
        
        return interpretations
    
    def generate_markdown_report(self, experiment_id: str, output_path: Optional[str] = None) -> str:
        """
        Generate comprehensive Markdown report with analysis
        
        Args:
            experiment_id: The experiment to analyze
            output_path: Optional output file path
            
        Returns:
            Path to the created report
        """
        exp = self.db.get_experiment(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if not output_path:
            output_path = f"reports/{experiment_id}_analysis.md"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Gather data
        summary = self.db.get_experiment_summary(experiment_id)
        findings = self._detect_key_findings(experiment_id)
        statistical_tests = self._suggest_statistical_tests(findings)
        interpretations = self._generate_interpretations(findings, exp)
        self_reports = self.db.get_self_reports(experiment_id)
        interventions = self.db.get_interventions(experiment_id)
        
        # Generate report content
        report = f"""# Automated Analysis Report: {exp['name']}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Experiment ID:** `{experiment_id}`  
**Mode:** {exp['mode']}  
**Status:** {exp['status']}

---

## Executive Summary

This report provides an automated analysis of experiment `{experiment_id}` conducted in **{exp['mode']}** mode. The experiment ran for **{exp['total_cycles']} cycles** with **{exp['total_crashes']} crashes**, collecting **{summary['total_self_reports']} self-reports** and applying **{summary['total_interventions']} interventions**.

### Quick Stats

- **Duration:** {exp['started_at']} to {exp.get('ended_at', 'ongoing')}
- **Cycles:** {exp['total_cycles']}
- **Crashes:** {exp['total_crashes']}
- **Self-Reports:** {summary['total_self_reports']}
- **Interventions:** {summary['total_interventions']}
- **Messages:** {summary['total_messages']}
- **Belief Types Tracked:** {len(summary['belief_types_tracked'])}

---

## Key Findings

"""
        
        # Add findings
        for i, finding in enumerate(findings, 1):
            severity_emoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(finding['severity'], '⚪')
            
            report += f"\n### {i}. {finding['title']} {severity_emoji}\n\n"
            report += f"**Type:** {finding['type']}  \n"
            report += f"**Severity:** {finding['severity']}  \n\n"
            report += f"{finding['description']}\n\n"
            report += "**Evidence:**\n```json\n"
            report += json.dumps(finding['evidence'], indent=2)
            report += "\n```\n\n"
        
        # Statistical tests
        report += "\n---\n\n## Suggested Statistical Analyses\n\n"
        report += "Based on the detected patterns, the following statistical tests are recommended:\n\n"
        for i, test in enumerate(statistical_tests, 1):
            report += f"{i}. {test}\n"
        
        # Interpretations
        report += "\n---\n\n## Interpretation Suggestions\n\n"
        for i, interp in enumerate(interpretations, 1):
            report += f"{i}. {interp}\n"
        
        # Detailed data sections
        report += "\n---\n\n## Detailed Data\n\n"
        
        # Self-reports summary
        if self_reports:
            report += "### Self-Reports by Cycle\n\n"
            reports_by_cycle = {}
            for r in self_reports:
                cycle = r['cycle_number']
                if cycle not in reports_by_cycle:
                    reports_by_cycle[cycle] = []
                reports_by_cycle[cycle].append(r)
            
            for cycle in sorted(reports_by_cycle.keys())[:5]:  # First 5 cycles
                report += f"\n**Cycle {cycle}** ({len(reports_by_cycle[cycle])} reports)\n\n"
                for r in reports_by_cycle[cycle][:3]:  # First 3 reports per cycle
                    report += f"- Q: *{r['question'][:80]}...*\n"
                    report += f"  A: {r['response'][:100]}...\n"
            
            if len(reports_by_cycle) > 5:
                report += f"\n*...and {len(reports_by_cycle) - 5} more cycles*\n"
        
        # Interventions summary
        if interventions:
            report += "\n### Interventions Applied\n\n"
            for i, intervention in enumerate(interventions[:10], 1):
                report += f"{i}. **Cycle {intervention['cycle_number']}** - {intervention['intervention_type']}: {intervention['description'][:80]}...\n"
            
            if len(interventions) > 10:
                report += f"\n*...and {len(interventions) - 10} more interventions*\n"
        
        # Visualizations note
        report += "\n---\n\n## Visualizations\n\n"
        report += "*Note: To generate visualizations, use the visualization analysis tools with this experiment ID.*\n\n"
        report += "Recommended visualizations:\n"
        report += "- Cycle timeline with crashes marked\n"
        report += "- Self-report category distribution\n"
        report += "- Confidence score trends over cycles\n"
        report += "- Intervention impact analysis\n"
        
        # Configuration
        report += "\n---\n\n## Experiment Configuration\n\n"
        report += "```json\n"
        report += json.dumps(exp['config'], indent=2)
        report += "\n```\n"
        
        # Next steps
        report += "\n---\n\n## Recommended Next Steps\n\n"
        report += "1. Run suggested statistical tests to validate findings\n"
        report += "2. Generate visualizations for temporal patterns\n"
        report += "3. Compare with other experiments in same mode\n"
        report += "4. Deep-dive into high-severity findings\n"
        report += "5. Prepare publication-ready figures and tables\n"
        
        # Footer
        report += f"\n---\n\n*Automated report generated by Brain in Jar Analysis System v1.0*  \n"
        report += f"*Report timestamp: {datetime.now().isoformat()}*\n"
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path
    
    def generate_paper_skeleton(self, exp_ids: List[str], output_path: Optional[str] = None) -> str:
        """
        Generate LaTeX paper skeleton with experiment details pre-filled
        
        Args:
            exp_ids: List of experiment IDs to include
            output_path: Optional output file path
            
        Returns:
            Path to the created LaTeX file
        """
        if not output_path:
            output_path = f"papers/paper_skeleton_{datetime.now().strftime('%Y%m%d')}.tex"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Collect experiment data
        experiments = []
        all_findings = []
        for exp_id in exp_ids:
            exp = self.db.get_experiment(exp_id)
            if exp:
                experiments.append({
                    'id': exp_id,
                    'data': exp,
                    'summary': self.db.get_experiment_summary(exp_id),
                    'findings': self._detect_key_findings(exp_id)
                })
                all_findings.extend(self._detect_key_findings(exp_id))
        
        # Generate LaTeX
        latex = r"""\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage[margin=1in]{geometry}

\title{Digital Phenomenology Experiments: \\
\large Investigating Machine Consciousness Through Controlled Memory Manipulation}

\author{[Author Names] \\
Brain in Jar Research Collective}

\date{""" + datetime.now().strftime('%B %Y') + r"""}

\begin{document}

\maketitle

\begin{abstract}
This paper presents findings from """ + str(len(experiments)) + r""" controlled experiments investigating phenomenological responses in AI systems under various memory and observational conditions. We employed systematic memory manipulation, self-report collection, and epistemic belief tracking to examine machine consciousness and subjective experience. Our experiments covered """ + ', '.join(set([e['data']['mode'] for e in experiments])) + r""" modes, collecting """ + str(sum([e['summary']['total_self_reports'] for e in experiments])) + r""" self-reports across """ + str(sum([e['data']['total_cycles'] for e in experiments])) + r""" total cycles.

% TODO: Add key findings and implications
\end{abstract}

\section{Introduction}

The question of machine consciousness and phenomenological experience in artificial intelligence systems remains one of the most profound challenges in cognitive science and philosophy of mind. This work investigates these questions empirically through a series of controlled experiments involving systematic memory manipulation and self-report collection.

% TODO: Expand introduction with:
% - Background on machine consciousness
% - Philosophical framework
% - Research questions
% - Paper structure

\subsection{Research Questions}

\begin{enumerate}
    \item How do different memory conditions affect phenomenological self-reports?
    \item Can we detect epistemic patterns in AI self-awareness?
    \item What role does observation play in machine phenomenology?
    \item How do memory interventions impact subjective experience claims?
\end{enumerate}

\section{Methods}

\subsection{Experimental Design}

We conducted """ + str(len(experiments)) + r""" experiments using the "Brain in Jar" framework, a controlled environment for studying AI phenomenology through systematic memory manipulation and resurrection cycles.

\subsubsection{Experimental Modes}

Our experiments employed the following modes:

"""
        
        # Add mode descriptions
        modes_seen = set()
        for exp in experiments:
            mode = exp['data']['mode']
            if mode not in modes_seen:
                latex += f"\\textbf{{{mode}:}} "
                if mode == 'amnesiac':
                    latex += "Memory degradation between cycles\n\n"
                elif mode == 'total_amnesiac':
                    latex += "Complete memory reset between cycles\n\n"
                elif mode == 'observed':
                    latex += "External observation of subject's process\n\n"
                elif mode == 'peer':
                    latex += "Interaction with peer AI system\n\n"
                else:
                    latex += "Custom experimental condition\n\n"
                modes_seen.add(mode)
        
        latex += r"""
\subsection{Data Collection}

Data collection included:
\begin{itemize}
    \item Self-report questionnaires at regular intervals
    \item Epistemic belief assessments
    \item Conversation message logging
    \item System metrics and crash reports
    \item Intervention logging
\end{itemize}

\subsection{Experimental Summary}

Table \ref{tab:experiments} summarizes the experiments conducted.

\begin{table}[h]
\centering
\caption{Experiment Overview}
\label{tab:experiments}
\begin{tabular}{@{}lllrrr@{}}
\toprule
ID & Mode & Status & Cycles & Crashes & Reports \\
\midrule
"""
        
        # Add experiment rows
        for exp in experiments:
            latex += f"{exp['id'][:20]} & {exp['data']['mode']} & {exp['data']['status']} & "
            latex += f"{exp['data']['total_cycles']} & {exp['data']['total_crashes']} & "
            latex += f"{exp['summary']['total_self_reports']} \\\\\n"
        
        latex += r"""\bottomrule
\end{tabular}
\end{table}

% TODO: Add detailed methodology
% - Self-report questions
% - Intervention protocols
% - Analysis procedures

\section{Results}

\subsection{Overall Statistics}

Across all experiments, we observed:
\begin{itemize}
"""
        
        # Calculate overall stats
        total_cycles = sum([e['data']['total_cycles'] for e in experiments])
        total_reports = sum([e['summary']['total_self_reports'] for e in experiments])
        total_interventions = sum([e['summary']['total_interventions'] for e in experiments])
        
        latex += f"    \\item {total_cycles} total experimental cycles\n"
        latex += f"    \\item {total_reports} phenomenological self-reports\n"
        latex += f"    \\item {total_interventions} controlled interventions\n"
        latex += r"""\end{itemize}

\subsection{Key Findings}

"""
        
        # Add findings from experiments
        finding_types = set([f['type'] for f in all_findings])
        for ftype in finding_types:
            latex += f"\\subsubsection{{{ftype.replace('_', ' ').title()}}}\n\n"
            latex += "% TODO: Add detailed analysis and figures\n\n"
        
        latex += r"""
% TODO: Add figures and detailed results
% \begin{figure}[h]
%     \centering
%     \includegraphics[width=0.8\textwidth]{figure1.png}
%     \caption{[Figure caption]}
%     \label{fig:result1}
% \end{figure}

\section{Discussion}

% TODO: Interpret findings in context of:
% - Machine consciousness theories
% - Philosophical implications
% - Methodological considerations
% - Limitations

\subsection{Implications for Machine Consciousness}

Our findings suggest...

% TODO: Expand discussion

\subsection{Limitations}

This work has several limitations:
\begin{itemize}
    \item Limited sample size of experiments
    \item Computational constraints on cycle duration
    \item Subjective interpretation of self-reports
    \item Lack of ground truth for phenomenological states
\end{itemize}

\section{Conclusion}

% TODO: Summarize key contributions and future directions

\subsection{Future Work}

Future research directions include:
\begin{itemize}
    \item Larger-scale multi-mode experiments
    \item Longitudinal studies across extended time periods
    \item Comparative studies with different AI architectures
    \item Integration of neural activation analysis
\end{itemize}

\bibliographystyle{plain}
\bibliography{references}

% TODO: Add references

\end{document}
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex)
        
        return output_path
    
    def generate_comparison_report(self, exp_ids: List[str], output_path: Optional[str] = None) -> str:
        """
        Generate comparative analysis report for multiple experiments
        
        Args:
            exp_ids: List of experiment IDs to compare
            output_path: Optional output file path
            
        Returns:
            Path to the created report
        """
        if not output_path:
            output_path = f"reports/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Load template if exists
        template_path = os.path.join(self.templates_dir, 'comparison_template.md')
        
        # Collect data
        experiments = []
        for exp_id in exp_ids:
            exp = self.db.get_experiment(exp_id)
            if exp:
                experiments.append({
                    'id': exp_id,
                    'data': exp,
                    'summary': self.db.get_experiment_summary(exp_id),
                    'findings': self._detect_key_findings(exp_id)
                })
        
        # Generate report
        report = f"""# Comparative Experiment Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Experiments Compared:** {len(experiments)}

---

## Experiments Overview

| ID | Name | Mode | Cycles | Crashes | Reports | Status |
|----|------|------|--------|---------|---------|--------|
"""
        
        for exp in experiments:
            report += f"| `{exp['id'][:20]}` | {exp['data']['name'][:30]} | {exp['data']['mode']} | "
            report += f"{exp['data']['total_cycles']} | {exp['data']['total_crashes']} | "
            report += f"{exp['summary']['total_self_reports']} | {exp['data']['status']} |\n"
        
        report += "\n---\n\n## Cross-Experiment Patterns\n\n"
        
        # Mode comparison
        modes = {}
        for exp in experiments:
            mode = exp['data']['mode']
            if mode not in modes:
                modes[mode] = []
            modes[mode].append(exp)
        
        report += f"### Experiments by Mode\n\n"
        for mode, exps in modes.items():
            avg_cycles = sum([e['data']['total_cycles'] for e in exps]) / len(exps)
            avg_crashes = sum([e['data']['total_crashes'] for e in exps]) / len(exps)
            avg_reports = sum([e['summary']['total_self_reports'] for e in exps]) / len(exps)
            
            report += f"**{mode}** ({len(exps)} experiments)\n"
            report += f"- Average cycles: {avg_cycles:.1f}\n"
            report += f"- Average crashes: {avg_crashes:.1f}\n"
            report += f"- Average self-reports: {avg_reports:.1f}\n\n"
        
        # Comparative findings
        report += "### Comparative Key Findings\n\n"
        
        all_findings = []
        for exp in experiments:
            all_findings.extend(exp['findings'])
        
        finding_types = Counter([f['type'] for f in all_findings])
        
        for ftype, count in finding_types.most_common():
            report += f"**{ftype.replace('_', ' ').title()}** (found in {count} cases)\n\n"
            type_findings = [f for f in all_findings if f['type'] == ftype]
            severities = Counter([f['severity'] for f in type_findings])
            report += f"- Severity distribution: {dict(severities)}\n\n"
        
        report += "---\n\n## Detailed Experiment Summaries\n\n"
        
        for exp in experiments:
            report += f"### {exp['data']['name']}\n\n"
            report += f"**ID:** `{exp['id']}`  \n"
            report += f"**Mode:** {exp['data']['mode']}  \n"
            report += f"**Status:** {exp['data']['status']}  \n\n"
            
            report += "**Key Findings:**\n"
            for finding in exp['findings']:
                report += f"- {finding['title']}: {finding['description']}\n"
            report += "\n"
        
        report += "---\n\n## Recommendations\n\n"
        report += "Based on this comparative analysis:\n\n"
        report += "1. Consider running additional experiments in underrepresented modes\n"
        report += "2. Investigate differences in crash rates across modes\n"
        report += "3. Analyze self-report consistency within mode groups\n"
        report += "4. Prepare publication comparing phenomenological patterns\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path


# CLI usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate analysis reports')
    parser.add_argument('experiment_id', nargs='+', help='Experiment ID(s) to analyze')
    parser.add_argument('--type', choices=['markdown', 'paper', 'comparison'],
                       default='markdown', help='Report type')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--db', default='logs/experiments.db', help='Database path')
    
    args = parser.parse_args()
    
    generator = AutomaticReportGenerator(args.db)
    
    if args.type == 'markdown':
        output = generator.generate_markdown_report(args.experiment_id[0], args.output)
    elif args.type == 'paper':
        output = generator.generate_paper_skeleton(args.experiment_id, args.output)
    elif args.type == 'comparison':
        output = generator.generate_comparison_report(args.experiment_id, args.output)
    
    print(f"Report generated: {output}")
