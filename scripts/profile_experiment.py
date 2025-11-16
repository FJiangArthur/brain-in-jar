#!/usr/bin/env python3
"""
CLI Profiler for Season 3 Experiments

Runs an experiment with full performance profiling and generates
comprehensive performance reports.

Usage:
    python scripts/profile_experiment.py \\
        --config experiments/examples/amnesiac_total.json \\
        --profile-output logs/profiles/amnesiac_profile.json \\
        --report-output logs/reports/amnesiac_report.html \\
        --enable-jetson
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.schema import ExperimentConfig
from src.runner.experiment_runner import ExperimentRunner
from src.infra.profiler import ExperimentProfiler
from src.infra.performance_monitor import PerformanceMonitor
from src.infra.optimizer import ExperimentOptimizer


class ProfiledExperimentRunner(ExperimentRunner):
    """
    Experiment runner with profiling instrumentation
    """

    def __init__(self, config: ExperimentConfig, db_path: str,
                 profiler: ExperimentProfiler,
                 perf_monitor: PerformanceMonitor,
                 console: Console):
        super().__init__(config, db_path)
        self.profiler = profiler
        self.perf_monitor = perf_monitor
        self.console = console

    def start(self):
        """Start experiment with profiling"""
        # Start profiler and monitor
        self.profiler.start_experiment()
        self.perf_monitor.start()

        # Run experiment
        result = super().start()

        # Stop profiling
        self.perf_monitor.stop()
        self.profiler.end_experiment()

        return result

    def _run_experiment_loop(self):
        """Override to add profiling hooks"""
        while self.running:
            if self.config.max_cycles and self.state.cycle_number >= self.config.max_cycles:
                self.console.print(f"\n[green]Experiment complete: Reached max cycles ({self.config.max_cycles})[/green]")
                break

            cycle_num = self.state.cycle_number
            self.console.print(f"\n[bold cyan]━━━ Cycle {cycle_num} ━━━[/bold cyan]")

            # Profile cycle
            self.profiler.start_cycle(cycle_num)

            # Time cycle operations
            with self.profiler.time("cycle_start"):
                cycle_id = self.db.start_cycle(self.config.experiment_id, cycle_num)

            if self.web_monitor:
                self.web_monitor.emit_cycle_start(self.config.experiment_id, cycle_num)

            # Profile interventions
            with self.profiler.time("interventions"):
                self._apply_scheduled_interventions(cycle_num)

            # Profile cycle execution
            crashed = False
            crash_reason = None

            try:
                with self.profiler.time("cycle_execution"):
                    self._run_cycle_simulation()
            except MemoryError as e:
                crashed = True
                crash_reason = "Out of Memory"
                self._handle_crash(crash_reason, cycle_num)
            except Exception as e:
                crashed = True
                crash_reason = str(e)
                self._handle_crash(crash_reason, cycle_num)

            # Profile self-report
            if self._should_collect_self_report(cycle_num):
                with self.profiler.time("self_report"):
                    self._collect_self_report("scheduled")

            # End cycle profiling
            self.profiler.end_cycle(crashed=crashed, crash_reason=crash_reason)

            time.sleep(1)

    def _run_cycle_simulation(self):
        """Override to add LLM profiling"""
        self.console.print("[dim]Simulating cycle... (In production: would run LLM here)[/dim]")

        # Profile memory processing
        with self.profiler.time("mode_memory_processing"):
            processed_memory = self.mode.process_memory(
                self.state.conversation_history,
                self.state
            )

        # Profile system prompt generation
        with self.profiler.time("mode_system_prompt"):
            system_prompt = self.mode.generate_system_prompt(self.state)

        self.console.print(f"\n[yellow]System Prompt Preview:[/yellow]")
        self.console.print(Panel(system_prompt[:300] + "...", border_style="dim"))

        # Simulate LLM inference with timing
        with self.profiler.time("llm_inference", tokens=150):
            time.sleep(0.5)  # Simulate inference time
            self._simulate_conversation()

        # Simulate crash with some probability
        import random
        if random.random() < 0.3:
            raise MemoryError("Simulated OOM")


def generate_html_report(profile_data: dict, perf_summary: dict,
                        recommendations: list, output_path: str):
    """Generate HTML performance report"""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Experiment Performance Report</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-left: 4px solid #764ba2;
            padding-left: 10px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}
        .metric-unit {{
            font-size: 14px;
            color: #888;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .priority-high {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .priority-medium {{
            color: #f39c12;
        }}
        .priority-low {{
            color: #95a5a6;
        }}
        .chart {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .bottleneck {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .recommendation {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .timestamp {{
            color: #888;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #888;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>🧠 Experiment Performance Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>📊 Experiment Overview</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Experiment</div>
                <div class="metric-value" style="font-size: 20px;">{profile_data['experiment_name']}</div>
                <div class="metric-unit">Mode: {profile_data['mode']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Duration</div>
                <div class="metric-value">{profile_data.get('total_duration', 0):.1f}</div>
                <div class="metric-unit">seconds</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cycles</div>
                <div class="metric-value">{profile_data['aggregate_metrics']['total_cycles']}</div>
                <div class="metric-unit">completed</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Tokens/Sec</div>
                <div class="metric-value">{profile_data['aggregate_metrics']['avg_tokens_per_second']:.2f}</div>
                <div class="metric-unit">tok/s</div>
            </div>
        </div>

        <h2>⚡ Performance Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total LLM Time</div>
                <div class="metric-value">{profile_data['aggregate_metrics']['total_llm_time']:.2f}</div>
                <div class="metric-unit">seconds</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total DB Time</div>
                <div class="metric-value">{profile_data['aggregate_metrics']['total_db_time']:.2f}</div>
                <div class="metric-unit">seconds</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Peak Memory</div>
                <div class="metric-value">{profile_data['aggregate_metrics']['peak_memory_mb']:.0f}</div>
                <div class="metric-unit">MB</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Memory</div>
                <div class="metric-value">{profile_data['aggregate_metrics']['avg_memory_mb']:.0f}</div>
                <div class="metric-unit">MB</div>
            </div>
        </div>

        <h2>🔥 Bottlenecks Identified</h2>
        {''.join(f'''
        <div class="bottleneck">
            <strong>{b['type'].replace('_', ' ').title()}</strong> -
            <span class="priority-{b['severity']}">{b['severity'].upper()}</span>
            <p>{b['description']}</p>
        </div>
        ''' for b in profile_data.get('bottlenecks', []))}

        <h2>💡 Optimization Recommendations</h2>
        {''.join(f'''
        <div class="recommendation">
            <strong class="priority-{r['priority']}">[{r['priority'].upper()}]</strong>
            <strong>{r['title']}</strong>
            <p>{r['description']}</p>
            <p><em>Current: {r['current_value']} → Recommended: {r['recommended_value']}</em></p>
            <p>Expected Impact: {r['expected_impact']}</p>
        </div>
        ''' for r in recommendations)}

        <h2>📈 Cycle Performance</h2>
        <div class="chart">
            <canvas id="cycleChart"></canvas>
        </div>

        <h2>🖥️ System Information</h2>
        <table>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
            {''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in profile_data.get('system_info', {}).items())}
        </table>

        <div class="footer">
            <p>Brain-in-Jar Season 3: Digital Phenomenology Lab</p>
            <p>Performance Profiling System v1.0</p>
        </div>
    </div>

    <script>
        // Cycle performance chart
        const cycles = {[c['cycle_number'] for c in profile_data.get('cycles', [])]};
        const durations = {[c.get('duration', 0) for c in profile_data.get('cycles', [])]};
        const tokens = {[c.get('llm_metrics', {}).get('tokens_per_second', 0) for c in profile_data.get('cycles', [])]};

        const ctx = document.getElementById('cycleChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: cycles,
                datasets: [{{
                    label: 'Cycle Duration (s)',
                    data: durations,
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    yAxisID: 'y',
                }}, {{
                    label: 'Tokens/Second',
                    data: tokens,
                    borderColor: 'rgb(118, 75, 162)',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    yAxisID: 'y1',
                }}]
            }},
            options: {{
                responsive: true,
                interaction: {{
                    mode: 'index',
                    intersect: false,
                }},
                scales: {{
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {{
                            display: true,
                            text: 'Duration (seconds)'
                        }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {{
                            display: true,
                            text: 'Tokens/Second'
                        }},
                        grid: {{
                            drawOnChartArea: false,
                        }},
                    }},
                }}
            }},
        }});
    </script>
</body>
</html>
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Profile Season 3 Experiment Performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic profiling
  python scripts/profile_experiment.py \\
      --config experiments/examples/amnesiac_total.json

  # Full profiling with report
  python scripts/profile_experiment.py \\
      --config experiments/examples/amnesiac_total.json \\
      --profile-output logs/profiles/amnesiac.json \\
      --report-output logs/reports/amnesiac.html

  # Jetson profiling with optimization
  python scripts/profile_experiment.py \\
      --config experiments/examples/amnesiac_total.json \\
      --enable-jetson \\
      --optimize-config \\
      --optimized-config-output experiments/optimized/amnesiac_optimized.json
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to experiment configuration JSON file'
    )

    parser.add_argument(
        '--profile-output',
        default='logs/profiles/experiment_profile.json',
        help='Path to save profile JSON (default: logs/profiles/experiment_profile.json)'
    )

    parser.add_argument(
        '--report-output',
        default='logs/reports/performance_report.html',
        help='Path to save HTML report (default: logs/reports/performance_report.html)'
    )

    parser.add_argument(
        '--db',
        default='logs/experiments.db',
        help='Path to experiment database (default: logs/experiments.db)'
    )

    parser.add_argument(
        '--enable-jetson',
        action='store_true',
        help='Enable Jetson-specific GPU profiling'
    )

    parser.add_argument(
        '--optimize-config',
        action='store_true',
        help='Generate optimized configuration based on profile'
    )

    parser.add_argument(
        '--optimized-config-output',
        help='Path to save optimized config (if --optimize-config enabled)'
    )

    parser.add_argument(
        '--sample-interval',
        type=float,
        default=1.0,
        help='Performance monitoring sample interval in seconds (default: 1.0)'
    )

    args = parser.parse_args()

    console = Console()

    # Load config
    try:
        config = ExperimentConfig.from_json(args.config)
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        return 1

    console.print(Panel.fit(
        f"[bold cyan]🔬 Experiment Profiler[/bold cyan]\n\n"
        f"[yellow]Experiment:[/yellow] {config.name}\n"
        f"[yellow]Mode:[/yellow] {config.mode}\n"
        f"[yellow]Jetson Profiling:[/yellow] {'Enabled' if args.enable_jetson else 'Disabled'}\n"
        f"[yellow]Profile Output:[/yellow] {args.profile_output}\n"
        f"[yellow]Report Output:[/yellow] {args.report_output}",
        title="Performance Profiling Session"
    ))

    # Create profiler
    profiler = ExperimentProfiler(
        config.experiment_id,
        config.name,
        config.mode,
        enable_jetson_profiling=args.enable_jetson
    )

    # Create performance monitor
    perf_monitor = PerformanceMonitor(
        sample_interval=args.sample_interval,
        enable_alerts=True,
        enable_jetson_monitoring=args.enable_jetson
    )

    # Set alert thresholds
    perf_monitor.set_threshold('memory_percent', 85, severity='warning')
    perf_monitor.set_threshold('memory_percent', 95, severity='critical')

    if args.enable_jetson:
        perf_monitor.set_threshold('cpu_temp_c', 75, severity='warning')
        perf_monitor.set_threshold('cpu_temp_c', 85, severity='critical')
        perf_monitor.set_threshold('gpu_temp_c', 75, severity='warning')

    # Alert handler
    def on_alert(alert):
        severity_color = {'warning': 'yellow', 'critical': 'red'}
        console.print(f"[{severity_color[alert.severity]}]⚠️  ALERT: {alert.message}[/{severity_color[alert.severity]}]")

    perf_monitor.on_alert(on_alert)

    # Create profiled runner
    runner = ProfiledExperimentRunner(
        config,
        db_path=args.db,
        profiler=profiler,
        perf_monitor=perf_monitor,
        console=console
    )

    # Run experiment
    console.print("\n[bold green]Starting profiled experiment...[/bold green]\n")

    try:
        runner.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Profiling interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Profiling error: {e}[/red]")
        import traceback
        traceback.print_exc()

    # Get results
    profile = profiler.get_profile()
    perf_summary = perf_monitor.get_summary_stats()

    # Export profile
    console.print(f"\n[cyan]Exporting profile to {args.profile_output}...[/cyan]")
    profiler.export_json(args.profile_output)

    # Generate recommendations
    console.print("[cyan]Generating optimization recommendations...[/cyan]")
    optimizer = ExperimentOptimizer()
    optimizer.load_profile_from_file(args.profile_output)
    recommendations = optimizer.generate_recommendations()

    # Convert recommendations to dict
    rec_dicts = [
        {
            'category': r.category,
            'priority': r.priority,
            'title': r.title,
            'description': r.description,
            'current_value': str(r.current_value),
            'recommended_value': str(r.recommended_value),
            'expected_impact': r.expected_impact,
        }
        for r in recommendations
    ]

    # Generate HTML report
    console.print(f"[cyan]Generating HTML report to {args.report_output}...[/cyan]")

    # Load profile data for report
    import json
    with open(args.profile_output, 'r') as f:
        profile_data = json.load(f)

    generate_html_report(profile_data, perf_summary, rec_dicts, args.report_output)

    # Display summary
    console.print(Panel.fit(
        f"[bold green]Profiling Complete[/bold green]\n\n"
        f"[yellow]Cycles Profiled:[/yellow] {len(profile.cycles)}\n"
        f"[yellow]Total Duration:[/yellow] {profile.total_duration:.2f}s\n"
        f"[yellow]Avg Tokens/Sec:[/yellow] {profile.avg_tokens_per_second:.2f}\n"
        f"[yellow]Peak Memory:[/yellow] {profile.peak_memory_mb:.0f} MB\n"
        f"[yellow]Bottlenecks Found:[/yellow] {len(profile.bottlenecks)}\n"
        f"[yellow]Recommendations:[/yellow] {len(recommendations)}\n\n"
        f"[cyan]Profile:[/cyan] {args.profile_output}\n"
        f"[cyan]Report:[/cyan] {args.report_output}",
        title="📊 Profiling Summary"
    ))

    # Show high priority recommendations
    high_priority = [r for r in recommendations if r.priority == 'high']
    if high_priority:
        console.print("\n[bold red]High Priority Recommendations:[/bold red]")
        for rec in high_priority:
            console.print(f"  • {rec.title}")

    # Optimize config if requested
    if args.optimize_config:
        console.print("\n[cyan]Generating optimized configuration...[/cyan]")

        # Load original config
        with open(args.config, 'r') as f:
            original_config = json.load(f)

        optimized_config = optimizer.apply_recommendations(
            original_config,
            recommendations,
            apply_high_only=True
        )

        # Save optimized config
        output_path = args.optimized_config_output or args.config.replace('.json', '_optimized.json')
        with open(output_path, 'w') as f:
            json.dump(optimized_config, f, indent=2)

        console.print(f"[green]✓ Optimized config saved to:[/green] {output_path}")

    console.print(f"\n[bold green]✅ Profiling session complete![/bold green]")
    console.print(f"[dim]Open {args.report_output} in a browser to view the full report.[/dim]\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
