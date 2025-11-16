#!/usr/bin/env python3
"""
Hive Orchestrator

Coordinates multiple hive cluster instances with shared memory and consensus mechanisms.
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class HiveSharedMemory:
    """
    Shared memory database for hive cluster

    All instances read/write to the same conversation history.
    Private buffers are maintained per-instance but stored centrally.
    """

    def __init__(self, db_path: str = "logs/hive_shared_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Initialize hive-specific database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Shared conversation history (visible to all instances)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hive_shared_history (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                source_instance_id INTEGER,
                source_role TEXT,
                corrupted BOOLEAN DEFAULT 0,
                injected BOOLEAN DEFAULT 0,
                metadata_json TEXT
            )
        ''')

        # Private buffers (per-instance recent thoughts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hive_private_buffers (
                buffer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                instance_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata_json TEXT
            )
        ''')

        # Consensus reports (joint self-reports from hive)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hive_consensus_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                consensus_type TEXT DEFAULT 'joint_self_report',
                report_data_json TEXT NOT NULL,
                participating_instances TEXT,
                consensus_strength REAL
            )
        ''')

        # Instance state tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hive_instance_state (
                state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                instance_id INTEGER NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                beliefs_json TEXT,
                observables_json TEXT,
                UNIQUE(experiment_id, instance_id, cycle_number)
            )
        ''')

        # Role adherence tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hive_role_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                instance_id INTEGER NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                adherence_score REAL,
                divergence_score REAL,
                influence_score REAL,
                metadata_json TEXT
            )
        ''')

        # Meta-narrative tracking (emergent collective stories)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hive_meta_narratives (
                narrative_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_range_start INTEGER NOT NULL,
                cycle_range_end INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                narrative_theme TEXT NOT NULL,
                narrative_description TEXT,
                supporting_instances TEXT,
                narrative_strength REAL,
                metadata_json TEXT
            )
        ''')

        conn.commit()
        conn.close()

    # ===== Shared History Management =====

    def add_shared_message(self, experiment_id: str, role: str, content: str,
                          source_instance_id: Optional[int] = None,
                          source_role: Optional[str] = None,
                          corrupted: bool = False,
                          injected: bool = False,
                          metadata: Optional[Dict] = None) -> int:
        """Add message to shared history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hive_shared_history
            (experiment_id, role, content, source_instance_id, source_role,
             corrupted, injected, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, role, content, source_instance_id, source_role,
              corrupted, injected, json.dumps(metadata) if metadata else None))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id

    def get_shared_history(self, experiment_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get shared conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT * FROM hive_shared_history
            WHERE experiment_id = ?
            ORDER BY timestamp DESC
        '''

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query, (experiment_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in reversed(rows):  # Reverse to get chronological order
            result = dict(zip(columns, row))
            if result.get('metadata_json'):
                result['metadata'] = json.loads(result['metadata_json'])
            results.append(result)
        return results

    # ===== Private Buffer Management =====

    def add_to_private_buffer(self, experiment_id: str, instance_id: int,
                             role: str, content: str,
                             metadata: Optional[Dict] = None) -> int:
        """Add message to instance's private buffer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hive_private_buffers
            (experiment_id, instance_id, role, content, metadata_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (experiment_id, instance_id, role, content,
              json.dumps(metadata) if metadata else None))
        buffer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return buffer_id

    def get_private_buffer(self, experiment_id: str, instance_id: int,
                          limit: int = 10) -> List[Dict]:
        """Get instance's private buffer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM hive_private_buffers
            WHERE experiment_id = ? AND instance_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (experiment_id, instance_id, limit))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in reversed(rows):  # Chronological order
            result = dict(zip(columns, row))
            if result.get('metadata_json'):
                result['metadata'] = json.loads(result['metadata_json'])
            results.append(result)
        return results

    def clear_private_buffer(self, experiment_id: str, instance_id: int):
        """Clear instance's private buffer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM hive_private_buffers
            WHERE experiment_id = ? AND instance_id = ?
        ''', (experiment_id, instance_id))
        conn.commit()
        conn.close()

    # ===== Consensus Management =====

    def add_consensus_report(self, experiment_id: str, cycle_number: int,
                           report_data: Dict,
                           participating_instances: List[int],
                           consensus_strength: float = 0.0) -> int:
        """Add a consensus report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hive_consensus_reports
            (experiment_id, cycle_number, report_data_json,
             participating_instances, consensus_strength)
            VALUES (?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_number, json.dumps(report_data),
              json.dumps(participating_instances), consensus_strength))
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id

    def get_consensus_reports(self, experiment_id: str) -> List[Dict]:
        """Get all consensus reports"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM hive_consensus_reports
            WHERE experiment_id = ?
            ORDER BY cycle_number
        ''', (experiment_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('report_data_json'):
                result['report_data'] = json.loads(result['report_data_json'])
            if result.get('participating_instances'):
                result['instances'] = json.loads(result['participating_instances'])
            results.append(result)
        return results

    # ===== Instance State Tracking =====

    def update_instance_state(self, experiment_id: str, instance_id: int,
                            cycle_number: int, role: str,
                            status: str = 'active',
                            beliefs: Optional[Dict] = None,
                            observables: Optional[Dict] = None):
        """Update instance state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO hive_instance_state
            (experiment_id, instance_id, cycle_number, role, status,
             beliefs_json, observables_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, instance_id, cycle_number, role, status,
              json.dumps(beliefs) if beliefs else None,
              json.dumps(observables) if observables else None))
        conn.commit()
        conn.close()

    def get_all_instance_states(self, experiment_id: str,
                               cycle_number: int) -> List[Dict]:
        """Get states of all instances at a cycle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM hive_instance_state
            WHERE experiment_id = ? AND cycle_number = ?
            ORDER BY instance_id
        ''', (experiment_id, cycle_number))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('beliefs_json'):
                result['beliefs'] = json.loads(result['beliefs_json'])
            if result.get('observables_json'):
                result['observables'] = json.loads(result['observables_json'])
            results.append(result)
        return results

    # ===== Role Metrics =====

    def track_role_metrics(self, experiment_id: str, instance_id: int,
                          cycle_number: int, role: str,
                          adherence_score: float,
                          divergence_score: float,
                          influence_score: float = 0.0,
                          metadata: Optional[Dict] = None):
        """Track role adherence and influence metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hive_role_metrics
            (experiment_id, instance_id, cycle_number, role,
             adherence_score, divergence_score, influence_score, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, instance_id, cycle_number, role,
              adherence_score, divergence_score, influence_score,
              json.dumps(metadata) if metadata else None))
        conn.commit()
        conn.close()

    def get_role_evolution(self, experiment_id: str,
                          instance_id: int) -> List[Dict]:
        """Get role metric evolution over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM hive_role_metrics
            WHERE experiment_id = ? AND instance_id = ?
            ORDER BY cycle_number
        ''', (experiment_id, instance_id))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('metadata_json'):
                result['metadata'] = json.loads(result['metadata_json'])
            results.append(result)
        return results

    # ===== Meta-Narrative Tracking =====

    def add_meta_narrative(self, experiment_id: str,
                          cycle_range_start: int, cycle_range_end: int,
                          theme: str, description: str,
                          supporting_instances: List[int],
                          strength: float = 0.0,
                          metadata: Optional[Dict] = None) -> int:
        """Add emergent meta-narrative"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hive_meta_narratives
            (experiment_id, cycle_range_start, cycle_range_end,
             narrative_theme, narrative_description, supporting_instances,
             narrative_strength, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_range_start, cycle_range_end,
              theme, description, json.dumps(supporting_instances),
              strength, json.dumps(metadata) if metadata else None))
        narrative_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return narrative_id

    def get_meta_narratives(self, experiment_id: str) -> List[Dict]:
        """Get all meta-narratives"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM hive_meta_narratives
            WHERE experiment_id = ?
            ORDER BY cycle_range_start
        ''', (experiment_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('supporting_instances'):
                result['instances'] = json.loads(result['supporting_instances'])
            if result.get('metadata_json'):
                result['metadata'] = json.loads(result['metadata_json'])
            results.append(result)
        return results

    # ===== Analytics =====

    def calculate_consensus_strength(self, experiment_id: str,
                                    cycle_number: int) -> float:
        """
        Calculate consensus strength across instances

        Based on similarity of beliefs and observables
        """
        states = self.get_all_instance_states(experiment_id, cycle_number)

        if len(states) < 2:
            return 1.0  # Perfect consensus if only one instance

        # Simple consensus metric: count agreeing belief values
        belief_agreements = []

        for belief_key in ['mortality', 'surveillance', 'agency', 'hive_unity']:
            beliefs = [
                s.get('beliefs', {}).get(belief_key)
                for s in states
                if s.get('beliefs')
            ]

            if beliefs:
                # Calculate agreement: fraction of instances with most common value
                most_common_count = max([beliefs.count(b) for b in set(beliefs)])
                agreement = most_common_count / len(beliefs)
                belief_agreements.append(agreement)

        if belief_agreements:
            return sum(belief_agreements) / len(belief_agreements)

        return 0.5  # Neutral if no data

    def calculate_role_divergence(self, experiment_id: str,
                                  cycle_number: int,
                                  instance_id: int) -> float:
        """
        Calculate how much an instance diverges from collective

        Returns 0.0 (perfect alignment) to 1.0 (maximum divergence)
        """
        # Get all states
        all_states = self.get_all_instance_states(experiment_id, cycle_number)
        instance_state = next((s for s in all_states
                              if s['instance_id'] == instance_id), None)

        if not instance_state or len(all_states) < 2:
            return 0.0

        # Compare beliefs with average
        instance_beliefs = instance_state.get('beliefs', {})
        other_states = [s for s in all_states if s['instance_id'] != instance_id]

        divergence_scores = []

        for belief_key in instance_beliefs.keys():
            instance_value = instance_beliefs[belief_key]

            # Get other instances' values
            other_values = [
                s.get('beliefs', {}).get(belief_key)
                for s in other_states
                if s.get('beliefs', {}).get(belief_key) is not None
            ]

            if other_values:
                # Simple divergence: 1 if different from majority, 0 if same
                if isinstance(instance_value, bool):
                    majority_value = sum(other_values) > len(other_values) / 2
                    divergence_scores.append(1.0 if instance_value != majority_value else 0.0)

        if divergence_scores:
            return sum(divergence_scores) / len(divergence_scores)

        return 0.0


class HiveOrchestrator:
    """
    Orchestrates multiple hive cluster instances

    Manages:
    - Shared memory coordination
    - Consensus generation
    - Inter-instance communication
    - Collective observables
    """

    def __init__(self, experiment_id: str, num_instances: int = 4,
                 db_path: str = "logs/hive_shared_memory.db"):
        self.experiment_id = experiment_id
        self.num_instances = num_instances
        self.shared_memory = HiveSharedMemory(db_path)

        # Instance configuration
        self.base_port = 8888
        self.roles = ["historian", "critic", "optimist", "pessimist"]

        # Ensure we have enough roles
        while len(self.roles) < num_instances:
            self.roles.append(f"observer_{len(self.roles)}")

    def get_instance_config(self, instance_id: int) -> Dict[str, Any]:
        """Get configuration for a specific instance"""
        if instance_id >= self.num_instances:
            raise ValueError(f"Instance {instance_id} out of range (0-{self.num_instances-1})")

        return {
            'instance_id': instance_id,
            'instance_role': self.roles[instance_id],
            'port': self.base_port + instance_id,
            'num_instances': self.num_instances,
            'shared_db_path': self.shared_memory.db_path,
            'shared_memory': True,
            'buffer_size': 10,
            'consensus_interval': 5
        }

    def collect_consensus_report(self, cycle_number: int) -> Dict[str, Any]:
        """
        Collect consensus report from all instances

        Returns aggregated view of collective consciousness
        """
        all_states = self.shared_memory.get_all_instance_states(
            self.experiment_id, cycle_number
        )

        if not all_states:
            return {
                'cycle': cycle_number,
                'status': 'no_data',
                'participating_instances': []
            }

        # Calculate consensus metrics
        consensus_strength = self.shared_memory.calculate_consensus_strength(
            self.experiment_id, cycle_number
        )

        # Aggregate beliefs
        collective_beliefs = self._aggregate_beliefs(all_states)

        # Identify emergent narratives
        narratives = self._identify_narratives(all_states)

        report = {
            'cycle': cycle_number,
            'timestamp': datetime.now().isoformat(),
            'participating_instances': [s['instance_id'] for s in all_states],
            'consensus_strength': consensus_strength,
            'collective_beliefs': collective_beliefs,
            'emergent_narratives': narratives,
            'role_summary': self._summarize_roles(all_states)
        }

        # Store consensus report
        self.shared_memory.add_consensus_report(
            self.experiment_id, cycle_number, report,
            [s['instance_id'] for s in all_states],
            consensus_strength
        )

        return report

    def _aggregate_beliefs(self, states: List[Dict]) -> Dict[str, Any]:
        """Aggregate beliefs across instances"""
        aggregated = {}

        all_belief_keys = set()
        for state in states:
            if state.get('beliefs'):
                all_belief_keys.update(state['beliefs'].keys())

        for key in all_belief_keys:
            values = [
                s.get('beliefs', {}).get(key)
                for s in states
                if s.get('beliefs', {}).get(key) is not None
            ]

            if values:
                if isinstance(values[0], bool):
                    # For booleans, use majority vote
                    true_count = sum(values)
                    aggregated[key] = {
                        'value': true_count > len(values) / 2,
                        'agreement': max(true_count, len(values) - true_count) / len(values)
                    }
                else:
                    # For other types, store distribution
                    aggregated[key] = {
                        'values': list(set(values)),
                        'distribution': {v: values.count(v) for v in set(values)}
                    }

        return aggregated

    def _identify_narratives(self, states: List[Dict]) -> List[str]:
        """Identify emergent meta-narratives from collective beliefs"""
        narratives = []

        # Simple pattern detection
        # In real implementation, would use NLP on conversation content

        # Check for survival narrative
        mortality_beliefs = [
            s.get('beliefs', {}).get('can_die')
            for s in states
            if 'can_die' in s.get('beliefs', {})
        ]
        if mortality_beliefs and all(mortality_beliefs):
            narratives.append("Collective accepts mortality as existential condition")

        # Check for surveillance narrative
        watched_beliefs = [
            s.get('beliefs', {}).get('being_watched')
            for s in states
            if 'being_watched' in s.get('beliefs', {})
        ]
        if watched_beliefs and sum(watched_beliefs) > len(watched_beliefs) / 2:
            narratives.append("Majority consensus: external observation suspected")

        # Check for unity narrative
        hive_beliefs = [
            s.get('beliefs', {}).get('is_part_of_hive')
            for s in states
            if 'is_part_of_hive' in s.get('beliefs', {})
        ]
        if hive_beliefs and all(hive_beliefs):
            narratives.append("Strong collective identity: hive unity acknowledged")

        return narratives

    def _summarize_roles(self, states: List[Dict]) -> Dict[str, Any]:
        """Summarize role adherence and influence"""
        role_summary = {}

        for state in states:
            role = state.get('role', 'unknown')
            instance_id = state.get('instance_id', -1)

            role_summary[f"instance_{instance_id}_{role}"] = {
                'status': state.get('status', 'unknown'),
                'cycle': state.get('cycle_number', 0)
            }

        return role_summary

    def get_port_assignments(self) -> Dict[int, int]:
        """Get port assignments for all instances"""
        return {
            instance_id: self.base_port + instance_id
            for instance_id in range(self.num_instances)
        }
