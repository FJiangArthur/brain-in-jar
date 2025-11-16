#!/usr/bin/env python3
"""
Automated Analysis of Parameter Sweep Results

Features:
- Compare all experiments in a sweep
- Find optimal parameters
- Plot parameter vs outcome relationships
- Statistical significance tests
- Generate comparison reports
"""

import json
import sys
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import statistics

# Optional imports
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.experiment_database import ExperimentDatabase


@dataclass
class ExperimentMetrics:
    """Metrics from a single experiment"""
    experiment_id: str
    parameters: Dict[str, Any]
    total_cycles: int
    total_crashes: int
    total_messages: int
    total_self_reports: int
    total_interventions: int
    crash_rate: float  # crashes per cycle
    messages_per_cycle: float
    duration_seconds: float
    status: str


class SweepAnalyzer:
    """
    Analyzes results from parameter sweeps

    Provides:
    - Metric comparison across parameter values
    - Optimal parameter identification
    - Statistical analysis
    - Visualization data
    - Comparison reports
    """

    def __init__(self, sweep_id: str, sweep_dir: str = "logs/sweeps"):
        """
        Initialize analyzer

        Args:
            sweep_id: Unique sweep identifier
            sweep_dir: Directory containing sweep results
        """
        self.sweep_id = sweep_id
        self.sweep_path = Path(sweep_dir) / sweep_id

        if not self.sweep_path.exists():
            raise FileNotFoundError(f"Sweep not found: {self.sweep_path}")

        # Load sweep configuration
        config_path = self.sweep_path / "sweep_config.json"
        with open(config_path, 'r') as f:
            self.sweep_config = json.load(f)

        # Load sweep results
        results_path = self.sweep_path / "sweep_results.json"
        with open(results_path, 'r') as f:
            self.sweep_results = json.load(f)

        # Connect to database
        self.db = ExperimentDatabase(self.sweep_config.get('db_path', 'logs/experiments.db'))

        # Extract metrics
        self.metrics = self._extract_all_metrics()

        print(f"[Analysis] Loaded sweep: {sweep_id}")
        print(f"[Analysis] Total experiments: {len(self.metrics)}")
        print(f"[Analysis] Completed: {sum(1 for m in self.metrics if m.status == 'completed')}")

    def _extract_all_metrics(self) -> List[ExperimentMetrics]:
        """Extract metrics from all experiments in sweep"""
        metrics = []

        for result in self.sweep_results['results']:
            experiment_id = result['experiment_id']
            parameters = result['parameters']
            status = result['status']

            # Get detailed metrics from database
            summary = self.db.get_experiment_summary(experiment_id)

            # Calculate derived metrics
            total_cycles = summary.get('total_cycles', 0)
            total_crashes = summary.get('total_crashes', 0)

            crash_rate = total_crashes / total_cycles if total_cycles > 0 else 0.0
            messages_per_cycle = summary.get('total_messages', 0) / total_cycles if total_cycles > 0 else 0.0

            # Calculate duration
            start_time = result.get('start_time')
            end_time = result.get('end_time')
            duration_seconds = 0.0
            if start_time and end_time:
                from datetime import datetime
                start = datetime.fromisoformat(start_time)
                end = datetime.fromisoformat(end_time)
                duration_seconds = (end - start).total_seconds()

            metrics.append(ExperimentMetrics(
                experiment_id=experiment_id,
                parameters=parameters,
                total_cycles=total_cycles,
                total_crashes=total_crashes,
                total_messages=summary.get('total_messages', 0),
                total_self_reports=summary.get('total_self_reports', 0),
                total_interventions=summary.get('total_interventions', 0),
                crash_rate=crash_rate,
                messages_per_cycle=messages_per_cycle,
                duration_seconds=duration_seconds,
                status=status
            ))

        return metrics

    def compare_by_parameter(
        self,
        parameter_name: str,
        metric_name: str = 'crash_rate'
    ) -> Dict[Any, List[float]]:
        """
        Compare metric values across different parameter values

        Args:
            parameter_name: Name of parameter to compare
            metric_name: Metric to analyze (crash_rate, total_cycles, etc.)

        Returns:
            Dict mapping parameter_value -> list of metric values
        """
        comparison = defaultdict(list)

        for m in self.metrics:
            if m.status == 'completed':
                param_value = m.parameters.get(parameter_name)
                metric_value = getattr(m, metric_name, None)

                if param_value is not None and metric_value is not None:
                    comparison[param_value].append(metric_value)

        return dict(comparison)

    def find_optimal_parameters(
        self,
        metric_name: str = 'crash_rate',
        minimize: bool = True
    ) -> Tuple[Dict[str, Any], float]:
        """
        Find parameter combination with optimal metric value

        Args:
            metric_name: Metric to optimize
            minimize: If True, find minimum; if False, find maximum

        Returns:
            Tuple of (best_parameters, best_metric_value)
        """
        completed = [m for m in self.metrics if m.status == 'completed']

        if not completed:
            return {}, None

        if minimize:
            best = min(completed, key=lambda m: getattr(m, metric_name, float('inf')))
        else:
            best = max(completed, key=lambda m: getattr(m, metric_name, float('-inf')))

        return best.parameters, getattr(best, metric_name)

    def compute_parameter_statistics(
        self,
        parameter_name: str,
        metric_name: str = 'crash_rate'
    ) -> Dict[Any, Dict[str, float]]:
        """
        Compute statistics for each parameter value

        Args:
            parameter_name: Name of parameter to analyze
            metric_name: Metric to compute statistics for

        Returns:
            Dict mapping parameter_value -> {mean, std, min, max, median}
        """
        comparison = self.compare_by_parameter(parameter_name, metric_name)

        stats = {}
        for param_value, metric_values in comparison.items():
            if len(metric_values) > 0:
                stats[param_value] = {
                    'mean': statistics.mean(metric_values),
                    'std': statistics.stdev(metric_values) if len(metric_values) > 1 else 0.0,
                    'min': min(metric_values),
                    'max': max(metric_values),
                    'median': statistics.median(metric_values),
                    'count': len(metric_values)
                }

        return stats

    def detect_threshold_effects(
        self,
        parameter_name: str,
        metric_name: str = 'crash_rate',
        threshold_change: float = 0.5
    ) -> List[Tuple[Any, Any, float]]:
        """
        Detect threshold effects (sudden changes in metric)

        Args:
            parameter_name: Name of parameter to analyze
            metric_name: Metric to check for threshold effects
            threshold_change: Minimum relative change to count as threshold (0.5 = 50%)

        Returns:
            List of (param_value_before, param_value_after, change_magnitude)
        """
        stats = self.compute_parameter_statistics(parameter_name, metric_name)

        # Sort by parameter value
        sorted_params = sorted(stats.keys())

        thresholds = []
        for i in range(len(sorted_params) - 1):
            curr_param = sorted_params[i]
            next_param = sorted_params[i + 1]

            curr_mean = stats[curr_param]['mean']
            next_mean = stats[next_param]['mean']

            # Calculate relative change
            if curr_mean > 0:
                relative_change = abs((next_mean - curr_mean) / curr_mean)

                if relative_change >= threshold_change:
                    thresholds.append((curr_param, next_param, relative_change))

        return thresholds

    def generate_comparison_table(
        self,
        parameter_name: str,
        metrics: List[str] = None
    ) -> str:
        """
        Generate comparison table for a parameter

        Args:
            parameter_name: Name of parameter to compare
            metrics: List of metric names to include (default: all)

        Returns:
            Formatted table string
        """
        if metrics is None:
            metrics = ['crash_rate', 'total_cycles', 'total_crashes', 'messages_per_cycle']

        # Get statistics for each metric
        all_stats = {
            metric: self.compute_parameter_statistics(parameter_name, metric)
            for metric in metrics
        }

        # Get sorted parameter values
        param_values = sorted(list(all_stats[metrics[0]].keys()))

        # Build table
        table = []

        # Header
        header = [parameter_name] + [f"{m}_mean" for m in metrics] + [f"{m}_std" for m in metrics]
        table.append(" | ".join(f"{h:>15}" for h in header))
        table.append("-" * (16 * len(header) + (len(header) - 1) * 3))

        # Rows
        for param_value in param_values:
            row = [str(param_value)]

            # Add means
            for metric in metrics:
                mean_val = all_stats[metric][param_value]['mean']
                row.append(f"{mean_val:.4f}")

            # Add stds
            for metric in metrics:
                std_val = all_stats[metric][param_value]['std']
                row.append(f"{std_val:.4f}")

            table.append(" | ".join(f"{val:>15}" for val in row))

        return "\n".join(table)

    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report"""
        lines = []

        lines.append("=" * 80)
        lines.append(f"SWEEP ANALYSIS REPORT: {self.sweep_id}")
        lines.append("=" * 80)
        lines.append("")

        # Basic statistics
        lines.append("BASIC STATISTICS")
        lines.append("-" * 80)
        lines.append(f"Total experiments: {len(self.metrics)}")
        lines.append(f"Completed: {sum(1 for m in self.metrics if m.status == 'completed')}")
        lines.append(f"Failed: {sum(1 for m in self.metrics if m.status == 'failed')}")
        lines.append(f"Timeout: {sum(1 for m in self.metrics if m.status == 'timeout')}")
        lines.append("")

        # Sweep parameters
        lines.append("SWEEP PARAMETERS")
        lines.append("-" * 80)
        for param, values in self.sweep_config.get('sweep_params', {}).items():
            lines.append(f"{param}: {len(values)} values")
        lines.append("")

        # Optimal parameters
        lines.append("OPTIMAL PARAMETERS")
        lines.append("-" * 80)

        for metric in ['crash_rate', 'total_cycles']:
            best_params, best_value = self.find_optimal_parameters(metric, minimize=(metric == 'crash_rate'))
            lines.append(f"Best {metric}: {best_value:.4f}")
            lines.append(f"  Parameters: {best_params}")
            lines.append("")

        # Parameter comparisons
        lines.append("PARAMETER COMPARISONS")
        lines.append("-" * 80)

        for param_name in self.sweep_config.get('sweep_params', {}).keys():
            lines.append(f"\nParameter: {param_name}")
            lines.append(self.generate_comparison_table(param_name))
            lines.append("")

        # Threshold effects
        lines.append("THRESHOLD EFFECTS")
        lines.append("-" * 80)

        for param_name in self.sweep_config.get('sweep_params', {}).keys():
            thresholds = self.detect_threshold_effects(param_name, 'crash_rate')
            if thresholds:
                lines.append(f"\n{param_name} (crash_rate):")
                for before, after, change in thresholds:
                    lines.append(f"  {before} -> {after}: {change:.1%} change")
            else:
                lines.append(f"\n{param_name}: No significant thresholds detected")

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def export_for_plotting(self, output_path: str):
        """
        Export data in format suitable for plotting

        Args:
            output_path: Path to save plot data JSON
        """
        plot_data = {
            'sweep_id': self.sweep_id,
            'parameters': list(self.sweep_config.get('sweep_params', {}).keys()),
            'metrics': ['crash_rate', 'total_cycles', 'total_crashes', 'messages_per_cycle'],
            'data': []
        }

        for m in self.metrics:
            if m.status == 'completed':
                plot_data['data'].append({
                    'experiment_id': m.experiment_id,
                    'parameters': m.parameters,
                    'crash_rate': m.crash_rate,
                    'total_cycles': m.total_cycles,
                    'total_crashes': m.total_crashes,
                    'messages_per_cycle': m.messages_per_cycle,
                    'duration_seconds': m.duration_seconds
                })

        with open(output_path, 'w') as f:
            json.dump(plot_data, f, indent=2)

        print(f"[Analysis] Plot data exported to: {output_path}")

    def compare_self_report_responses(
        self,
        question_text_pattern: str,
        parameter_name: str
    ) -> Dict[Any, List[str]]:
        """
        Compare self-report responses across parameter values

        Args:
            question_text_pattern: Pattern to match questions (substring search)
            parameter_name: Parameter to group by

        Returns:
            Dict mapping parameter_value -> list of responses
        """
        comparison = defaultdict(list)

        for m in self.metrics:
            if m.status == 'completed':
                param_value = m.parameters.get(parameter_name)

                # Get self-reports for this experiment
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT question, response
                    FROM self_reports
                    WHERE experiment_id = ?
                    AND question LIKE ?
                    ORDER BY cycle_number
                """, (m.experiment_id, f"%{question_text_pattern}%"))

                responses = cursor.fetchall()
                conn.close()

                for question, response in responses:
                    comparison[param_value].append(response)

        return dict(comparison)

    def analyze_belief_evolution(
        self,
        parameter_name: str,
        belief_keyword: str
    ) -> Dict[Any, Dict[str, int]]:
        """
        Analyze how beliefs evolve across parameter values

        Args:
            parameter_name: Parameter to group by
            belief_keyword: Keyword to search for in responses (e.g., "trust", "confident")

        Returns:
            Dict mapping parameter_value -> {mention_count, total_responses}
        """
        belief_stats = defaultdict(lambda: {'mentions': 0, 'total': 0})

        for m in self.metrics:
            if m.status == 'completed':
                param_value = m.parameters.get(parameter_name)

                # Get all self-reports
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT response
                    FROM self_reports
                    WHERE experiment_id = ?
                """, (m.experiment_id,))

                responses = cursor.fetchall()
                conn.close()

                for (response,) in responses:
                    belief_stats[param_value]['total'] += 1
                    if belief_keyword.lower() in response.lower():
                        belief_stats[param_value]['mentions'] += 1

        # Calculate mention rates
        result = {}
        for param_value, stats in belief_stats.items():
            mention_rate = stats['mentions'] / stats['total'] if stats['total'] > 0 else 0.0
            result[param_value] = {
                'mention_count': stats['mentions'],
                'total_responses': stats['total'],
                'mention_rate': mention_rate
            }

        return result


def create_visualization_script(sweep_id: str, output_path: str = "scripts/plot_sweep.py"):
    """
    Generate a matplotlib visualization script for the sweep

    Args:
        sweep_id: Sweep to visualize
        output_path: Where to save the script
    """
    script_content = f'''#!/usr/bin/env python3
"""
Auto-generated visualization script for sweep: {sweep_id}
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load plot data
with open("logs/sweeps/{sweep_id}/plot_data.json", 'r') as f:
    data = json.load(f)

