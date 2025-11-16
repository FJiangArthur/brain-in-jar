#!/usr/bin/env python3
"""
Simple demo of the profiling infrastructure

Demonstrates basic usage of ExperimentProfiler, PerformanceMonitor, and ExperimentOptimizer
"""

import sys
import time
import random
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infra.profiler import ExperimentProfiler
from src.infra.performance_monitor import PerformanceMonitor
from src.infra.optimizer import ExperimentOptimizer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress


def simulate_experiment():
    """Simulate a simple experiment with profiling"""

    console = Console()

    console.print(Panel.fit(
        "[bold cyan]Profiling Demo[/bold cyan]\n\n"
        "Simulating a 5-cycle experiment with profiling",
        title="🔬 Performance Profiling Demo"
    ))

    # Initialize profiler
    profiler = ExperimentProfiler(
        experiment_id="demo_001",
        experiment_name="Profiling Demo",
        mode="amnesiac_loop",
        enable_jetson_profiling=False  # Set True on Jetson
    )

    # Initialize performance monitor
    monitor = PerformanceMonitor(
        sample_interval=0.5,
        enable_alerts=True,
        enable_jetson_monitoring=False
    )

    # Set thresholds
    monitor.set_threshold('memory_percent', 80, severity='warning')

    # Alert handler
    def on_alert(alert):
        console.print(f"[yellow]⚠️  {alert.message}[/yellow]")

    monitor.on_alert(on_alert)

    # Start profiling
    console.print("\n[green]Starting profiler and monitor...[/green]")
    profiler.start_experiment()
    monitor.start()

    # Simulate cycles
    num_cycles = 5

    with Progress() as progress:
        task = progress.add_task("[cyan]Running cycles...", total=num_cycles)

        for cycle in range(num_cycles):
            console.print(f"\n[bold]Cycle {cycle}[/bold]")

            # Start cycle profiling
            profiler.start_cycle(cycle)

            # Simulate mode processing
            with profiler.time("mode_memory_processing"):
                time.sleep(random.uniform(0.05, 0.15))

            # Simulate system prompt generation
            with profiler.time("mode_system_prompt"):
                time.sleep(random.uniform(0.01, 0.05))

            # Simulate LLM inference
            tokens_generated = random.randint(120, 200)
            inference_time = tokens_generated / random.uniform(12, 18)  # Variable speed

            with profiler.time("llm_inference", tokens=tokens_generated):
                time.sleep(inference_time)

            console.print(f"  Generated {tokens_generated} tokens in {inference_time:.2f}s")

            # Simulate database writes
            with profiler.time("database_write"):
                time.sleep(random.uniform(0.05, 0.15))

            # Simulate crash 30% of the time
            crashed = random.random() < 0.3
            crash_reason = "Simulated OOM" if crashed else None

            if crashed:
                console.print("  [red]💀 Crashed![/red]")

            # End cycle
            profiler.end_cycle(crashed=crashed, crash_reason=crash_reason)

            progress.update(task, advance=1)

    # Stop profiling
    console.print("\n[green]Stopping profiler and monitor...[/green]")
    monitor.stop()
    profiler.end_experiment()

    # Get results
    profile = profiler.get_profile()
    perf_summary = monitor.get_summary_stats()

    # Display results
    console.print(Panel.fit(
        f"[bold green]Profiling Complete[/bold green]\n\n"
        f"[yellow]Total Duration:[/yellow] {profile.total_duration:.2f}s\n"
        f"[yellow]Total Cycles:[/yellow] {len(profile.cycles)}\n"
        f"[yellow]Total Tokens:[/yellow] {profile.total_tokens}\n"
        f"[yellow]Avg Tokens/Sec:[/yellow] {profile.avg_tokens_per_second:.2f}\n"
        f"[yellow]Peak Memory:[/yellow] {profile.peak_memory_mb:.0f} MB\n"
        f"[yellow]Bottlenecks Found:[/yellow] {len(profile.bottlenecks)}",
        title="📊 Results"
    ))

    # Show bottlenecks
    if profile.bottlenecks:
        console.print("\n[bold red]Bottlenecks:[/bold red]")
        for bottleneck in profile.bottlenecks:
            console.print(f"  • [{bottleneck['severity']}] {bottleneck['description']}")

    # Show recommendations
    if profile.recommendations:
        console.print("\n[bold cyan]Recommendations:[/bold cyan]")
        for i, rec in enumerate(profile.recommendations[:5], 1):
            console.print(f"  {i}. {rec}")

    # Export profile
    output_path = "logs/profiles/demo_profile.json"
    profiler.export_json(output_path)
    console.print(f"\n[green]✓ Profile exported to:[/green] {output_path}")

    # Run optimizer
    console.print("\n[cyan]Running optimizer...[/cyan]")
    optimizer = ExperimentOptimizer()
    optimizer.load_profile_from_file(output_path)

    recommendations = optimizer.generate_recommendations()

    if recommendations:
        console.print(f"\n[bold]Top Optimization Recommendations:[/bold]")
        for rec in recommendations[:3]:
            priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'dim'}
            color = priority_color.get(rec.priority, 'white')

            console.print(Panel(
                f"[{color}]{rec.title}[/{color}]\n\n"
                f"{rec.description}\n\n"
                f"Current: {rec.current_value}\n"
                f"Recommended: {rec.recommended_value}\n\n"
                f"Expected Impact: {rec.expected_impact}",
                border_style=color
            ))

    console.print("\n[bold green]✅ Demo complete![/bold green]\n")


if __name__ == "__main__":
    simulate_experiment()
