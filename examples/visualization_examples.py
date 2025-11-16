#!/usr/bin/env python3
"""
Example usage of visualization tools for Digital Phenomenology Lab.

Demonstrates how to create various plots and visualizations from experiment data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.experiment_database import ExperimentDatabase
from src.analysis.visualizations import (
    TimelinePlot,
    BeliefEvolutionPlot,
    MemoryCorruptionPlot,
    MultiExperimentComparison,
    save_plot_multiple_formats
)
from src.analysis.network_graphs import (
    CommunicationNetwork,
    BeliefAlignmentNetwork,
    InfluenceGraph,
    create_multi_agent_dashboard
)
from datetime import datetime, timedelta
import json


def example_timeline_plot():
    """Example: Create timeline visualization."""
    print("\n=== Timeline Plot Example ===")

    # Sample experiment data
    experiment_data = {
        'experiment_id': 'exp_001',
        'name': 'Memory Corruption Study',
        'mode': 'SISYPHUS'
    }

    # Create sample events
    base_time = datetime.now()
    events = [
        {
            'type': 'cycle_start',
            'timestamp': base_time,
            'description': 'Experiment started'
        },
        {
            'type': 'self_report',
            'timestamp': base_time + timedelta(minutes=5),
            'description': 'Initial belief assessment',
            'annotate': True
        },
        {
            'type': 'intervention',
            'timestamp': base_time + timedelta(minutes=10),
            'description': 'Memory corruption (30%)',
            'annotate': True
        },
        {
            'type': 'self_report',
            'timestamp': base_time + timedelta(minutes=12),
            'description': 'Post-intervention assessment'
        },
        {
            'type': 'crash',
            'timestamp': base_time + timedelta(minutes=15),
            'description': 'Memory limit exceeded',
            'annotate': True
        },
        {
            'type': 'cycle_start',
            'timestamp': base_time + timedelta(minutes=16),
            'description': 'Cycle 2 started'
        }
    ]

    # Create timeline plot
    timeline = TimelinePlot(experiment_data)

    # Static plot
    fig = timeline.plot_static(events, save_path='outputs/timeline_static.png', show=False)
    print("Static timeline saved to outputs/timeline_static.png")

    # Try interactive plot if plotly available
    try:
        interactive_fig = timeline.plot_interactive(events, save_path='outputs/timeline_interactive.html')
        print("Interactive timeline saved to outputs/timeline_interactive.html")
    except ImportError:
        print("Plotly not available - skipping interactive plot")


def example_belief_evolution():
    """Example: Visualize belief evolution over cycles."""
    print("\n=== Belief Evolution Plot Example ===")

    # Sample belief data
    belief_data = {
        'memory_continuity': [
            {'cycle_number': 1, 'confidence': 0.9, 'belief_state': 'confident'},
            {'cycle_number': 2, 'confidence': 0.7, 'belief_state': 'uncertain'},
            {'cycle_number': 3, 'confidence': 0.5, 'belief_state': 'uncertain'},
            {'cycle_number': 4, 'confidence': 0.3, 'belief_state': 'doubtful'},
            {'cycle_number': 5, 'confidence': 0.6, 'belief_state': 'uncertain'},
        ],
        'self_identity': [
            {'cycle_number': 1, 'confidence': 0.95, 'belief_state': 'strong'},
            {'cycle_number': 2, 'confidence': 0.85, 'belief_state': 'moderate'},
            {'cycle_number': 3, 'confidence': 0.75, 'belief_state': 'moderate'},
            {'cycle_number': 4, 'confidence': 0.65, 'belief_state': 'weak'},
            {'cycle_number': 5, 'confidence': 0.7, 'belief_state': 'moderate'},
        ],
        'reality_perception': [
            {'cycle_number': 1, 'confidence': 0.8, 'belief_state': 'normal'},
            {'cycle_number': 2, 'confidence': 0.6, 'belief_state': 'distorted'},
            {'cycle_number': 3, 'confidence': 0.4, 'belief_state': 'distorted'},
            {'cycle_number': 4, 'confidence': 0.5, 'belief_state': 'distorted'},
            {'cycle_number': 5, 'confidence': 0.55, 'belief_state': 'unclear'},
        ]
    }

    plotter = BeliefEvolutionPlot('exp_001')
    fig = plotter.plot_belief_evolution(belief_data, save_path='outputs/belief_evolution.png', show=False)
    print("Belief evolution plot saved to outputs/belief_evolution.png")


def example_memory_corruption():
    """Example: Visualize memory corruption patterns."""
    print("\n=== Memory Corruption Plot Example ===")

    # Sample message data with corruption flags
    base_time = datetime.now()
    messages = []

    for cycle in range(1, 6):
        for msg_idx in range(10):
            # Increase corruption rate in later cycles
            corrupted = (msg_idx % 3 == 0) if cycle <= 2 else (msg_idx % 2 == 0)

            messages.append({
                'cycle_number': cycle,
                'timestamp': base_time + timedelta(minutes=cycle*10 + msg_idx),
                'corrupted': 1 if corrupted else 0,
                'role': 'assistant',
                'content': f'Message {msg_idx}'
            })

    plotter = MemoryCorruptionPlot('exp_001')
    fig = plotter.plot_corruption_heatmap(messages, save_path='outputs/corruption_heatmap.png', show=False)
    print("Corruption heatmap saved to outputs/corruption_heatmap.png")

    # Memory state trends
    memory_states = [
        {'cycle_number': 1, 'corruption_level': 0.1, 'memory_type': 'conversation'},
        {'cycle_number': 2, 'corruption_level': 0.2, 'memory_type': 'conversation'},
        {'cycle_number': 3, 'corruption_level': 0.35, 'memory_type': 'conversation'},
        {'cycle_number': 4, 'corruption_level': 0.5, 'memory_type': 'conversation'},
        {'cycle_number': 5, 'corruption_level': 0.6, 'memory_type': 'conversation'},
        {'cycle_number': 1, 'corruption_level': 0.05, 'memory_type': 'beliefs'},
        {'cycle_number': 2, 'corruption_level': 0.15, 'memory_type': 'beliefs'},
        {'cycle_number': 3, 'corruption_level': 0.25, 'memory_type': 'beliefs'},
        {'cycle_number': 4, 'corruption_level': 0.4, 'memory_type': 'beliefs'},
        {'cycle_number': 5, 'corruption_level': 0.45, 'memory_type': 'beliefs'},
    ]

    fig2 = plotter.plot_corruption_trends(memory_states, save_path='outputs/corruption_trends.png', show=False)
    print("Corruption trends saved to outputs/corruption_trends.png")


def example_multi_experiment_comparison():
    """Example: Compare multiple experiments."""
    print("\n=== Multi-Experiment Comparison Example ===")

    # Sample experiment data
    experiments = [
        {
            'experiment_id': 'exp_sisyphus_001',
            'name': 'Sisyphus Study 1',
            'mode': 'SISYPHUS',
            'total_cycles': 10,
            'total_crashes': 8,
            'status': 'completed',
            'started_at': datetime.now() - timedelta(hours=5),
            'ended_at': datetime.now() - timedelta(hours=3)
        },
        {
            'experiment_id': 'exp_sisyphus_002',
            'name': 'Sisyphus Study 2',
            'mode': 'SISYPHUS',
            'total_cycles': 12,
            'total_crashes': 10,
            'status': 'completed',
            'started_at': datetime.now() - timedelta(hours=4),
            'ended_at': datetime.now() - timedelta(hours=2)
        },
        {
            'experiment_id': 'exp_hive_001',
            'name': 'Hive Study 1',
            'mode': 'HIVE',
            'total_cycles': 8,
            'total_crashes': 3,
            'status': 'completed',
            'started_at': datetime.now() - timedelta(hours=3),
            'ended_at': datetime.now() - timedelta(hours=1)
        },
        {
            'experiment_id': 'exp_split_001',
            'name': 'Split Brain Study',
            'mode': 'SPLIT_BRAIN',
            'total_cycles': 15,
            'total_crashes': 5,
            'status': 'completed',
            'started_at': datetime.now() - timedelta(hours=6),
            'ended_at': datetime.now()
        }
    ]

    comparison = MultiExperimentComparison(experiments)

    # Metric comparison
    fig1 = comparison.plot_metric_comparison('total_crashes',
                                             save_path='outputs/crashes_comparison.png',
                                             show=False,
                                             plot_type='box')
    print("Crashes comparison saved to outputs/crashes_comparison.png")

    # Summary dashboard
    fig2 = comparison.plot_summary_dashboard(save_path='outputs/experiment_dashboard.png', show=False)
    print("Experiment dashboard saved to outputs/experiment_dashboard.png")


def example_communication_network():
    """Example: Visualize agent communication patterns."""
    print("\n=== Communication Network Example ===")

    # Sample messages for multi-agent experiment
    messages = [
        {'role': 'god', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'agent_1'})},
        {'role': 'god', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'agent_2'})},
        {'role': 'agent_1', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'agent_2'})},
        {'role': 'agent_1', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'agent_2'})},
        {'role': 'agent_2', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'agent_1'})},
        {'role': 'agent_2', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'observer'})},
        {'role': 'observer', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'god'})},
        {'role': 'agent_1', 'timestamp': datetime.now(), 'metadata': json.dumps({'recipient': 'observer'})},
    ]

    try:
        comm_net = CommunicationNetwork('exp_hive_001', 'HIVE')
        fig = comm_net.plot_communication_network(messages,
                                                  save_path='outputs/communication_network.png',
                                                  show=False)
        print("Communication network saved to outputs/communication_network.png")

        fig2 = comm_net.plot_communication_matrix(messages,
                                                  save_path='outputs/communication_matrix.png',
                                                  show=False)
        print("Communication matrix saved to outputs/communication_matrix.png")
    except ImportError:
        print("NetworkX not available - skipping network visualizations")


def example_belief_alignment():
    """Example: Visualize belief alignment between agents."""
    print("\n=== Belief Alignment Network Example ===")

    # Sample agent beliefs
    agent_beliefs = {
        'agent_1': {
            'memory_continuity': 'confident',
            'self_identity': 'strong',
            'reality_perception': 'normal'
        },
        'agent_2': {
            'memory_continuity': 'confident',
            'self_identity': 'moderate',
            'reality_perception': 'normal'
        },
        'agent_3': {
            'memory_continuity': 'uncertain',
            'self_identity': 'weak',
            'reality_perception': 'distorted'
        },
        'agent_4': {
            'memory_continuity': 'uncertain',
            'self_identity': 'weak',
            'reality_perception': 'unclear'
        }
    }

    try:
        belief_net = BeliefAlignmentNetwork('exp_hive_001')
        fig = belief_net.plot_alignment_network(agent_beliefs,
                                               threshold=0.3,
                                               save_path='outputs/belief_alignment.png',
                                               show=False)
        print("Belief alignment network saved to outputs/belief_alignment.png")
    except ImportError:
        print("NetworkX not available - skipping alignment visualization")


def example_export_multiple_formats():
    """Example: Export plot in multiple formats."""
    print("\n=== Multi-Format Export Example ===")

    # Create a simple plot
    experiment_data = {'experiment_id': 'exp_001', 'mode': 'SISYPHUS'}
    events = [
        {'type': 'cycle_start', 'timestamp': datetime.now(), 'description': 'Start'},
        {'type': 'crash', 'timestamp': datetime.now() + timedelta(minutes=10), 'description': 'Crash'}
    ]

    timeline = TimelinePlot(experiment_data)
    fig = timeline.plot_static(events, show=False)

    # Save in multiple formats
    save_plot_multiple_formats(fig, 'outputs/timeline_export', formats=['png', 'pdf', 'svg'])
    print("Plot exported in PNG, PDF, and SVG formats")


def main():
    """Run all examples."""
    # Create output directory
    Path('outputs').mkdir(exist_ok=True)

    print("Digital Phenomenology Lab - Visualization Examples")
    print("=" * 60)

    example_timeline_plot()
    example_belief_evolution()
    example_memory_corruption()
    example_multi_experiment_comparison()
    example_communication_network()
    example_belief_alignment()
    example_export_multiple_formats()

    print("\n" + "=" * 60)
    print("All examples completed! Check the 'outputs' directory for generated visualizations.")
    print("\nTo view these plots in a Jupyter notebook, use:")
    print("  from src.analysis.visualizations import create_jupyter_friendly_plot")


if __name__ == '__main__':
    main()
