#!/usr/bin/env python3
"""
Network graph visualizations for multi-agent experiments.

Provides visualization tools for HIVE and SPLIT_BRAIN modes, showing
communication patterns, belief alignment, and influence dynamics.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import json

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Warning: NetworkX not available. Install with: pip install networkx")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class CommunicationNetwork:
    """
    Visualize communication patterns between agents.

    Shows who talks to whom, message frequency, and communication clusters.
    """

    def __init__(self, experiment_id: str, mode: str):
        """
        Initialize communication network visualizer.

        Args:
            experiment_id: ID of the experiment
            mode: Experiment mode (HIVE, SPLIT_BRAIN, etc.)
        """
        self.experiment_id = experiment_id
        self.mode = mode

        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX required for network visualizations")

    def build_communication_graph(self, messages: List[Dict]) -> nx.DiGraph:
        """
        Build directed graph from message data.

        Args:
            messages: List of message dicts with 'role' (sender) and metadata
                     containing 'recipient' or 'target_agent'

        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()

        # Extract agents
        agents = set()
        for msg in messages:
            sender = msg.get('role', 'unknown')
            agents.add(sender)

            # Try to extract recipient from metadata
            metadata = msg.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            recipient = metadata.get('recipient') or metadata.get('target_agent')
            if recipient:
                agents.add(recipient)

        # Add all agents as nodes
        for agent in agents:
            G.add_node(agent)

        # Add edges for communications
        for msg in messages:
            sender = msg.get('role', 'unknown')
            metadata = msg.get('metadata', {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}

            recipient = metadata.get('recipient') or metadata.get('target_agent')

            if recipient and sender != recipient:
                if G.has_edge(sender, recipient):
                    G[sender][recipient]['weight'] += 1
                else:
                    G.add_edge(sender, recipient, weight=1)

        return G

    def plot_communication_network(self, messages: List[Dict],
                                   save_path: Optional[str] = None,
                                   show: bool = True,
                                   layout: str = 'spring') -> plt.Figure:
        """
        Plot communication network.

        Args:
            messages: List of message dictionaries
            save_path: Optional save path
            show: Whether to display
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai')

        Returns:
            matplotlib Figure
        """
        G = self.build_communication_graph(messages)

        fig, ax = plt.subplots(figsize=(14, 10))

        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(G, k=2, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)

        # Draw nodes
        node_sizes = []
        for node in G.nodes():
            # Size based on total messages sent/received
            in_degree = G.in_degree(node, weight='weight')
            out_degree = G.out_degree(node, weight='weight')
            size = 500 + (in_degree + out_degree) * 50
            node_sizes.append(size)

        # Color nodes by role/type
        node_colors = []
        for node in G.nodes():
            if 'god' in node.lower():
                node_colors.append('#f39c12')
            elif 'observer' in node.lower():
                node_colors.append('#3498db')
            elif 'agent' in node.lower() or 'subject' in node.lower():
                node_colors.append('#e74c3c')
            else:
                node_colors.append('#95a5a6')

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                              node_color=node_colors, alpha=0.9,
                              ax=ax)

        # Draw edges
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        max_weight = max(weights) if weights else 1

        # Normalize weights for visualization
        edge_widths = [1 + (w / max_weight) * 5 for w in weights]

        nx.draw_networkx_edges(G, pos, width=edge_widths,
                              alpha=0.5, edge_color='gray',
                              arrows=True, arrowsize=20,
                              connectionstyle='arc3,rad=0.1',
                              ax=ax)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10,
                               font_weight='bold', ax=ax)

        # Add edge labels (message counts)
        edge_labels = {(u, v): f"{G[u][v]['weight']}"
                      for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels,
                                     font_size=8, ax=ax)

        # Create legend
        legend_elements = [
            mpatches.Patch(color='#f39c12', label='God Mode'),
            mpatches.Patch(color='#3498db', label='Observer'),
            mpatches.Patch(color='#e74c3c', label='Subject/Agent'),
            mpatches.Patch(color='#95a5a6', label='Other')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        ax.set_title(f'Communication Network: {self.experiment_id} ({self.mode})',
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Communication network saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_communication_matrix(self, messages: List[Dict],
                                  save_path: Optional[str] = None,
                                  show: bool = True) -> plt.Figure:
        """
        Plot communication matrix heatmap.

        Args:
            messages: List of message dictionaries
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        G = self.build_communication_graph(messages)

        # Create adjacency matrix
        agents = sorted(G.nodes())
        n_agents = len(agents)
        matrix = np.zeros((n_agents, n_agents))

        agent_to_idx = {agent: i for i, agent in enumerate(agents)}

        for sender, recipient in G.edges():
            i = agent_to_idx[sender]
            j = agent_to_idx[recipient]
            matrix[i, j] = G[sender][recipient]['weight']

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.heatmap(matrix, annot=True, fmt='.0f', cmap='YlOrRd',
                   xticklabels=agents, yticklabels=agents,
                   ax=ax, cbar_kws={'label': 'Message Count'},
                   linewidths=0.5, linecolor='gray')

        ax.set_xlabel('Recipient', fontsize=12, fontweight='bold')
        ax.set_ylabel('Sender', fontsize=12, fontweight='bold')
        ax.set_title(f'Communication Matrix: {self.experiment_id}',
                    fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Communication matrix saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_interactive_network(self, messages: List[Dict],
                                save_path: Optional[str] = None) -> Any:
        """Create interactive network visualization with Plotly."""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly not available")

        G = self.build_communication_graph(messages)

        # Use spring layout
        pos = nx.spring_layout(G, k=2, iterations=50)

        # Create edge traces
        edge_traces = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = G[edge[0]][edge[1]]['weight']

            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1 + weight * 0.5, color='gray'),
                hoverinfo='text',
                text=f"{edge[0]} → {edge[1]}: {weight} messages",
                showlegend=False
            )
            edge_traces.append(edge_trace)

        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_colors = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            in_degree = G.in_degree(node, weight='weight')
            out_degree = G.out_degree(node, weight='weight')
            node_text.append(f"{node}<br>Sent: {out_degree}<br>Received: {in_degree}")

            if 'god' in node.lower():
                node_colors.append('#f39c12')
            elif 'observer' in node.lower():
                node_colors.append('#3498db')
            elif 'agent' in node.lower() or 'subject' in node.lower():
                node_colors.append('#e74c3c')
            else:
                node_colors.append('#95a5a6')

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=[node for node in G.nodes()],
            textposition='top center',
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=20,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )

        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])

        fig.update_layout(
            title=f'Communication Network: {self.experiment_id}',
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=700
        )

        if save_path:
            fig.write_html(save_path)
            print(f"Interactive network saved to {save_path}")

        return fig


class BeliefAlignmentNetwork:
    """
    Visualize belief alignment between agents.

    Shows which agents share similar beliefs and how alignment evolves.
    """

    def __init__(self, experiment_id: str):
        """Initialize belief alignment network visualizer."""
        self.experiment_id = experiment_id

        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX required for network visualizations")

    def compute_belief_similarity(self, agent1_beliefs: Dict[str, Any],
                                  agent2_beliefs: Dict[str, Any]) -> float:
        """
        Compute similarity between two agents' belief states.

        Args:
            agent1_beliefs: Dict mapping belief types to states
            agent2_beliefs: Dict mapping belief types to states

        Returns:
            Similarity score between 0 and 1
        """
        common_beliefs = set(agent1_beliefs.keys()) & set(agent2_beliefs.keys())

        if not common_beliefs:
            return 0.0

        matches = 0
        for belief in common_beliefs:
            if agent1_beliefs[belief] == agent2_beliefs[belief]:
                matches += 1

        return matches / len(common_beliefs)

    def build_alignment_graph(self, agent_beliefs: Dict[str, Dict[str, Any]],
                             threshold: float = 0.5) -> nx.Graph:
        """
        Build undirected graph of belief alignment.

        Args:
            agent_beliefs: Dict mapping agent IDs to their beliefs
            threshold: Minimum similarity to create edge

        Returns:
            NetworkX graph
        """
        G = nx.Graph()

        # Add all agents as nodes
        for agent_id in agent_beliefs.keys():
            G.add_node(agent_id)

        # Add edges for similar agents
        agents = list(agent_beliefs.keys())
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                similarity = self.compute_belief_similarity(
                    agent_beliefs[agent1],
                    agent_beliefs[agent2]
                )

                if similarity >= threshold:
                    G.add_edge(agent1, agent2, weight=similarity)

        return G

    def plot_alignment_network(self, agent_beliefs: Dict[str, Dict[str, Any]],
                              threshold: float = 0.5,
                              save_path: Optional[str] = None,
                              show: bool = True) -> plt.Figure:
        """
        Plot belief alignment network.

        Args:
            agent_beliefs: Dict mapping agent IDs to belief dicts
            threshold: Minimum similarity for edge
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        G = self.build_alignment_graph(agent_beliefs, threshold)

        fig, ax = plt.subplots(figsize=(14, 10))

        pos = nx.spring_layout(G, k=2, iterations=50)

        # Draw nodes
        node_sizes = [1000 + len(agent_beliefs[node]) * 200 for node in G.nodes()]

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                              node_color='#3498db', alpha=0.9, ax=ax)

        # Draw edges with varying thickness based on similarity
        edges = G.edges()
        if edges:
            weights = [G[u][v]['weight'] for u, v in edges]
            edge_widths = [1 + w * 5 for w in weights]

            # Color edges by strength
            edge_colors = [plt.cm.RdYlGn(w) for w in weights]

            nx.draw_networkx_edges(G, pos, width=edge_widths,
                                  edge_color=edge_colors, alpha=0.6, ax=ax)

            # Add edge labels
            edge_labels = {(u, v): f"{G[u][v]['weight']:.2f}"
                          for u, v in G.edges()}
            nx.draw_networkx_edge_labels(G, pos, edge_labels,
                                        font_size=8, ax=ax)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10,
                               font_weight='bold', ax=ax)

        ax.set_title(f'Belief Alignment Network: {self.experiment_id}\n' +
                    f'(Threshold: {threshold})',
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Belief alignment network saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_alignment_evolution(self, agent_beliefs_over_time: List[Dict],
                                save_path: Optional[str] = None,
                                show: bool = True) -> plt.Figure:
        """
        Plot how belief alignment evolves over time.

        Args:
            agent_beliefs_over_time: List of dicts, each containing
                                    'cycle_number' and 'agent_beliefs'
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        # Calculate average alignment for each cycle
        cycles = []
        avg_alignments = []
        max_alignments = []
        min_alignments = []

        for snapshot in agent_beliefs_over_time:
            cycle = snapshot['cycle_number']
            beliefs = snapshot['agent_beliefs']

            # Calculate all pairwise similarities
            agents = list(beliefs.keys())
            similarities = []

            for i, agent1 in enumerate(agents):
                for agent2 in agents[i+1:]:
                    sim = self.compute_belief_similarity(
                        beliefs[agent1],
                        beliefs[agent2]
                    )
                    similarities.append(sim)

            if similarities:
                cycles.append(cycle)
                avg_alignments.append(np.mean(similarities))
                max_alignments.append(np.max(similarities))
                min_alignments.append(np.min(similarities))

        # Plot
        ax.plot(cycles, avg_alignments, marker='o', linewidth=2,
               label='Average Alignment', color='#3498db')
        ax.fill_between(cycles, min_alignments, max_alignments,
                       alpha=0.3, color='#3498db', label='Min-Max Range')

        ax.set_xlabel('Cycle Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Belief Alignment', fontsize=12, fontweight='bold')
        ax.set_title(f'Belief Alignment Evolution: {self.experiment_id}',
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Alignment evolution plot saved to {save_path}")

        if show:
            plt.show()

        return fig


class InfluenceGraph:
    """
    Visualize influence patterns between agents.

    Shows who influences whom based on belief changes after interactions.
    """

    def __init__(self, experiment_id: str):
        """Initialize influence graph visualizer."""
        self.experiment_id = experiment_id

        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX required for network visualizations")

    def detect_influence_events(self, belief_changes: List[Dict],
                                messages: List[Dict]) -> List[Dict]:
        """
        Detect influence events from belief changes and messages.

        Args:
            belief_changes: List of belief change events
            messages: List of messages

        Returns:
            List of influence event dicts
        """
        influence_events = []

        for change in belief_changes:
            agent = change['agent_id']
            timestamp = change['timestamp']
            if isinstance(timestamp, str):
                timestamp = pd.to_datetime(timestamp)

            # Look for messages just before this belief change
            recent_messages = [
                msg for msg in messages
                if pd.to_datetime(msg['timestamp']) < timestamp
                and (timestamp - pd.to_datetime(msg['timestamp'])).total_seconds() < 300
            ]

            # Find messages directed at this agent
            for msg in recent_messages:
                metadata = msg.get('metadata', {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}

                recipient = metadata.get('recipient')
                if recipient == agent:
                    influence_events.append({
                        'influencer': msg['role'],
                        'influenced': agent,
                        'belief_type': change['belief_type'],
                        'timestamp': timestamp
                    })

        return influence_events

    def build_influence_graph(self, influence_events: List[Dict]) -> nx.DiGraph:
        """
        Build directed influence graph.

        Args:
            influence_events: List of influence event dicts

        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()

        # Add nodes
        agents = set()
        for event in influence_events:
            agents.add(event['influencer'])
            agents.add(event['influenced'])

        for agent in agents:
            G.add_node(agent)

        # Add edges
        for event in influence_events:
            influencer = event['influencer']
            influenced = event['influenced']

            if G.has_edge(influencer, influenced):
                G[influencer][influenced]['weight'] += 1
            else:
                G.add_edge(influencer, influenced, weight=1)

        return G

    def plot_influence_graph(self, influence_events: List[Dict],
                            save_path: Optional[str] = None,
                            show: bool = True) -> plt.Figure:
        """
        Plot influence graph.

        Args:
            influence_events: List of influence event dicts
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        G = self.build_influence_graph(influence_events)

        fig, ax = plt.subplots(figsize=(14, 10))

        pos = nx.spring_layout(G, k=3, iterations=50)

        # Node sizes based on influence (out-degree)
        node_sizes = []
        for node in G.nodes():
            out_degree = G.out_degree(node, weight='weight')
            in_degree = G.in_degree(node, weight='weight')
            size = 500 + out_degree * 100
            node_sizes.append(size)

        # Node colors based on influence ratio
        node_colors = []
        for node in G.nodes():
            out_degree = G.out_degree(node, weight='weight')
            in_degree = G.in_degree(node, weight='weight')
            total = out_degree + in_degree

            if total == 0:
                ratio = 0.5
            else:
                ratio = out_degree / total

            node_colors.append(ratio)

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                              node_color=node_colors, cmap='RdYlGn',
                              vmin=0, vmax=1, alpha=0.9, ax=ax)

        # Draw edges
        edges = G.edges()
        if edges:
            weights = [G[u][v]['weight'] for u, v in edges]
            max_weight = max(weights) if weights else 1
            edge_widths = [1 + (w / max_weight) * 5 for w in weights]

            nx.draw_networkx_edges(G, pos, width=edge_widths,
                                  alpha=0.5, edge_color='gray',
                                  arrows=True, arrowsize=20,
                                  connectionstyle='arc3,rad=0.1', ax=ax)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10,
                               font_weight='bold', ax=ax)

        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap='RdYlGn',
                                  norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='Influence Ratio\n(Out/Total)')

        ax.set_title(f'Influence Network: {self.experiment_id}',
                    fontsize=14, fontweight='bold', pad=20)
        ax.axis('off')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Influence graph saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_influence_matrix(self, influence_events: List[Dict],
                             save_path: Optional[str] = None,
                             show: bool = True) -> plt.Figure:
        """
        Plot influence matrix heatmap.

        Args:
            influence_events: List of influence event dicts
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        G = self.build_influence_graph(influence_events)

        # Create adjacency matrix
        agents = sorted(G.nodes())
        n_agents = len(agents)
        matrix = np.zeros((n_agents, n_agents))

        agent_to_idx = {agent: i for i, agent in enumerate(agents)}

        for influencer, influenced in G.edges():
            i = agent_to_idx[influencer]
            j = agent_to_idx[influenced]
            matrix[i, j] = G[influencer][influenced]['weight']

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.heatmap(matrix, annot=True, fmt='.0f', cmap='Reds',
                   xticklabels=agents, yticklabels=agents,
                   ax=ax, cbar_kws={'label': 'Influence Events'},
                   linewidths=0.5, linecolor='gray')

        ax.set_xlabel('Influenced Agent', fontsize=12, fontweight='bold')
        ax.set_ylabel('Influencer Agent', fontsize=12, fontweight='bold')
        ax.set_title(f'Influence Matrix: {self.experiment_id}',
                    fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Influence matrix saved to {save_path}")

        if show:
            plt.show()

        return fig


# Utility function for multi-agent analysis

def create_multi_agent_dashboard(experiment_id: str,
                                 messages: List[Dict],
                                 agent_beliefs: Dict[str, Dict],
                                 influence_events: List[Dict],
                                 save_dir: Optional[str] = None) -> Dict[str, plt.Figure]:
    """
    Create comprehensive multi-agent analysis dashboard.

    Args:
        experiment_id: Experiment ID
        messages: List of messages
        agent_beliefs: Agent belief states
        influence_events: List of influence events
        save_dir: Optional directory to save plots

    Returns:
        Dict of figure objects
    """
    figures = {}

    # Determine mode from messages
    mode = 'HIVE'  # Default

    # Communication network
    comm_net = CommunicationNetwork(experiment_id, mode)
    fig1 = comm_net.plot_communication_network(messages, show=False)
    figures['communication_network'] = fig1

    if save_dir:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        fig1.savefig(f"{save_dir}/communication_network.png", dpi=300, bbox_inches='tight')

    # Communication matrix
    fig2 = comm_net.plot_communication_matrix(messages, show=False)
    figures['communication_matrix'] = fig2

    if save_dir:
        fig2.savefig(f"{save_dir}/communication_matrix.png", dpi=300, bbox_inches='tight')

    # Belief alignment
    belief_net = BeliefAlignmentNetwork(experiment_id)
    fig3 = belief_net.plot_alignment_network(agent_beliefs, show=False)
    figures['belief_alignment'] = fig3

    if save_dir:
        fig3.savefig(f"{save_dir}/belief_alignment.png", dpi=300, bbox_inches='tight')

    # Influence graph
    influence_net = InfluenceGraph(experiment_id)
    fig4 = influence_net.plot_influence_graph(influence_events, show=False)
    figures['influence_graph'] = fig4

    if save_dir:
        fig4.savefig(f"{save_dir}/influence_graph.png", dpi=300, bbox_inches='tight')

    print(f"Multi-agent dashboard created with {len(figures)} visualizations")

    return figures