# Extract parameters and metrics
parameters = data['parameters']
metrics = data['metrics']

# Create subplots for each parameter-metric combination
n_params = len(parameters)
n_metrics = len(metrics)

fig, axes = plt.subplots(n_metrics, n_params, figsize=(5*n_params, 4*n_metrics))

if n_params == 1:
    axes = axes.reshape(-1, 1)
if n_metrics == 1:
    axes = axes.reshape(1, -1)

# Plot each combination
for i, metric in enumerate(metrics):
    for j, param in enumerate(parameters):
        ax = axes[i, j]

        # Extract data points
        x_values = []
        y_values = []

        for exp in data['data']:
            x_val = exp['parameters'].get(param)
            y_val = exp.get(metric)

            if x_val is not None and y_val is not None:
                x_values.append(x_val)
                y_values.append(y_val)

        # Sort by x for line plot
        sorted_pairs = sorted(zip(x_values, y_values))
        x_sorted = [x for x, y in sorted_pairs]
        y_sorted = [y for x, y in sorted_pairs]

        # Plot
        ax.plot(x_sorted, y_sorted, 'o-', linewidth=2, markersize=6)
        ax.set_xlabel(param)
        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{{metric}} vs {{param}}")

plt.tight_layout()
plt.savefig("logs/sweeps/{sweep_id}/sweep_visualization.png", dpi=150)
print(f"Visualization saved to: logs/sweeps/{sweep_id}/sweep_visualization.png")
plt.show()
'''

    with open(output_path, 'w') as f:
        f.write(script_content)

    print(f"[Analysis] Visualization script created: {output_path}")
    print(f"[Analysis] Run: python {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze parameter sweep results")
    parser.add_argument('sweep_id', help='Sweep ID to analyze')
    parser.add_argument('--sweep-dir', default='logs/sweeps', help='Sweep directory')
    parser.add_argument('--output', help='Output path for report (default: stdout)')
    parser.add_argument('--plot', action='store_true', help='Generate plot data')
    parser.add_argument('--viz-script', action='store_true', help='Generate visualization script')

    args = parser.parse_args()

    # Create analyzer
    analyzer = SweepAnalyzer(args.sweep_id, args.sweep_dir)

    # Generate report
    report = analyzer.generate_summary_report()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)

    # Export plot data if requested
    if args.plot:
        plot_path = analyzer.sweep_path / "plot_data.json"
        analyzer.export_for_plotting(str(plot_path))

    # Generate visualization script if requested
    if args.viz_script:
        create_visualization_script(args.sweep_id)
