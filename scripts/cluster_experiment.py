#!/usr/bin/env python3
"""
Multi-Node Cluster Experiment Runner

Orchestrates experiments across Jetson Orin + Raspberry Pi cluster.

Usage:
    # Run split brain experiment with manual placement
    python scripts/cluster_experiment.py \\
        --config experiments/examples/split_brain_001_brain_A.json \\
        --config experiments/examples/split_brain_001_brain_B.json \\
        --placement "split_brain_001_brain_A:jetson,split_brain_001_brain_B:rpi1"

    # Run hive cluster experiment with automatic placement
    python scripts/cluster_experiment.py \\
        --config experiments/examples/hive_cluster_4minds.json \\
        --auto-place

    # Validate cluster configuration
    python scripts/cluster_experiment.py --validate-config

    # Health check all nodes
    python scripts/cluster_experiment.py --health-check

    # Deploy code to all nodes
    python scripts/cluster_experiment.py --deploy-all
"""

import argparse
import asyncio
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infra.cluster_orchestrator import (
    ClusterOrchestrator, ExperimentInstance, NodeStatus
)
from src.infra.remote_runner import RemoteRunner


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class ClusterExperimentRunner:
    """
    Orchestrates multi-node experiment execution

    Workflow:
    1. Load cluster config
    2. Validate node connectivity
    3. Place experiment instances
    4. Deploy code to remote nodes
    5. Start experiments
    6. Monitor and stream logs
    7. Aggregate results
    """

    def __init__(self, cluster_config_path: str = "src/infra/cluster_config.yaml"):
        self.orchestrator = ClusterOrchestrator(cluster_config_path)
        self.runners: Dict[str, RemoteRunner] = {}
        self.experiment_configs: List[str] = []

    async def validate_config(self) -> bool:
        """Validate cluster configuration"""
        console.print(Panel.fit(
            "[bold cyan]Validating Cluster Configuration[/bold cyan]",
            border_style="cyan"
        ))

        # Check nodes
        console.print(f"\n[yellow]Nodes:[/yellow] {len(self.orchestrator.nodes)}")

        for node in self.orchestrator.nodes:
            console.print(
                f"  [cyan]•[/cyan] {node.name}: "
                f"{node.host} "
                f"({node.ram_gb}GB RAM, "
                f"{'GPU' if node.gpu else 'CPU'}, "
                f"max {node.max_instances} instances)"
            )

        console.print(f"\n[green]✓[/green] Configuration loaded successfully\n")
        return True

    async def health_check(self) -> Dict[str, NodeStatus]:
        """Run health checks on all nodes"""
        console.print(Panel.fit(
            "[bold cyan]Cluster Health Check[/bold cyan]",
            border_style="cyan"
        ))

        await self.orchestrator.health_check_all()

        # Display results in table
        table = Table(title="Node Health Status")
        table.add_column("Node", style="cyan")
        table.add_column("Host", style="white")
        table.add_column("Status", style="green")
        table.add_column("RAM (GB)", justify="right")
        table.add_column("GPU", justify="center")
        table.add_column("Max Instances", justify="right")

        for node in self.orchestrator.nodes:
            status_style = {
                NodeStatus.HEALTHY: "green",
                NodeStatus.DEGRADED: "yellow",
                NodeStatus.UNAVAILABLE: "red",
                NodeStatus.MAINTENANCE: "dim"
            }.get(node.status, "white")

            table.add_row(
                node.name,
                node.host,
                f"[{status_style}]{node.status.value}[/{status_style}]",
                f"{node.ram_gb}",
                "✓" if node.gpu else "✗",
                f"{node.max_instances}"
            )

        console.print(table)

        # Summary
        healthy_count = sum(1 for n in self.orchestrator.nodes if n.status == NodeStatus.HEALTHY)
        total_count = len(self.orchestrator.nodes)

        if healthy_count == total_count:
            console.print(f"\n[green]✓[/green] All {total_count} nodes are healthy\n")
        else:
            console.print(
                f"\n[yellow]⚠[/yellow] {healthy_count}/{total_count} nodes are healthy\n"
            )

        return {node.name: node.status for node in self.orchestrator.nodes}

    async def deploy_all(self, local_code_dir: str = "."):
        """Deploy code to all remote nodes"""
        console.print(Panel.fit(
            "[bold cyan]Deploying Code to All Nodes[/bold cyan]",
            border_style="cyan"
        ))

        local_path = Path(local_code_dir).resolve()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for node in self.orchestrator.nodes:
                if node.is_localhost:
                    continue

                task = progress.add_task(f"Deploying to {node.name}...", total=None)

                runner = RemoteRunner(
                    node.host,
                    node.ssh_user,
                    node.ssh_port,
                    node.ssh_key_path
                )

                try:
                    await runner.connect()

                    # Get remote work dir from config
                    remote_work_dir = f"/home/{node.ssh_user}/brain-in-jar"

                    # Deploy code
                    success = await runner.deploy_code(
                        str(local_path),
                        remote_work_dir,
                        exclude=[
                            '*.pyc',
                            '__pycache__',
                            '.git',
                            'logs/*',
                            'test_outputs/*',
                            '*.db',
                            'models/*'  # Don't sync large model files
                        ]
                    )

                    if success:
                        # Create necessary directories
                        await runner.execute_command(f"mkdir -p {remote_work_dir}/logs")
                        await runner.execute_command(f"mkdir -p {remote_work_dir}/models")

                        progress.update(task, description=f"[green]✓[/green] {node.name} deployed")
                    else:
                        progress.update(task, description=f"[red]✗[/red] {node.name} failed")

                    await runner.disconnect()

                except Exception as e:
                    progress.update(task, description=f"[red]✗[/red] {node.name}: {e}")
                    logger.error(f"Deployment to {node.name} failed: {e}")

        console.print("\n[green]✓[/green] Deployment complete\n")

    def add_experiment_config(self, config_path: str):
        """Add experiment configuration"""
        self.experiment_configs.append(config_path)

    def parse_placement_string(self, placement_str: str) -> Dict[str, str]:
        """
        Parse placement string into instance->node mapping

        Format: "instance1:node1,instance2:node2"

        Example: "split_brain_A:jetson,split_brain_B:rpi1"
        """
        placements = {}

        for pair in placement_str.split(','):
            pair = pair.strip()
            if ':' not in pair:
                console.print(f"[red]Invalid placement format:[/red] {pair}")
                continue

            instance_id, node_name = pair.split(':', 1)
            placements[instance_id.strip()] = node_name.strip()

        return placements

    async def run_experiments(self, manual_placement: Optional[Dict[str, str]] = None):
        """
        Run all configured experiments

        Args:
            manual_placement: Optional manual instance->node mapping
        """
        console.print(Panel.fit(
            "[bold cyan]Starting Multi-Node Experiments[/bold cyan]",
            border_style="cyan"
        ))

        # Add instances to orchestrator
        for config_path in self.experiment_configs:
            with open(config_path) as f:
                config = json.load(f)

            instance_id = config['experiment_id']

            # Extract resource requirements
            ram_gb = config['resource_constraints']['ram_limit_gb']
            gpu_layers = config['resource_constraints'].get('gpu_layers', 0)
            gpu_required = gpu_layers > 0

            # Estimate GPU memory (rough heuristic)
            gpu_memory_gb = 0.0
            if gpu_required:
                gpu_memory_gb = ram_gb  # Jetson uses unified memory

            instance = ExperimentInstance(
                instance_id=instance_id,
                experiment_config_path=config_path,
                ram_gb=ram_gb,
                gpu_required=gpu_required,
                gpu_memory_gb=gpu_memory_gb
            )

            # Apply manual placement if specified
            if manual_placement and instance_id in manual_placement:
                instance.preferred_node = manual_placement[instance_id]

            self.orchestrator.add_instance(instance)

        # Place instances
        console.print(f"\n[yellow]Placing {len(self.orchestrator.instances)} instances...[/yellow]")

        try:
            placements = self.orchestrator.place_all()
        except RuntimeError as e:
            console.print(f"\n[red]Placement failed:[/red] {e}\n")
            return

        # Display placement
        table = Table(title="Experiment Placement")
        table.add_column("Instance", style="cyan")
        table.add_column("Node", style="green")
        table.add_column("RAM (GB)", justify="right")
        table.add_column("GPU", justify="center")

        for instance in self.orchestrator.instances:
            table.add_row(
                instance.instance_id,
                instance.assigned_node or "UNASSIGNED",
                f"{instance.ram_gb}",
                "✓" if instance.gpu_required else "✗"
            )

        console.print(table)

        # Start experiments
        console.print("\n[yellow]Starting experiments...[/yellow]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for instance in self.orchestrator.instances:
                node_name = instance.assigned_node
                node = next(n for n in self.orchestrator.nodes if n.name == node_name)

                task = progress.add_task(
                    f"Starting {instance.instance_id} on {node_name}...",
                    total=None
                )

                try:
                    if node.is_localhost:
                        # Local execution
                        await self._start_local_experiment(instance)
                    else:
                        # Remote execution
                        await self._start_remote_experiment(instance, node)

                    progress.update(
                        task,
                        description=f"[green]✓[/green] {instance.instance_id} started on {node_name}"
                    )

                except Exception as e:
                    progress.update(
                        task,
                        description=f"[red]✗[/red] {instance.instance_id} failed: {e}"
                    )
                    logger.error(f"Failed to start {instance.instance_id}: {e}")

        console.print("\n[green]✓[/green] All experiments started\n")

        # Save cluster state
        state_path = f"logs/cluster/cluster_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path("logs/cluster").mkdir(parents=True, exist_ok=True)
        self.orchestrator.save_state(state_path)
        console.print(f"[dim]Cluster state saved to {state_path}[/dim]\n")

    async def _start_local_experiment(self, instance: ExperimentInstance):
        """Start experiment on localhost"""
        # Import here to avoid circular dependency
        from src.runner.experiment_runner import ExperimentRunner
        from experiments.schema import ExperimentConfig

        # Load config
        config = ExperimentConfig.from_json(instance.experiment_config_path)

        # Start in background (would need proper process management)
        # For now, just log
        logger.info(f"Would start local experiment: {instance.instance_id}")

    async def _start_remote_experiment(self, instance: ExperimentInstance, node):
        """Start experiment on remote node"""
        runner = RemoteRunner(
            node.host,
            node.ssh_user,
            node.ssh_port,
            node.ssh_key_path
        )

        await runner.connect()

        remote_work_dir = f"/home/{node.ssh_user}/brain-in-jar"

        # Upload config if needed
        await runner.put_file(
            instance.experiment_config_path,
            f"{remote_work_dir}/{instance.experiment_config_path}"
        )

        # Start experiment
        await runner.start_experiment(
            instance.experiment_config_path,
            remote_work_dir,
            instance.instance_id
        )

        # Store runner for monitoring
        self.runners[instance.instance_id] = runner

    async def monitor_all(self, duration_seconds: int = 60):
        """Monitor all running experiments"""
        console.print(Panel.fit(
            f"[bold cyan]Monitoring Experiments ({duration_seconds}s)[/bold cyan]",
            border_style="cyan"
        ))

        for _ in range(duration_seconds):
            await asyncio.sleep(1)

            # Check status of each instance
            for instance_id, runner in self.runners.items():
                status = await runner.monitor_experiment(instance_id)
                if not status['running']:
                    console.print(
                        f"[yellow]{instance_id}:[/yellow] "
                        f"Exited with code {status['exit_code']}"
                    )

    async def cleanup(self):
        """Cleanup: disconnect all runners"""
        for runner in self.runners.values():
            await runner.disconnect()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Node Cluster Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Configuration
    parser.add_argument(
        '--cluster-config',
        default='src/infra/cluster_config.yaml',
        help='Path to cluster configuration YAML'
    )

    # Experiment configs
    parser.add_argument(
        '--config',
        action='append',
        help='Experiment configuration(s) to run (can specify multiple)'
    )

    # Placement
    parser.add_argument(
        '--placement',
        help='Manual placement string: "instance1:node1,instance2:node2"'
    )

    parser.add_argument(
        '--auto-place',
        action='store_true',
        help='Use automatic placement algorithm'
    )

    # Operations
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='Validate cluster configuration and exit'
    )

    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Run health check on all nodes and exit'
    )

    parser.add_argument(
        '--deploy-all',
        action='store_true',
        help='Deploy code to all nodes and exit'
    )

    # Monitoring
    parser.add_argument(
        '--monitor-duration',
        type=int,
        default=300,
        help='How long to monitor experiments (seconds, default 300)'
    )

    args = parser.parse_args()

    # Initialize runner
    runner = ClusterExperimentRunner(args.cluster_config)

    try:
        # Operations
        if args.validate_config:
            await runner.validate_config()
            return 0

        if args.health_check:
            await runner.health_check()
            return 0

        if args.deploy_all:
            await runner.deploy_all()
            return 0

        # Run experiments
        if args.config:
            for config_path in args.config:
                runner.add_experiment_config(config_path)

            # Parse placement
            manual_placement = None
            if args.placement:
                manual_placement = runner.parse_placement_string(args.placement)

            # Run
            await runner.run_experiments(manual_placement)

            # Monitor
            await runner.monitor_all(args.monitor_duration)

        else:
            console.print("[red]Error:[/red] No experiment configs specified (use --config)")
            return 1

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")

    finally:
        await runner.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
