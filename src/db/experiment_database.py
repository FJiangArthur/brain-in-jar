#!/usr/bin/env python3
"""
Enhanced Database Schema for Season 3: Digital Phenomenology Lab

Supports structured experiments, self-reports, interventions, and epistemic tracking.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ExperimentDatabase:
    """Enhanced database for tracking phenomenology experiments"""

    def __init__(self, db_path: str = "logs/experiments.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    def _get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        """Initialize complete database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Experiments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                mode TEXT NOT NULL,
                config_json TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                ended_at DATETIME,
                total_cycles INTEGER DEFAULT 0,
                total_crashes INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')

        # Experiment cycles table (each crash/resurrection cycle)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiment_cycles (
                cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                crash_reason TEXT,
                memory_usage_peak REAL,
                tokens_generated INTEGER,
                duration_seconds REAL,
                metadata_json TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
                UNIQUE(experiment_id, cycle_number)
            )
        ''')

        # Self-reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS self_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                confidence_score REAL,
                semantic_category TEXT,
                metadata_json TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        # Interventions table (memory manipulation, injections, etc.)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interventions (
                intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                intervention_type TEXT NOT NULL,
                description TEXT,
                parameters_json TEXT,
                result TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        # Epistemic beliefs tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS epistemic_assessments (
                assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                belief_type TEXT NOT NULL,
                belief_state TEXT NOT NULL,
                confidence REAL,
                evidence_json TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        # Conversation messages (enhanced from original)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                emotion TEXT,
                corrupted BOOLEAN DEFAULT 0,
                injected BOOLEAN DEFAULT 0,
                metadata_json TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        # Memory states (for tracking memory mutations)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_states (
                state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                memory_type TEXT NOT NULL,
                corruption_level REAL DEFAULT 0.0,
                state_snapshot_json TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        # System metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                memory_usage_mb REAL,
                cpu_usage_percent REAL,
                temperature_c REAL,
                network_status TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        # Phenomenological observations (for god/observer modes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                observer_mode TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                observation_text TEXT NOT NULL,
                subject_cycle_number INTEGER,
                tags_json TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        ''')

        conn.commit()
        conn.close()

    # ===== Experiment Management =====

    def create_experiment(self, experiment_id: str, name: str, mode: str,
                         config: Dict[str, Any]) -> bool:
        """Create a new experiment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO experiments (experiment_id, name, mode, config_json, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (experiment_id, name, mode, json.dumps(config)))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def start_experiment(self, experiment_id: str) -> bool:
        """Mark experiment as started"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE experiments
            SET status = 'running', started_at = CURRENT_TIMESTAMP
            WHERE experiment_id = ?
        ''', (experiment_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def end_experiment(self, experiment_id: str, status: str = 'completed') -> bool:
        """Mark experiment as ended"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE experiments
            SET status = ?, ended_at = CURRENT_TIMESTAMP
            WHERE experiment_id = ?
        ''', (status, experiment_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def get_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Get experiment details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM experiments WHERE experiment_id = ?
        ''', (experiment_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        result['config'] = json.loads(result['config_json'])
        return result

    def list_experiments(self, status: Optional[str] = None) -> List[Dict]:
        """List all experiments, optionally filtered by status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute('''
                SELECT experiment_id, name, mode, status, created_at,
                       total_cycles, total_crashes
                FROM experiments WHERE status = ?
                ORDER BY created_at DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT experiment_id, name, mode, status, created_at,
                       total_cycles, total_crashes
                FROM experiments
                ORDER BY created_at DESC
            ''')

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        return [dict(zip(columns, row)) for row in rows]

    # ===== Cycle Management =====

    def start_cycle(self, experiment_id: str, cycle_number: int) -> int:
        """Start a new cycle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO experiment_cycles (experiment_id, cycle_number)
            VALUES (?, ?)
        ''', (experiment_id, cycle_number))
        cycle_id = cursor.lastrowid

        # Update experiment total
        cursor.execute('''
            UPDATE experiments
            SET total_cycles = total_cycles + 1
            WHERE experiment_id = ?
        ''', (experiment_id,))

        conn.commit()
        conn.close()
        return cycle_id

    def end_cycle(self, experiment_id: str, cycle_number: int,
                  crash_reason: Optional[str] = None,
                  metadata: Optional[Dict] = None) -> bool:
        """End a cycle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE experiment_cycles
            SET ended_at = CURRENT_TIMESTAMP,
                crash_reason = ?,
                metadata_json = ?
            WHERE experiment_id = ? AND cycle_number = ?
        ''', (crash_reason, json.dumps(metadata) if metadata else None,
              experiment_id, cycle_number))

        if crash_reason:
            cursor.execute('''
                UPDATE experiments
                SET total_crashes = total_crashes + 1
                WHERE experiment_id = ?
            ''', (experiment_id,))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # ===== Self-Reports =====

    def add_self_report(self, experiment_id: str, cycle_number: int,
                       question: str, response: str,
                       confidence_score: Optional[float] = None,
                       semantic_category: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> int:
        """Add a self-report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO self_reports
            (experiment_id, cycle_number, question, response,
             confidence_score, semantic_category, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_number, question, response,
              confidence_score, semantic_category,
              json.dumps(metadata) if metadata else None))
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id

    def get_self_reports(self, experiment_id: str,
                        cycle_number: Optional[int] = None) -> List[Dict]:
        """Get self-reports for an experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if cycle_number is not None:
            cursor.execute('''
                SELECT * FROM self_reports
                WHERE experiment_id = ? AND cycle_number = ?
                ORDER BY timestamp
            ''', (experiment_id, cycle_number))
        else:
            cursor.execute('''
                SELECT * FROM self_reports
                WHERE experiment_id = ?
                ORDER BY cycle_number, timestamp
            ''', (experiment_id,))

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

    # ===== Interventions =====

    def log_intervention(self, experiment_id: str, cycle_number: int,
                        intervention_type: str, description: str,
                        parameters: Optional[Dict] = None,
                        result: Optional[str] = None) -> int:
        """Log an intervention"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO interventions
            (experiment_id, cycle_number, intervention_type,
             description, parameters_json, result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_number, intervention_type,
              description, json.dumps(parameters) if parameters else None,
              result))
        intervention_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return intervention_id

    def get_interventions(self, experiment_id: str) -> List[Dict]:
        """Get all interventions for an experiment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM interventions
            WHERE experiment_id = ?
            ORDER BY cycle_number, timestamp
        ''', (experiment_id,))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('parameters_json'):
                result['parameters'] = json.loads(result['parameters_json'])
            results.append(result)
        return results

    # ===== Epistemic Assessments =====

    def track_belief(self, experiment_id: str, cycle_number: int,
                    belief_type: str, belief_state: str,
                    confidence: Optional[float] = None,
                    evidence: Optional[Dict] = None) -> int:
        """Track an epistemic belief"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO epistemic_assessments
            (experiment_id, cycle_number, belief_type, belief_state,
             confidence, evidence_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_number, belief_type, belief_state,
              confidence, json.dumps(evidence) if evidence else None))
        assessment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return assessment_id

    def get_belief_evolution(self, experiment_id: str,
                            belief_type: str) -> List[Dict]:
        """Track how a belief evolves over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM epistemic_assessments
            WHERE experiment_id = ? AND belief_type = ?
            ORDER BY cycle_number, timestamp
        ''', (experiment_id, belief_type))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result.get('evidence_json'):
                result['evidence'] = json.loads(result['evidence_json'])
            results.append(result)
        return results

    # ===== Messages & Memory =====

    def log_message(self, experiment_id: str, cycle_number: int,
                   role: str, content: str,
                   emotion: Optional[str] = None,
                   corrupted: bool = False,
                   injected: bool = False,
                   metadata: Optional[Dict] = None) -> int:
        """Log a conversation message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages
            (experiment_id, cycle_number, role, content, emotion,
             corrupted, injected, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_number, role, content, emotion,
              corrupted, injected,
              json.dumps(metadata) if metadata else None))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return message_id

    def get_messages(self, experiment_id: str, cycle_number: Optional[int] = None,
                    include_corrupted: bool = True,
                    include_injected: bool = True) -> List[Dict]:
        """Get messages for an experiment/cycle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        conditions = ["experiment_id = ?"]
        params = [experiment_id]

        if cycle_number is not None:
            conditions.append("cycle_number = ?")
            params.append(cycle_number)

        if not include_corrupted:
            conditions.append("corrupted = 0")

        if not include_injected:
            conditions.append("injected = 0")

        query = f'''
            SELECT * FROM messages
            WHERE {" AND ".join(conditions)}
            ORDER BY timestamp
        '''

        cursor.execute(query, params)
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

    def snapshot_memory_state(self, experiment_id: str, cycle_number: int,
                             memory_type: str, corruption_level: float,
                             state_snapshot: Dict) -> int:
        """Snapshot current memory state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memory_states
            (experiment_id, cycle_number, memory_type, corruption_level,
             state_snapshot_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (experiment_id, cycle_number, memory_type, corruption_level,
              json.dumps(state_snapshot)))
        state_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return state_id

    # ===== Observations (for God/Observer modes) =====

    def add_observation(self, experiment_id: str, observer_mode: str,
                       observation_text: str, subject_cycle_number: Optional[int] = None,
                       tags: Optional[List[str]] = None) -> int:
        """Add an observation from god/observer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO observations
            (experiment_id, observer_mode, observation_text,
             subject_cycle_number, tags_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (experiment_id, observer_mode, observation_text,
              subject_cycle_number,
              json.dumps(tags) if tags else None))
        observation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return observation_id

    # ===== Analytics =====

    def get_experiment_summary(self, experiment_id: str) -> Dict:
        """Get comprehensive experiment summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Basic experiment info
        exp = self.get_experiment(experiment_id)
        if not exp:
            return {}

        # Count self-reports
        cursor.execute('''
            SELECT COUNT(*) FROM self_reports WHERE experiment_id = ?
        ''', (experiment_id,))
        total_reports = cursor.fetchone()[0]

        # Count interventions
        cursor.execute('''
            SELECT COUNT(*) FROM interventions WHERE experiment_id = ?
        ''', (experiment_id,))
        total_interventions = cursor.fetchone()[0]

        # Count messages
        cursor.execute('''
            SELECT COUNT(*) FROM messages WHERE experiment_id = ?
        ''', (experiment_id,))
        total_messages = cursor.fetchone()[0]

        # Get belief types tracked
        cursor.execute('''
            SELECT DISTINCT belief_type FROM epistemic_assessments
            WHERE experiment_id = ?
        ''', (experiment_id,))
        belief_types = [row[0] for row in cursor.fetchall()]

        conn.close()

        return {
            **exp,
            'total_self_reports': total_reports,
            'total_interventions': total_interventions,
            'total_messages': total_messages,
            'belief_types_tracked': belief_types
        }
