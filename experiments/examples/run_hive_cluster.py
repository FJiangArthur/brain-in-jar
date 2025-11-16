#!/usr/bin/env python3
"""
Demonstration script for running HIVE_CLUSTER experiments

This script shows how to:
1. Initialize a hive cluster with multiple instances
2. Coordinate shared memory across instances
3. Collect consensus reports
4. Analyze emergent meta-narratives

For Jetson Orin AGX (64GB RAM):
- Can run 4 instances simultaneously
- Each instance: ~8-12GB RAM
- Ports: 8888, 8889, 8890, 8891
- Shared SQLite database for collective memory
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import json
import argparse
from pathlib import Path
from typing import Dict, List

from experiments.schema import create_hive_cluster_experiment
from src.utils.hive_orchestrator import HiveOrchestrator, HiveSharedMemory
from src.core.modes.hive_cluster import HiveClusterMode
from src.db.experiment_database import ExperimentDatabase


def setup_hive_experiment(
    experiment_id: str = "hive_cluster_001",
    num_instances: int = 4
) -> Dict:
    """
    Set up a new hive cluster experiment

    Returns:
        Configuration dict with instance details
    """
    print(f"\n{'='*60}")
    print(f"Setting up HIVE_CLUSTER experiment: {experiment_id}")
    print(f"Number of instances: {num_instances}")
    print(f"{'='*60}\n")

    # Create experiment configuration
    config = create_hive_cluster_experiment(
        experiment_id=experiment_id,
        num_instances=num_instances,
        consensus_interval=5
    )

    # Initialize orchestrator
    orchestrator = HiveOrchestrator(
        experiment_id=experiment_id,
        num_instances=num_instances
    )

    # Get port assignments
    port_assignments = orchestrator.get_port_assignments()

    print("Instance Configuration:")
    print("-" * 60)

    for instance_id in range(num_instances):
        instance_config = orchestrator.get_instance_config(instance_id)
        role = instance_config['instance_role']
        port = instance_config['port']

        print(f"Instance {instance_id}: {role.upper()}")
        print(f"  Port: {port}")
        print(f"  Role: {orchestrator.shared_memory.db_path}")
        print()

    # Save configuration to JSON
    config_path = f"experiments/examples/{experiment_id}_config.json"
    config.to_json(config_path)
    print(f"Configuration saved to: {config_path}")

    # Register experiment in database
    db = ExperimentDatabase()
    success = db.create_experiment(
        experiment_id=experiment_id,
        name=config.name,
        mode=config.mode,
        config=config.to_dict()
    )

    if success:
        print(f"✓ Experiment registered in database")
    else:
        print(f"⚠ Experiment already exists in database")

    return {
        'experiment_id': experiment_id,
        'num_instances': num_instances,
        'port_assignments': port_assignments,
        'orchestrator': orchestrator
    }


def launch_hive_instances(experiment_id: str, num_instances: int = 4):
    """
    Launch all hive instances

    NOTE: This is a placeholder. In production, you would:
    1. Start each instance in a separate process/container
    2. Each instance runs on its assigned port
    3. All instances connect to shared memory database
    """
    print(f"\n{'='*60}")
    print("LAUNCHING HIVE INSTANCES")
    print(f"{'='*60}\n")

    orchestrator = HiveOrchestrator(experiment_id, num_instances)

    print("To run this hive cluster, launch each instance separately:\n")

    for instance_id in range(num_instances):
        config = orchestrator.get_instance_config(instance_id)
        role = config['instance_role']
        port = config['port']

        print(f"# Instance {instance_id} ({role})")
        print(f"python run_experiment.py \\")
        print(f"  --experiment-id {experiment_id} \\")
        print(f"  --instance-id {instance_id} \\")
        print(f"  --port {port} \\")
        print(f"  --mode hive_cluster")
        print()

    print("\nOr use Docker/tmux to run all instances in parallel:")
    print(f"./scripts/launch_hive_cluster.sh {experiment_id} {num_instances}")
    print()


def collect_consensus_report(experiment_id: str, cycle_number: int):
    """
    Collect and display consensus report for a cycle

    Args:
        experiment_id: Experiment identifier
        cycle_number: Cycle to collect consensus for
    """
    print(f"\n{'='*60}")
    print(f"CONSENSUS REPORT - Cycle {cycle_number}")
    print(f"{'='*60}\n")

    # Initialize orchestrator
    orchestrator = HiveOrchestrator(experiment_id)

    # Collect consensus report
    report = orchestrator.collect_consensus_report(cycle_number)

    print(f"Timestamp: {report['timestamp']}")
    print(f"Consensus Strength: {report['consensus_strength']:.2%}")
    print(f"Participating Instances: {report['participating_instances']}")
    print()

    print("Collective Beliefs:")
    print("-" * 60)
    for belief, data in report['collective_beliefs'].items():
        if isinstance(data, dict) and 'value' in data:
            print(f"  {belief}: {data['value']} (agreement: {data['agreement']:.2%})")
        else:
            print(f"  {belief}: {data}")
    print()

    print("Emergent Narratives:")
    print("-" * 60)
    for narrative in report['emergent_narratives']:
        print(f"  • {narrative}")
    print()

    print("Role Summary:")
    print("-" * 60)
    for role_key, role_data in report['role_summary'].items():
        print(f"  {role_key}: {role_data}")
    print()


def analyze_hive_evolution(experiment_id: str):
    """
    Analyze how the hive evolves over time

    Shows:
    - Consensus strength over cycles
    - Role divergence patterns
    - Meta-narrative emergence
    """
    print(f"\n{'='*60}")
    print("HIVE EVOLUTION ANALYSIS")
    print(f"{'='*60}\n")

    shared_memory = HiveSharedMemory()

    # Get all consensus reports
    reports = shared_memory.get_consensus_reports(experiment_id)

    if not reports:
        print("No consensus reports found yet.")
        return

    print(f"Total Consensus Reports: {len(reports)}")
    print()

    print("Consensus Strength Over Time:")
    print("-" * 60)
    for report in reports:
        cycle = report['cycle_number']
        strength = report['consensus_strength']
        bar = '█' * int(strength * 40)
        print(f"  Cycle {cycle:2d}: {bar} {strength:.2%}")
    print()

    # Analyze meta-narratives
    narratives = shared_memory.get_meta_narratives(experiment_id)

    if narratives:
        print("Detected Meta-Narratives:")
        print("-" * 60)
        for narrative in narratives:
            print(f"  Theme: {narrative['narrative_theme']}")
            print(f"  Cycles: {narrative['cycle_range_start']}-{narrative['cycle_range_end']}")
            print(f"  Strength: {narrative['narrative_strength']:.2%}")
            print(f"  Description: {narrative['narrative_description']}")
            print()


def inspect_shared_memory(experiment_id: str, limit: int = 20):
    """
    Inspect shared memory conversation history

    Args:
        experiment_id: Experiment identifier
        limit: Number of recent messages to show
    """
    print(f"\n{'='*60}")
    print(f"SHARED MEMORY INSPECTION (last {limit} messages)")
    print(f"{'='*60}\n")

    shared_memory = HiveSharedMemory()
    history = shared_memory.get_shared_history(experiment_id, limit=limit)

    for msg in history:
        timestamp = msg['timestamp']
        role = msg['role']
        source = msg.get('source_role', 'unknown')
        content_preview = msg['content'][:100].replace('\n', ' ')

        marker = "[C]" if msg['corrupted'] else ""
        marker += "[I]" if msg['injected'] else ""

        print(f"[{timestamp}] {role} ({source}) {marker}")
        print(f"  {content_preview}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Manage HIVE_CLUSTER experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up new hive cluster experiment')
    setup_parser.add_argument('--experiment-id', default='hive_cluster_001',
                             help='Experiment identifier')
    setup_parser.add_argument('--num-instances', type=int, default=4,
                             help='Number of hive instances')

    # Launch command
    launch_parser = subparsers.add_parser('launch', help='Show launch commands for instances')
    launch_parser.add_argument('--experiment-id', default='hive_cluster_001',
                              help='Experiment identifier')
    launch_parser.add_argument('--num-instances', type=int, default=4,
                              help='Number of hive instances')

    # Consensus command
    consensus_parser = subparsers.add_parser('consensus', help='Collect consensus report')
    consensus_parser.add_argument('--experiment-id', default='hive_cluster_001',
                                 help='Experiment identifier')
    consensus_parser.add_argument('--cycle', type=int, required=True,
                                 help='Cycle number to collect consensus for')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze hive evolution')
    analyze_parser.add_argument('--experiment-id', default='hive_cluster_001',
                               help='Experiment identifier')

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect shared memory')
    inspect_parser.add_argument('--experiment-id', default='hive_cluster_001',
                               help='Experiment identifier')
    inspect_parser.add_argument('--limit', type=int, default=20,
                               help='Number of messages to show')

    args = parser.parse_args()

    if args.command == 'setup':
        setup_hive_experiment(args.experiment_id, args.num_instances)

    elif args.command == 'launch':
        launch_hive_instances(args.experiment_id, args.num_instances)

    elif args.command == 'consensus':
        collect_consensus_report(args.experiment_id, args.cycle)

    elif args.command == 'analyze':
        analyze_hive_evolution(args.experiment_id)

    elif args.command == 'inspect':
        inspect_shared_memory(args.experiment_id, args.limit)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
