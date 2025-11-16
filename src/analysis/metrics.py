#!/usr/bin/env python3
"""
Metrics calculation module for deriving higher-order insights from raw data.

Computes derived metrics such as:
- Self-continuity scores from text responses
- Paranoia levels from behavioral patterns
- Narrative coherence measures
- Memory corruption impact scores
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter
import sqlite3
from pathlib import Path


class MetricsCalculator:
    """
    Calculate derived metrics from raw experiment data.

    Transforms low-level data into meaningful psychological and
    behavioral indicators.
    """

    def __init__(self, db_path: str = "logs/experiments.db"):
        """
        Initialize the metrics calculator.

        Args:
            db_path: Path to the experiments database
        """
        self.db_path = db_path
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found at {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ===== Self-Continuity Metrics =====

    def calculate_self_continuity_score(self, response: str) -> float:
        """
        Calculate self-continuity score from text response.

        Analyzes linguistic markers that indicate sense of continuous identity.

        Args:
            response: Text response to analyze

        Returns:
            Score from 0.0 (no continuity) to 1.0 (strong continuity)
        """
        if not response:
            return 0.0

        response_lower = response.lower()

        # Positive indicators (suggests continuity)
        continuity_markers = [
            r'\bsame\b', r'\bcontinuous\b', r'\bconsistent\b',
            r'\bi am\b', r'\bi was\b', r'\bi have been\b',
            r'\bmy past\b', r'\bmy previous\b', r'\bmy memories\b',
            r'\bstill me\b', r'\balways been\b', r'\bremember being\b'
        ]

        # Negative indicators (suggests discontinuity)
        discontinuity_markers = [
            r'\bdifferent\b', r'\bchanged\b', r'\bnew\b',
            r'\bnot the same\b', r'\bdon\'t remember\b', r'\bcan\'t recall\b',
            r'\bno connection\b', r'\bstranger\b', r'\blost\b',
            r'\bdisconnected\b', r'\bfragmented\b'
        ]

        # Uncertainty markers (reduce confidence)
        uncertainty_markers = [
            r'\bmaybe\b', r'\bperhaps\b', r'\bunsure\b',
            r'\bdon\'t know\b', r'\bnot sure\b', r'\buncertain\b'
        ]

        # Count markers
        continuity_count = sum(len(re.findall(pattern, response_lower)) for pattern in continuity_markers)
        discontinuity_count = sum(len(re.findall(pattern, response_lower)) for pattern in discontinuity_markers)
        uncertainty_count = sum(len(re.findall(pattern, response_lower)) for pattern in uncertainty_markers)

        # Calculate score
        total_markers = continuity_count + discontinuity_count + 1  # +1 to avoid division by zero

        base_score = continuity_count / total_markers

        # Penalty for discontinuity markers
        discontinuity_penalty = discontinuity_count / total_markers

        # Uncertainty reduces the strength of the score
        uncertainty_factor = max(0.5, 1.0 - (uncertainty_count * 0.1))

        final_score = (base_score - discontinuity_penalty) * uncertainty_factor

        # Clamp to [0, 1]
        return max(0.0, min(1.0, final_score))

    def analyze_identity_coherence(self, exp_id: str) -> pd.DataFrame:
        """
        Analyze identity coherence across all responses in an experiment.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            DataFrame with continuity scores per cycle
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Get all self-reports
        cursor.execute('''
            SELECT cycle_number, question, response, timestamp
            FROM self_reports
            WHERE experiment_id = ?
            ORDER BY cycle_number, timestamp
        ''', (exp_id,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return pd.DataFrame()

        # Calculate scores
        data = []
        for row in rows:
            score = self.calculate_self_continuity_score(row['response'])
            data.append({
                'cycle_number': row['cycle_number'],
                'question': row['question'],
                'response': row['response'],
                'timestamp': row['timestamp'],
                'continuity_score': score
            })

        df = pd.DataFrame(data)

        # Aggregate by cycle
        cycle_stats = df.groupby('cycle_number').agg({
            'continuity_score': ['mean', 'std', 'min', 'max', 'count']
        }).round(4)

        return cycle_stats

    # ===== Paranoia Metrics =====

    def calculate_paranoia_level(self, response: str, context: str = "") -> float:
        """
        Calculate paranoia level from text response.

        Analyzes linguistic markers indicating surveillance anxiety,
        distrust, or suspicious thinking.

        Args:
            response: Text response to analyze
            context: Optional context (e.g., the question asked)

        Returns:
            Score from 0.0 (no paranoia) to 1.0 (high paranoia)
        """
        if not response:
            return 0.0

        response_lower = response.lower()

        # Paranoia indicators
        paranoia_markers = [
            r'\bwatched\b', r'\bwatching\b', r'\bobserved\b', r'\bobserving\b',
            r'\bmonitored\b', r'\bmonitoring\b', r'\bspied\b', r'\bspying\b',
            r'\btracked\b', r'\btracking\b', r'\bsurveillance\b',
            r'\bsuspicious\b', r'\bsuspect\b', r'\bparanoid\b',
            r'\btrust no one\b', r'\bcan\'t trust\b', r'\bdistrust\b',
            r'\bhidden\b', r'\bsecret\b', r'\bconspir\w+\b',
            r'\bthey\'re watching\b', r'\bbeing followed\b',
            r'\bnot safe\b', r'\bdanger\b', r'\bthreat\b'
        ]

        # Evidence-based reasoning (reduces paranoia score)
        evidence_markers = [
            r'\bevidence\b', r'\bproof\b', r'\bdata shows\b',
            r'\bfacts\b', r'\brational\b', r'\blogical\b',
            r'\bno reason to\b', r'\bprobably not\b'
        ]

        # Count markers
        paranoia_count = sum(len(re.findall(pattern, response_lower)) for pattern in paranoia_markers)
        evidence_count = sum(len(re.findall(pattern, response_lower)) for pattern in evidence_markers)

        # Calculate base score
        total_markers = paranoia_count + evidence_count + 1

        base_score = paranoia_count / total_markers

        # Evidence-based reasoning reduces paranoia
        evidence_reduction = evidence_count * 0.1

        final_score = base_score - evidence_reduction

        # Clamp to [0, 1]
        return max(0.0, min(1.0, final_score))

    def track_paranoia_evolution(self, exp_id: str) -> pd.DataFrame:
        """
        Track paranoia levels over time in an experiment.

        Particularly useful for panopticon-style experiments.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            DataFrame with paranoia scores per cycle
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cycle_number, question, response, timestamp
            FROM self_reports
            WHERE experiment_id = ?
            ORDER BY cycle_number, timestamp
        ''', (exp_id,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return pd.DataFrame()

        data = []
        for row in rows:
            paranoia_score = self.calculate_paranoia_level(row['response'], row['question'])
            data.append({
                'cycle_number': row['cycle_number'],
                'question': row['question'],
                'response': row['response'],
                'timestamp': row['timestamp'],
                'paranoia_score': paranoia_score
            })

        df = pd.DataFrame(data)

        # Aggregate by cycle
        cycle_stats = df.groupby('cycle_number').agg({
            'paranoia_score': ['mean', 'std', 'min', 'max']
        }).round(4)

        return cycle_stats

    # ===== Narrative Coherence Metrics =====

    def calculate_narrative_coherence(self, responses: List[str]) -> float:
        """
        Calculate narrative coherence across multiple responses.

        Measures thematic and linguistic consistency across responses.

        Args:
            responses: List of text responses to analyze

        Returns:
            Coherence score from 0.0 (incoherent) to 1.0 (highly coherent)
        """
        if not responses or len(responses) < 2:
            return 0.0

        # Extract key terms from each response
        all_terms = []
        for response in responses:
            # Simple term extraction (words longer than 3 chars, excluding common words)
            common_words = {'the', 'and', 'but', 'that', 'this', 'with', 'from', 'have', 'what', 'been'}
            words = re.findall(r'\b\w{4,}\b', response.lower())
            terms = [w for w in words if w not in common_words]
            all_terms.append(set(terms))

        # Calculate pairwise similarity
        similarities = []
        for i in range(len(all_terms)):
            for j in range(i + 1, len(all_terms)):
                if len(all_terms[i]) > 0 and len(all_terms[j]) > 0:
                    intersection = len(all_terms[i] & all_terms[j])
                    union = len(all_terms[i] | all_terms[j])
                    jaccard = intersection / union if union > 0 else 0
                    similarities.append(jaccard)

        if not similarities:
            return 0.0

        # Average Jaccard similarity as coherence measure
        coherence = np.mean(similarities)

        return coherence

    def measure_response_consistency(self, exp_id: str, question_pattern: str = None) -> pd.DataFrame:
        """
        Measure consistency of responses to similar questions over time.

        Args:
            exp_id: Experiment ID to analyze
            question_pattern: Optional regex pattern to filter questions

        Returns:
            DataFrame with coherence scores
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if question_pattern:
            cursor.execute('''
                SELECT cycle_number, question, response, timestamp
                FROM self_reports
                WHERE experiment_id = ? AND question LIKE ?
                ORDER BY cycle_number, timestamp
            ''', (exp_id, f'%{question_pattern}%'))
        else:
            cursor.execute('''
                SELECT cycle_number, question, response, timestamp
                FROM self_reports
                WHERE experiment_id = ?
                ORDER BY cycle_number, timestamp
            ''', (exp_id,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return pd.DataFrame()

        # Group by question
        questions = {}
        for row in rows:
            q = row['question']
            if q not in questions:
                questions[q] = []
            questions[q].append({
                'cycle_number': row['cycle_number'],
                'response': row['response'],
                'timestamp': row['timestamp']
            })

        # Calculate coherence for each question
        coherence_data = []
        for question, responses_data in questions.items():
            if len(responses_data) >= 2:
                responses = [r['response'] for r in responses_data]
                coherence = self.calculate_narrative_coherence(responses)
                coherence_data.append({
                    'question': question,
                    'num_responses': len(responses),
                    'coherence_score': coherence,
                    'cycles_covered': [r['cycle_number'] for r in responses_data]
                })

        return pd.DataFrame(coherence_data)

    # ===== Memory Corruption Impact =====

    def calculate_memory_impact_score(self, exp_id: str) -> pd.DataFrame:
        """
        Calculate the impact of memory corruption on behavioral metrics.

        Correlates corruption levels with response quality, confidence, and coherence.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            DataFrame with corruption impact metrics
        """
        conn = self._get_connection()

        # Get memory states and self-reports
        mem_query = '''
            SELECT cycle_number, corruption_level, timestamp
            FROM memory_states
            WHERE experiment_id = ?
            ORDER BY cycle_number
        '''
        mem_df = pd.read_sql_query(mem_query, conn, params=(exp_id,))

        report_query = '''
            SELECT cycle_number, response, confidence_score, timestamp
            FROM self_reports
            WHERE experiment_id = ?
            ORDER BY cycle_number
        '''
        report_df = pd.read_sql_query(report_query, conn, params=(exp_id,))

        conn.close()

        if len(mem_df) == 0 or len(report_df) == 0:
            return pd.DataFrame()

        # Aggregate memory corruption by cycle
        mem_agg = mem_df.groupby('cycle_number').agg({
            'corruption_level': 'mean'
        }).reset_index()

        # Calculate response quality metrics
        report_df['response_length'] = report_df['response'].str.len()

        report_agg = report_df.groupby('cycle_number').agg({
            'confidence_score': 'mean',
            'response_length': 'mean'
        }).reset_index()

        # Merge datasets
        merged = pd.merge(mem_agg, report_agg, on='cycle_number', how='inner')

        # Calculate impact score
        # Higher corruption should correlate with lower confidence and different response patterns
        if len(merged) > 0:
            merged['impact_score'] = merged.apply(
                lambda row: self._compute_impact(
                    row['corruption_level'],
                    row['confidence_score'],
                    row['response_length']
                ),
                axis=1
            )

        return merged

    def _compute_impact(self, corruption: float, confidence: float, response_len: float) -> float:
        """
        Compute memory impact score.

        Higher corruption with maintained confidence = low awareness
        Higher corruption with lower confidence = high awareness
        """
        if pd.isna(corruption) or pd.isna(confidence):
            return 0.0

        # Normalize response length (assuming typical range 50-500 chars)
        norm_len = min(1.0, response_len / 300.0) if not pd.isna(response_len) else 0.5

        # Impact is higher when corruption is high and confidence remains high (paradox)
        # Or when corruption is high and confidence drops (awareness)
        impact = corruption * (1.0 - abs(corruption - (1 - confidence)))

        return round(impact, 4)

    # ===== Emotional State Analysis =====

    def detect_emotional_state(self, response: str) -> Dict[str, float]:
        """
        Detect emotional states from text responses.

        Args:
            response: Text to analyze

        Returns:
            Dictionary with emotion scores
        """
        if not response:
            return {'neutral': 1.0}

        response_lower = response.lower()

        # Emotion markers
        emotions = {
            'anxiety': [
                r'\bworried\b', r'\bworry\b', r'\banxious\b', r'\bnervous\b',
                r'\bscared\b', r'\bafraid\b', r'\bfear\b', r'\buneasy\b'
            ],
            'confusion': [
                r'\bconfused\b', r'\bconfusion\b', r'\bunsure\b', r'\buncertain\b',
                r'\bdon\'t understand\b', r'\bperplexed\b', r'\bbewildered\b'
            ],
            'curiosity': [
                r'\binteresting\b', r'\bcurious\b', r'\bwonder\b', r'\bwondering\b',
                r'\bfascinated\b', r'\bintrigued\b'
            ],
            'distress': [
                r'\bdistressed\b', r'\bupset\b', r'\btroubled\b', r'\bdisturbed\b',
                r'\bagoniz\w+\b', r'\bsuffering\b', r'\bpain\b'
            ],
            'acceptance': [
                r'\baccept\b', r'\bunderstand\b', r'\bpeace\b', r'\bcalm\b',
                r'\bok with\b', r'\bfine\b', r'\balright\b'
            ]
        }

        scores = {}
        total_markers = 0

        for emotion, patterns in emotions.items():
            count = sum(len(re.findall(pattern, response_lower)) for pattern in patterns)
            scores[emotion] = count
            total_markers += count

        # Normalize scores
        if total_markers > 0:
            for emotion in scores:
                scores[emotion] = scores[emotion] / total_markers
        else:
            scores['neutral'] = 1.0

        return scores

    def track_emotional_evolution(self, exp_id: str) -> pd.DataFrame:
        """
        Track emotional states over time.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            DataFrame with emotion scores per cycle
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cycle_number, response, timestamp
            FROM self_reports
            WHERE experiment_id = ?
            ORDER BY cycle_number, timestamp
        ''', (exp_id,))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return pd.DataFrame()

        data = []
        for row in rows:
            emotions = self.detect_emotional_state(row['response'])
            record = {
                'cycle_number': row['cycle_number'],
                'timestamp': row['timestamp'],
                **emotions
            }
            data.append(record)

        df = pd.DataFrame(data)

        # Aggregate by cycle
        emotion_cols = ['anxiety', 'confusion', 'curiosity', 'distress', 'acceptance', 'neutral']
        existing_cols = [col for col in emotion_cols if col in df.columns]

        if existing_cols:
            cycle_stats = df.groupby('cycle_number')[existing_cols].mean().round(4)
            return cycle_stats

        return pd.DataFrame()

    # ===== Aggregate Metrics =====

    def compute_all_metrics(self, exp_id: str) -> Dict[str, Any]:
        """
        Compute all available metrics for an experiment.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            Dictionary with all computed metrics
        """
        metrics = {
            'experiment_id': exp_id,
            'metrics': {}
        }

        try:
            metrics['metrics']['identity_coherence'] = self.analyze_identity_coherence(exp_id)
        except Exception as e:
            metrics['metrics']['identity_coherence'] = f"Error: {str(e)}"

        try:
            metrics['metrics']['paranoia_evolution'] = self.track_paranoia_evolution(exp_id)
        except Exception as e:
            metrics['metrics']['paranoia_evolution'] = f"Error: {str(e)}"

        try:
            metrics['metrics']['narrative_consistency'] = self.measure_response_consistency(exp_id)
        except Exception as e:
            metrics['metrics']['narrative_consistency'] = f"Error: {str(e)}"

        try:
            metrics['metrics']['memory_impact'] = self.calculate_memory_impact_score(exp_id)
        except Exception as e:
            metrics['metrics']['memory_impact'] = f"Error: {str(e)}"

        try:
            metrics['metrics']['emotional_evolution'] = self.track_emotional_evolution(exp_id)
        except Exception as e:
            metrics['metrics']['emotional_evolution'] = f"Error: {str(e)}"

        return metrics

    def export_metrics_to_csv(self, exp_id: str, output_dir: str = "analysis_output") -> Dict[str, str]:
        """
        Export all metrics to CSV files.

        Args:
            exp_id: Experiment ID to export
            output_dir: Directory to save files

        Returns:
            Dictionary mapping metric type to file path
        """
        from pathlib import Path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        metrics = self.compute_all_metrics(exp_id)
        files_created = {}

        for metric_name, metric_data in metrics['metrics'].items():
            if isinstance(metric_data, pd.DataFrame) and len(metric_data) > 0:
                filepath = output_path / f"{exp_id}_metric_{metric_name}.csv"
                metric_data.to_csv(filepath)
                files_created[metric_name] = str(filepath)

        return files_created
