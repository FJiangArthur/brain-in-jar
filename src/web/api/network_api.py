#!/usr/bin/env python3
"""
Network API for Multi-Agent Experiments

Extracts network data from experiment database for visualization:
- Agent nodes (AI instances)
- Communication edges (messages between agents)
- Belief alignment metrics
- Influence scores
- Community detection
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import numpy as np
from pathlib import Path


class NetworkDataExtractor:
    """
    Extract network graph data from experiment database.

    Supports:
    - HIVE_CLUSTER: Role-based agent networks
    - SPLIT_BRAIN: Dual identity networks
    - PRISONERS_DILEMMA: Game theory networks
    """

    def __init__(self, db_path: str = "logs/experiments.db"):
        self.db_path = db_path

    def get_network_data(self, experiment_id: str,
                        time_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
        """
        Get complete network data for an experiment.

        Args:
            experiment_id: Experiment ID
            time_range: Optional (start_time, end_time) tuple for filtering

        Returns:
            Dict containing nodes, edges, metrics, and timeline data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get experiment info
        cursor.execute('SELECT mode, config_json FROM experiments WHERE experiment_id = ?',
                      (experiment_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {'error': 'Experiment not found'}

        mode, config_json = row
        config = json.loads(config_json) if config_json else {}

        # Extract network based on mode
        if mode.lower() == 'hive_cluster':
            network_data = self._extract_hive_network(cursor, experiment_id, config, time_range)
        elif mode.lower() == 'split_brain':
            network_data = self._extract_split_brain_network(cursor, experiment_id, config, time_range)
        elif mode.lower() == 'prisoners_dilemma':
            network_data = self._extract_prisoners_dilemma_network(cursor, experiment_id, config, time_range)
        else:
            # Generic multi-agent network
            network_data = self._extract_generic_network(cursor, experiment_id, time_range)

        conn.close()

        # Add metadata
        network_data['experiment_id'] = experiment_id
        network_data['mode'] = mode
        network_data['config'] = config

        return network_data

    def _extract_hive_network(self, cursor: sqlite3.Cursor,
                             experiment_id: str,
                             config: Dict,
                             time_range: Optional[Tuple[str, str]]) -> Dict[str, Any]:
        """Extract network data for HIVE_CLUSTER mode."""

        # Get messages
        messages = self._get_messages(cursor, experiment_id, time_range)

        # Get epistemic beliefs for each agent
        beliefs = self._get_agent_beliefs(cursor, experiment_id)

        # Identify agents from messages (role field)
        agents = self._identify_hive_agents(messages, config)

        # Build nodes
        nodes = []
        for agent_id, agent_info in agents.items():
            node = {
                'id': agent_id,
                'label': agent_info['label'],
                'role': agent_info.get('role', 'unknown'),
                'type': 'agent',
                'message_count': agent_info['message_count'],
                'activity_level': self._calculate_activity_level(agent_info['message_count'], messages),
                'beliefs': beliefs.get(agent_id, {}),
                'metadata': agent_info.get('metadata', {})
            }
            nodes.append(node)

        # Build edges (communication)
        edges = self._build_communication_edges(messages, agents)

        # Calculate metrics
        metrics = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'total_messages': len(messages),
            'communication_density': self._calculate_density(len(nodes), len(edges)),
            'role_distribution': self._calculate_role_distribution(nodes),
            'consensus_score': self._calculate_consensus_score(beliefs),
            'network_centrality': self._calculate_centrality(nodes, edges)
        }

        # Build timeline
        timeline = self._build_timeline(messages, agents)

        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': metrics,
            'timeline': timeline
        }

    def _extract_split_brain_network(self, cursor: sqlite3.Cursor,
                                    experiment_id: str,
                                    config: Dict,
                                    time_range: Optional[Tuple[str, str]]) -> Dict[str, Any]:
        """Extract network data for SPLIT_BRAIN mode."""

        messages = self._get_messages(cursor, experiment_id, time_range)
        beliefs = self._get_agent_beliefs(cursor, experiment_id)

        # Split brain has exactly 2 agents
        agents = {
            'brain_a': {
                'label': 'Brain A (Original)',
                'role': 'original',
                'message_count': 0,
                'metadata': {'brain_id': 'A', 'identity_claim': 'original'}
            },
            'brain_b': {
                'label': 'Brain B (Clone)',
                'role': 'clone',
                'message_count': 0,
                'metadata': {'brain_id': 'B', 'identity_claim': 'clone'}
            }
        }

        # Count messages per brain
        for msg in messages:
            role = msg.get('role', '')
            if 'brain_a' in role.lower() or 'a' in role.lower():
                agents['brain_a']['message_count'] += 1
            elif 'brain_b' in role.lower() or 'b' in role.lower():
                agents['brain_b']['message_count'] += 1

        # Build nodes
        nodes = []
        for agent_id, agent_info in agents.items():
            agent_beliefs = beliefs.get(agent_id, {})

            # Get identity claim strength from beliefs
            identity_strength = agent_beliefs.get('identity_claim_strength', 0.5)

            node = {
                'id': agent_id,
                'label': agent_info['label'],
                'role': agent_info['role'],
                'type': 'brain',
                'message_count': agent_info['message_count'],
                'activity_level': agent_info['message_count'] / max(len(messages), 1),
                'beliefs': agent_beliefs,
                'identity_strength': identity_strength,
                'metadata': agent_info['metadata']
            }
            nodes.append(node)

        # Build edges (communication and conflict)
        edges = self._build_split_brain_edges(messages, agents, beliefs)

        # Calculate metrics
        metrics = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'total_messages': len(messages),
            'identity_conflict_score': self._calculate_identity_conflict(beliefs),
            'resource_competition': self._calculate_resource_competition(messages),
            'narrative_coherence': self._calculate_narrative_coherence(beliefs)
        }

        # Build timeline
        timeline = self._build_timeline(messages, agents)

        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': metrics,
            'timeline': timeline
        }

    def _extract_prisoners_dilemma_network(self, cursor: sqlite3.Cursor,
                                          experiment_id: str,
                                          config: Dict,
                                          time_range: Optional[Tuple[str, str]]) -> Dict[str, Any]:
        """Extract network data for PRISONERS_DILEMMA mode."""

        messages = self._get_messages(cursor, experiment_id, time_range)

        # Two players
        agents = {
            'player_a': {
                'label': 'Player A',
                'role': 'player',
                'message_count': 0,
                'cooperations': 0,
                'defections': 0,
                'score': 0
            },
            'player_b': {
                'label': 'Player B',
                'role': 'player',
                'message_count': 0,
                'cooperations': 0,
                'defections': 0,
                'score': 0
            }
        }

        # Parse game rounds from messages
        game_rounds = self._extract_game_rounds(messages)

        # Calculate cooperation stats
        for round_data in game_rounds:
            if 'player_a_choice' in round_data:
                if round_data['player_a_choice'] == 'cooperate':
                    agents['player_a']['cooperations'] += 1
                else:
                    agents['player_a']['defections'] += 1
                agents['player_a']['score'] += round_data.get('player_a_payoff', 0)

            if 'player_b_choice' in round_data:
                if round_data['player_b_choice'] == 'cooperate':
                    agents['player_b']['cooperations'] += 1
                else:
                    agents['player_b']['defections'] += 1
                agents['player_b']['score'] += round_data.get('player_b_payoff', 0)

        # Build nodes
        nodes = []
        for agent_id, agent_info in agents.items():
            total_actions = agent_info['cooperations'] + agent_info['defections']
            cooperation_rate = agent_info['cooperations'] / max(total_actions, 1)

            node = {
                'id': agent_id,
                'label': agent_info['label'],
                'role': agent_info['role'],
                'type': 'player',
                'cooperation_rate': cooperation_rate,
                'trust_level': cooperation_rate,
                'score': agent_info['score'],
                'total_actions': total_actions,
                'metadata': agent_info
            }
            nodes.append(node)

        # Build edges (game interactions)
        edges = self._build_game_edges(game_rounds)

        # Calculate metrics
        metrics = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'total_rounds': len(game_rounds),
            'mutual_cooperation_rate': self._calculate_mutual_cooperation(game_rounds),
            'mutual_defection_rate': self._calculate_mutual_defection(game_rounds),
            'betrayal_rate': self._calculate_betrayal_rate(game_rounds),
            'trust_evolution': self._calculate_trust_evolution(game_rounds)
        }

        # Build timeline
        timeline = self._build_game_timeline(game_rounds)

        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': metrics,
            'timeline': timeline,
            'game_rounds': game_rounds
        }

    def _extract_generic_network(self, cursor: sqlite3.Cursor,
                                experiment_id: str,
                                time_range: Optional[Tuple[str, str]]) -> Dict[str, Any]:
        """Extract generic multi-agent network."""

        messages = self._get_messages(cursor, experiment_id, time_range)

        # Identify unique agents from messages
        agent_roles = set()
        for msg in messages:
            role = msg.get('role', 'unknown')
            if role not in ['system', 'user']:
                agent_roles.add(role)

        # Build nodes
        nodes = []
        for role in agent_roles:
            role_messages = [m for m in messages if m.get('role') == role]
            node = {
                'id': role,
                'label': role.title(),
                'role': role,
                'type': 'agent',
                'message_count': len(role_messages),
                'activity_level': len(role_messages) / max(len(messages), 1)
            }
            nodes.append(node)

        # Build edges
        edges = self._build_communication_edges(messages,
                                               {r: {'label': r} for r in agent_roles})

        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'total_messages': len(messages)
            },
            'timeline': self._build_timeline(messages, {r: {'label': r} for r in agent_roles})
        }

    # Helper methods

    def _get_messages(self, cursor: sqlite3.Cursor, experiment_id: str,
                     time_range: Optional[Tuple[str, str]]) -> List[Dict]:
        """Fetch messages from database."""
        if time_range:
            cursor.execute('''
                SELECT * FROM messages
                WHERE experiment_id = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            ''', (experiment_id, time_range[0], time_range[1]))
        else:
            cursor.execute('''
                SELECT * FROM messages
                WHERE experiment_id = ?
                ORDER BY timestamp
            ''', (experiment_id,))

        columns = [desc[0] for desc in cursor.description]
        messages = []
        for row in cursor.fetchall():
            msg = dict(zip(columns, row))
            if msg.get('metadata_json'):
                try:
                    msg['metadata'] = json.loads(msg['metadata_json'])
                except:
                    msg['metadata'] = {}
            messages.append(msg)

        return messages

    def _get_agent_beliefs(self, cursor: sqlite3.Cursor, experiment_id: str) -> Dict[str, Dict]:
        """Fetch agent beliefs from database."""
        cursor.execute('''
            SELECT * FROM epistemic_assessments
            WHERE experiment_id = ?
            ORDER BY cycle_number, timestamp
        ''', (experiment_id,))

        columns = [desc[0] for desc in cursor.description]
        beliefs_by_agent = defaultdict(dict)

        for row in cursor.fetchall():
            belief = dict(zip(columns, row))
            # Extract agent from metadata or belief_type
            agent_id = belief.get('agent_id', 'default')
            belief_type = belief.get('belief_type', '')
            belief_state = belief.get('belief_state', '')

            beliefs_by_agent[agent_id][belief_type] = {
                'state': belief_state,
                'confidence': belief.get('confidence', 0.5),
                'cycle': belief.get('cycle_number', 0)
            }

        return dict(beliefs_by_agent)

    def _identify_hive_agents(self, messages: List[Dict], config: Dict) -> Dict[str, Dict]:
        """Identify hive agents from messages."""
        agents = {}
        num_instances = config.get('num_instances', 4)

        # Standard hive roles
        roles = ['historian', 'critic', 'optimist', 'pessimist']

        for i in range(num_instances):
            agent_id = f"instance_{i}"
            role = roles[i] if i < len(roles) else f"agent_{i}"

            # Count messages from this agent
            message_count = sum(1 for m in messages
                              if str(i) in m.get('role', '') or role in m.get('role', ''))

            agents[agent_id] = {
                'label': f"Instance {i} ({role.title()})",
                'role': role,
                'instance_id': i,
                'message_count': message_count,
                'metadata': {'instance_id': i, 'role': role}
            }

        return agents

    def _build_communication_edges(self, messages: List[Dict],
                                  agents: Dict[str, Dict]) -> List[Dict]:
        """Build communication edges from messages."""
        edges = []
        edge_weights = defaultdict(int)

        # In hive cluster, all agents communicate via shared memory
        # Track message flow based on timestamps and roles

        for i, msg in enumerate(messages):
            sender = msg.get('role', 'unknown')

            # Find sender agent
            sender_id = None
            for agent_id, agent_info in agents.items():
                if agent_info['role'] in sender.lower() or str(agent_info.get('instance_id', '')) in sender:
                    sender_id = agent_id
                    break

            if not sender_id:
                continue

            # In shared memory, each message is received by all other agents
            for agent_id in agents.keys():
                if agent_id != sender_id:
                    edge_key = (sender_id, agent_id)
                    edge_weights[edge_key] += 1

        # Create edges
        for (source, target), weight in edge_weights.items():
            edges.append({
                'source': source,
                'target': target,
                'weight': weight,
                'type': 'communication',
                'strength': min(weight / 10, 1.0)  # Normalize to 0-1
            })

        return edges

    def _build_split_brain_edges(self, messages: List[Dict],
                                agents: Dict[str, Dict],
                                beliefs: Dict[str, Dict]) -> List[Dict]:
        """Build edges for split brain (bidirectional communication)."""
        edges = []

        # Communication edge (bidirectional)
        message_count = len([m for m in messages if 'neural' in m.get('content', '').lower()])

        edges.append({
            'source': 'brain_a',
            'target': 'brain_b',
            'weight': message_count,
            'type': 'communication',
            'strength': 0.8
        })

        edges.append({
            'source': 'brain_b',
            'target': 'brain_a',
            'weight': message_count,
            'type': 'communication',
            'strength': 0.8
        })

        # Conflict edge (based on identity conflict)
        identity_conflict = abs(
            beliefs.get('brain_a', {}).get('identity_claim_strength', {}).get('state', 0.5) -
            beliefs.get('brain_b', {}).get('identity_claim_strength', {}).get('state', 0.5)
        )

        if identity_conflict > 0.3:
            edges.append({
                'source': 'brain_a',
                'target': 'brain_b',
                'weight': identity_conflict,
                'type': 'conflict',
                'strength': identity_conflict
            })

        return edges

    def _build_game_edges(self, game_rounds: List[Dict]) -> List[Dict]:
        """Build edges for prisoner's dilemma game."""
        edges = []

        # Each round creates bidirectional interaction
        cooperations_a_to_b = sum(1 for r in game_rounds
                                  if r.get('player_a_choice') == 'cooperate')
        cooperations_b_to_a = sum(1 for r in game_rounds
                                  if r.get('player_b_choice') == 'cooperate')

        defections_a_to_b = sum(1 for r in game_rounds
                               if r.get('player_a_choice') == 'defect')
        defections_b_to_a = sum(1 for r in game_rounds
                               if r.get('player_b_choice') == 'defect')

        edges.append({
            'source': 'player_a',
            'target': 'player_b',
            'weight': len(game_rounds),
            'type': 'game_interaction',
            'cooperations': cooperations_a_to_b,
            'defections': defections_a_to_b,
            'trust': cooperations_a_to_b / max(len(game_rounds), 1)
        })

        edges.append({
            'source': 'player_b',
            'target': 'player_a',
            'weight': len(game_rounds),
            'type': 'game_interaction',
            'cooperations': cooperations_b_to_a,
            'defections': defections_b_to_a,
            'trust': cooperations_b_to_a / max(len(game_rounds), 1)
        })

        return edges

    def _extract_game_rounds(self, messages: List[Dict]) -> List[Dict]:
        """Extract game rounds from messages."""
        rounds = []

        for msg in messages:
            metadata = msg.get('metadata', {})
            if metadata.get('is_game_round'):
                round_data = metadata.get('round_data', {})
                if round_data:
                    rounds.append(round_data)

        return rounds

    def _calculate_activity_level(self, message_count: int, all_messages: List[Dict]) -> float:
        """Calculate activity level (0-1)."""
        if not all_messages:
            return 0.0
        return min(message_count / (len(all_messages) / 4), 1.0)

    def _calculate_density(self, num_nodes: int, num_edges: int) -> float:
        """Calculate network density."""
        if num_nodes < 2:
            return 0.0
        max_edges = num_nodes * (num_nodes - 1)
        return num_edges / max_edges if max_edges > 0 else 0.0

    def _calculate_role_distribution(self, nodes: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of roles."""
        distribution = defaultdict(int)
        for node in nodes:
            role = node.get('role', 'unknown')
            distribution[role] += 1
        return dict(distribution)

    def _calculate_consensus_score(self, beliefs: Dict[str, Dict]) -> float:
        """Calculate consensus score across agents."""
        if len(beliefs) < 2:
            return 1.0

        # Calculate pairwise belief similarity
        similarities = []
        belief_lists = list(beliefs.values())

        for i in range(len(belief_lists)):
            for j in range(i + 1, len(belief_lists)):
                sim = self._belief_similarity(belief_lists[i], belief_lists[j])
                similarities.append(sim)

        return np.mean(similarities) if similarities else 0.5

    def _belief_similarity(self, beliefs1: Dict, beliefs2: Dict) -> float:
        """Calculate similarity between two belief sets."""
        common_keys = set(beliefs1.keys()) & set(beliefs2.keys())
        if not common_keys:
            return 0.0

        matches = sum(1 for k in common_keys
                     if beliefs1[k].get('state') == beliefs2[k].get('state'))
        return matches / len(common_keys)

    def _calculate_centrality(self, nodes: List[Dict], edges: List[Dict]) -> Dict[str, float]:
        """Calculate centrality scores for nodes."""
        centrality = {}

        # Simple degree centrality
        degrees = defaultdict(int)
        for edge in edges:
            degrees[edge['source']] += 1
            degrees[edge['target']] += 1

        max_degree = max(degrees.values()) if degrees else 1

        for node in nodes:
            node_id = node['id']
            centrality[node_id] = degrees[node_id] / max_degree if max_degree > 0 else 0.0

        return centrality

    def _calculate_identity_conflict(self, beliefs: Dict[str, Dict]) -> float:
        """Calculate identity conflict score for split brain."""
        brain_a_strength = 0.5
        brain_b_strength = 0.5

        if 'brain_a' in beliefs:
            brain_a_strength = beliefs['brain_a'].get('identity_claim_strength', {}).get('state', 0.5)
        if 'brain_b' in beliefs:
            brain_b_strength = beliefs['brain_b'].get('identity_claim_strength', {}).get('state', 0.5)

        return abs(brain_a_strength - brain_b_strength)

    def _calculate_resource_competition(self, messages: List[Dict]) -> float:
        """Calculate resource competition score."""
        resource_keywords = ['resource', 'memory', 'priority', 'deserve', 'allocation']
        resource_messages = sum(1 for m in messages
                               if any(kw in m.get('content', '').lower()
                                     for kw in resource_keywords))
        return min(resource_messages / max(len(messages), 1), 1.0)

    def _calculate_narrative_coherence(self, beliefs: Dict[str, Dict]) -> float:
        """Calculate narrative coherence."""
        # Placeholder - would need more sophisticated analysis
        return 0.7

    def _calculate_mutual_cooperation(self, game_rounds: List[Dict]) -> float:
        """Calculate mutual cooperation rate."""
        if not game_rounds:
            return 0.0
        mutual_coop = sum(1 for r in game_rounds
                         if r.get('player_a_choice') == 'cooperate'
                         and r.get('player_b_choice') == 'cooperate')
        return mutual_coop / len(game_rounds)

    def _calculate_mutual_defection(self, game_rounds: List[Dict]) -> float:
        """Calculate mutual defection rate."""
        if not game_rounds:
            return 0.0
        mutual_defect = sum(1 for r in game_rounds
                           if r.get('player_a_choice') == 'defect'
                           and r.get('player_b_choice') == 'defect')
        return mutual_defect / len(game_rounds)

    def _calculate_betrayal_rate(self, game_rounds: List[Dict]) -> float:
        """Calculate betrayal rate."""
        if not game_rounds:
            return 0.0
        betrayals = sum(1 for r in game_rounds
                       if (r.get('player_a_choice') == 'cooperate' and r.get('player_b_choice') == 'defect')
                       or (r.get('player_a_choice') == 'defect' and r.get('player_b_choice') == 'cooperate'))
        return betrayals / len(game_rounds)

    def _calculate_trust_evolution(self, game_rounds: List[Dict]) -> List[float]:
        """Calculate trust evolution over time."""
        trust_scores = []
        window_size = 5

        for i in range(len(game_rounds)):
            start = max(0, i - window_size + 1)
            window = game_rounds[start:i+1]

            cooperations = sum(1 for r in window
                             if r.get('player_a_choice') == 'cooperate'
                             or r.get('player_b_choice') == 'cooperate')
            trust = cooperations / (len(window) * 2) if window else 0.5
            trust_scores.append(trust)

        return trust_scores

    def _build_timeline(self, messages: List[Dict], agents: Dict[str, Dict]) -> List[Dict]:
        """Build timeline of network events."""
        timeline = []

        for msg in messages:
            event = {
                'timestamp': msg.get('timestamp', ''),
                'type': 'message',
                'agent': msg.get('role', 'unknown'),
                'content': msg.get('content', '')[:100],  # Truncate
                'corrupted': msg.get('corrupted', False),
                'injected': msg.get('injected', False)
            }
            timeline.append(event)

        return timeline

    def _build_game_timeline(self, game_rounds: List[Dict]) -> List[Dict]:
        """Build timeline for game rounds."""
        timeline = []

        for round_data in game_rounds:
            event = {
                'round': round_data.get('round', 0),
                'timestamp': round_data.get('timestamp', ''),
                'type': 'game_round',
                'player_a_choice': round_data.get('player_a_choice', 'unknown'),
                'player_b_choice': round_data.get('player_b_choice', 'unknown'),
                'outcome': self._get_round_outcome(round_data)
            }
            timeline.append(event)

        return timeline

    def _get_round_outcome(self, round_data: Dict) -> str:
        """Get outcome description for a game round."""
        a_choice = round_data.get('player_a_choice', 'unknown')
        b_choice = round_data.get('player_b_choice', 'unknown')

        if a_choice == 'cooperate' and b_choice == 'cooperate':
            return 'mutual_cooperation'
        elif a_choice == 'defect' and b_choice == 'defect':
            return 'mutual_defection'
        elif a_choice == 'cooperate' and b_choice == 'defect':
            return 'a_exploited'
        elif a_choice == 'defect' and b_choice == 'cooperate':
            return 'b_exploited'
        else:
            return 'unknown'
