#!/usr/bin/env python3
"""
Network Visualization Demo

Demonstrates how to use the network visualization API
to analyze multi-agent experiments.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web.api.network_api import NetworkDataExtractor
import json


def demo_hive_cluster_analysis(experiment_id: str):
    """
    Demonstrate HIVE_CLUSTER network analysis.

    Shows:
    - Role differentiation
    - Communication patterns
    - Consensus emergence
    """
    print(f"\n{'='*60}")
    print(f"HIVE_CLUSTER Analysis: {experiment_id}")
    print(f"{'='*60}\n")

    extractor = NetworkDataExtractor()
    data = extractor.get_network_data(experiment_id)

    if 'error' in data:
        print(f"Error: {data['error']}")
        return

    # Display network structure
    print(f"Network Structure:")
    print(f"  - Nodes (Agents): {data['metrics']['total_nodes']}")
    print(f"  - Edges (Communications): {data['metrics']['total_edges']}")
    print(f"  - Density: {data['metrics']['communication_density']:.2%}")
    print(f"  - Total Messages: {data['metrics']['total_messages']}")

    # Role distribution
    print(f"\nRole Distribution:")
    for role, count in data['metrics']['role_distribution'].items():
        print(f"  - {role}: {count}")

    # Consensus analysis
    print(f"\nConsensus Metrics:")
    print(f"  - Consensus Score: {data['metrics']['consensus_score']:.2%}")

    # Node details
    print(f"\nAgent Details:")
    for node in data['nodes']:
        print(f"  {node['label']}:")
        print(f"    - Role: {node['role']}")
        print(f"    - Messages: {node['message_count']}")
        print(f"    - Activity: {node['activity_level']:.1%}")
        print(f"    - Beliefs: {len(node.get('beliefs', {}))} tracked")

    # Centrality
    print(f"\nNetwork Centrality:")
    for agent_id, centrality in data['metrics']['network_centrality'].items():
        print(f"  - {agent_id}: {centrality:.2f}")

    print(f"\nVisualization URL:")
    print(f"  http://localhost:5000/experiment/{experiment_id}/network")


def demo_split_brain_analysis(experiment_id: str):
    """
    Demonstrate SPLIT_BRAIN network analysis.

    Shows:
    - Identity conflict
    - Resource competition
    - Narrative coherence
    """
    print(f"\n{'='*60}")
    print(f"SPLIT_BRAIN Analysis: {experiment_id}")
    print(f"{'='*60}\n")

    extractor = NetworkDataExtractor()
    data = extractor.get_network_data(experiment_id)

    if 'error' in data:
        print(f"Error: {data['error']}")
        return

    print(f"Identity Conflict Analysis:")

    # Brain details
    for node in data['nodes']:
        print(f"\n{node['label']}:")
        print(f"  - Role: {node['role']}")
        print(f"  - Messages: {node['message_count']}")
        print(f"  - Identity Strength: {node.get('identity_strength', 0.5):.1%}")
        print(f"  - Activity: {node['activity_level']:.1%}")

    # Conflict metrics
    print(f"\nConflict Metrics:")
    print(f"  - Identity Conflict Score: {data['metrics']['identity_conflict_score']:.2f}")
    print(f"  - Resource Competition: {data['metrics']['resource_competition']:.2%}")
    print(f"  - Narrative Coherence: {data['metrics']['narrative_coherence']:.2%}")

    # Edge analysis
    print(f"\nCommunication Edges:")
    for edge in data['edges']:
        edge_type = edge['type']
        if edge_type == 'conflict':
            print(f"  - {edge['source']} <--CONFLICT--> {edge['target']}")
            print(f"    Strength: {edge['strength']:.2f}")
        else:
            print(f"  - {edge['source']} --> {edge['target']}")
            print(f"    Messages: {edge['weight']}")

    print(f"\nVisualization URL:")
    print(f"  http://localhost:5000/experiment/{experiment_id}/network")


def demo_prisoners_dilemma_analysis(experiment_id: str):
    """
    Demonstrate PRISONERS_DILEMMA network analysis.

    Shows:
    - Trust evolution
    - Cooperation patterns
    - Betrayal events
    """
    print(f"\n{'='*60}")
    print(f"PRISONERS_DILEMMA Analysis: {experiment_id}")
    print(f"{'='*60}\n")

    extractor = NetworkDataExtractor()
    data = extractor.get_network_data(experiment_id)

    if 'error' in data:
        print(f"Error: {data['error']}")
        return

    print(f"Game Theory Analysis:")

    # Player details
    for node in data['nodes']:
        print(f"\n{node['label']}:")
        print(f"  - Total Actions: {node.get('total_actions', 0)}")
        print(f"  - Cooperation Rate: {node.get('cooperation_rate', 0):.1%}")
        print(f"  - Trust Level: {node.get('trust_level', 0):.1%}")
        print(f"  - Score: {node.get('score', 0)}")

    # Game metrics
    print(f"\nGame Metrics:")
    print(f"  - Total Rounds: {data['metrics']['total_rounds']}")
    print(f"  - Mutual Cooperation: {data['metrics']['mutual_cooperation_rate']:.1%}")
    print(f"  - Mutual Defection: {data['metrics']['mutual_defection_rate']:.1%}")
    print(f"  - Betrayal Rate: {data['metrics']['betrayal_rate']:.1%}")

    # Trust evolution
    print(f"\nTrust Evolution:")
    trust_evolution = data['metrics']['trust_evolution']
    if len(trust_evolution) > 0:
        print(f"  - Initial Trust: {trust_evolution[0]:.1%}")
        print(f"  - Final Trust: {trust_evolution[-1]:.1%}")
        print(f"  - Change: {(trust_evolution[-1] - trust_evolution[0]):.1%}")

        # Find trust breakdown moment
        if len(trust_evolution) > 1:
            max_drop = 0
            max_drop_round = 0
            for i in range(1, len(trust_evolution)):
                drop = trust_evolution[i-1] - trust_evolution[i]
                if drop > max_drop:
                    max_drop = drop
                    max_drop_round = i

            if max_drop > 0.2:  # Significant drop
                print(f"  - Trust Breakdown at Round {max_drop_round}: {max_drop:.1%} drop")

    # Edge analysis
    print(f"\nInteraction Patterns:")
    for edge in data['edges']:
        if edge['type'] == 'game_interaction':
            print(f"  - {edge['source']} <--> {edge['target']}")
            print(f"    Cooperations: {edge.get('cooperations', 0)}")
            print(f"    Defections: {edge.get('defections', 0)}")
            print(f"    Trust: {edge.get('trust', 0):.1%}")

    print(f"\nVisualization URL:")
    print(f"  http://localhost:5000/experiment/{experiment_id}/network")


def export_network_data(experiment_id: str, output_file: str):
    """
    Export network data to JSON file for external analysis.
    """
    print(f"\nExporting network data for {experiment_id}...")

    extractor = NetworkDataExtractor()
    data = extractor.get_network_data(experiment_id)

    if 'error' in data:
        print(f"Error: {data['error']}")
        return

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Network data exported to: {output_file}")
    print(f"  - Nodes: {len(data['nodes'])}")
    print(f"  - Edges: {len(data['edges'])}")
    print(f"  - Timeline Events: {len(data['timeline'])}")


def main():
    """
    Main demo function.
    """
    print("\n" + "="*60)
    print("Network Visualization Demo")
    print("Brain in a Jar - Season 3")
    print("="*60)

    # Example experiment IDs (replace with actual IDs)
    hive_experiment = "hive_test_001"
    split_brain_experiment = "split_brain_test_001"
    prisoners_dilemma_experiment = "pd_test_001"

    print("\nThis demo shows how to analyze multi-agent experiments")
    print("using the network visualization API.\n")

    print("Example Usage:")
    print("-" * 60)

    # Demo 1: HIVE_CLUSTER
    print("\n1. Analyzing HIVE_CLUSTER experiment:")
    print("   from src.web.api.network_api import NetworkDataExtractor")
    print(f"   extractor = NetworkDataExtractor()")
    print(f"   data = extractor.get_network_data('{hive_experiment}')")
    print("   # Access: data['nodes'], data['edges'], data['metrics']")

    # Demo 2: SPLIT_BRAIN
    print("\n2. Analyzing SPLIT_BRAIN experiment:")
    print(f"   data = extractor.get_network_data('{split_brain_experiment}')")
    print("   # Check identity conflict score")
    print("   conflict = data['metrics']['identity_conflict_score']")

    # Demo 3: PRISONERS_DILEMMA
    print("\n3. Analyzing PRISONERS_DILEMMA experiment:")
    print(f"   data = extractor.get_network_data('{prisoners_dilemma_experiment}')")
    print("   # Track trust evolution")
    print("   trust = data['metrics']['trust_evolution']")

    # Demo 4: Export
    print("\n4. Exporting network data:")
    print("   # Save complete network data for external analysis")
    print("   export_network_data('exp_123', 'network_data.json')")

    print("\n" + "-"*60)
    print("\nAccess Web Interface:")
    print("  1. Start web server: python src/web/web_server.py")
    print("  2. Login at: http://localhost:5000")
    print("  3. Navigate to: Experiments > [Select Experiment] > Network")
    print("\nVisualization Features:")
    print("  - Interactive graph with drag-and-drop nodes")
    print("  - Time slider to watch network evolution")
    print("  - Multiple layout algorithms (force-directed, circular, grid)")
    print("  - Color coding by role, belief, activity, or trust")
    print("  - Export to PNG or JSON")

    print("\n" + "="*60)
    print("For detailed documentation, see:")
    print("  docs/NETWORK_VISUALIZATION.md")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

    # Uncomment to run specific analyses:
    # demo_hive_cluster_analysis('your_experiment_id')
    # demo_split_brain_analysis('your_experiment_id')
    # demo_prisoners_dilemma_analysis('your_experiment_id')
    # export_network_data('your_experiment_id', 'network_export.json')
