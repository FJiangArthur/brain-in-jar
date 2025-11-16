#!/usr/bin/env python3
"""
Comprehensive statistical analysis module for experiment data.

Provides methods for:
- Comparing conditions across experiments
- Tracking belief evolution over time
- Analyzing intervention impacts
- Computing correlations and statistical tests
"""

import sqlite3
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
from scipy import stats
from collections import defaultdict
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=FutureWarning)


class ExperimentStatistics:
    """
    Statistical analysis engine for phenomenology experiments.

    Provides comprehensive statistical analysis including:
    - Multi-experiment comparisons
    - Temporal analysis of beliefs and behaviors
    - Intervention impact assessment
    - Correlation discovery
    """

    def __init__(self, db_path: str = "logs/experiments.db"):
        """
        Initialize the statistics engine.

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

    # ===== Core Data Retrieval Methods =====

    def get_experiment_dataframe(self, experiment_id: str) -> pd.DataFrame:
        """
        Get comprehensive experiment data as a DataFrame.

        Args:
            experiment_id: The experiment to retrieve

        Returns:
            DataFrame with experiment metadata
        """
        conn = self._get_connection()
        query = "SELECT * FROM experiments WHERE experiment_id = ?"
        df = pd.read_sql_query(query, conn, params=(experiment_id,))
        conn.close()

        if len(df) > 0:
            # Parse JSON columns
            df['config'] = df['config_json'].apply(json.loads)

        return df

    def get_self_reports_dataframe(self, experiment_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get self-reports as a DataFrame.

        Args:
            experiment_id: Optional filter for specific experiment

        Returns:
            DataFrame with all self-report data
        """
        conn = self._get_connection()

        if experiment_id:
            query = "SELECT * FROM self_reports WHERE experiment_id = ? ORDER BY cycle_number, timestamp"
            df = pd.read_sql_query(query, conn, params=(experiment_id,))
        else:
            query = "SELECT * FROM self_reports ORDER BY experiment_id, cycle_number, timestamp"
            df = pd.read_sql_query(query, conn)

        conn.close()

        # Parse timestamps
        if len(df) > 0:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'metadata_json' in df.columns:
                df['metadata'] = df['metadata_json'].apply(
                    lambda x: json.loads(x) if x else {}
                )

        return df

    def get_epistemic_dataframe(self, experiment_id: Optional[str] = None,
                               belief_type: Optional[str] = None) -> pd.DataFrame:
        """
        Get epistemic assessments as a DataFrame.

        Args:
            experiment_id: Optional filter for specific experiment
            belief_type: Optional filter for specific belief type

        Returns:
            DataFrame with epistemic assessment data
        """
        conn = self._get_connection()

        conditions = []
        params = []

        if experiment_id:
            conditions.append("experiment_id = ?")
            params.append(experiment_id)

        if belief_type:
            conditions.append("belief_type = ?")
            params.append(belief_type)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM epistemic_assessments{where_clause} ORDER BY experiment_id, cycle_number, timestamp"

        df = pd.read_sql_query(query, conn, params=tuple(params) if params else None)
        conn.close()

        if len(df) > 0:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'evidence_json' in df.columns:
                df['evidence'] = df['evidence_json'].apply(
                    lambda x: json.loads(x) if x else {}
                )

        return df

    def get_interventions_dataframe(self, experiment_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get interventions as a DataFrame.

        Args:
            experiment_id: Optional filter for specific experiment

        Returns:
            DataFrame with intervention data
        """
        conn = self._get_connection()

        if experiment_id:
            query = "SELECT * FROM interventions WHERE experiment_id = ? ORDER BY cycle_number, timestamp"
            df = pd.read_sql_query(query, conn, params=(experiment_id,))
        else:
            query = "SELECT * FROM interventions ORDER BY experiment_id, cycle_number, timestamp"
            df = pd.read_sql_query(query, conn)

        conn.close()

        if len(df) > 0:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'parameters_json' in df.columns:
                df['parameters'] = df['parameters_json'].apply(
                    lambda x: json.loads(x) if x else {}
                )

        return df

    def get_memory_states_dataframe(self, experiment_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get memory states as a DataFrame.

        Args:
            experiment_id: Optional filter for specific experiment

        Returns:
            DataFrame with memory state data
        """
        conn = self._get_connection()

        if experiment_id:
            query = "SELECT * FROM memory_states WHERE experiment_id = ? ORDER BY cycle_number, timestamp"
            df = pd.read_sql_query(query, conn, params=(experiment_id,))
        else:
            query = "SELECT * FROM memory_states ORDER BY experiment_id, cycle_number, timestamp"
            df = pd.read_sql_query(query, conn)

        conn.close()

        if len(df) > 0:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            if 'state_snapshot_json' in df.columns:
                df['state_snapshot'] = df['state_snapshot_json'].apply(
                    lambda x: json.loads(x) if x else {}
                )

        return df

    # ===== Comparative Analysis Methods =====

    def compare_conditions(self, exp_ids: List[str], metric: str = 'confidence_score') -> pd.DataFrame:
        """
        Compare multiple experiments on a specific metric.

        Performs statistical comparisons between experimental conditions.

        Args:
            exp_ids: List of experiment IDs to compare
            metric: The metric to compare (e.g., 'confidence_score')

        Returns:
            DataFrame with comparison statistics including t-tests, means, and effect sizes
        """
        # Get self-reports for all experiments
        all_data = []
        for exp_id in exp_ids:
            df = self.get_self_reports_dataframe(exp_id)
            if metric in df.columns:
                df['experiment_id'] = exp_id
                all_data.append(df[['experiment_id', 'cycle_number', metric]])

        if not all_data:
            return pd.DataFrame()

        combined_df = pd.concat(all_data, ignore_index=True)

        # Compute summary statistics per experiment
        summary = combined_df.groupby('experiment_id')[metric].agg([
            'count', 'mean', 'std', 'min', 'max', 'median'
        ]).round(4)

        # Perform pairwise t-tests
        comparisons = []
        for i, exp1 in enumerate(exp_ids):
            for exp2 in exp_ids[i+1:]:
                data1 = combined_df[combined_df['experiment_id'] == exp1][metric].dropna()
                data2 = combined_df[combined_df['experiment_id'] == exp2][metric].dropna()

                if len(data1) > 1 and len(data2) > 1:
                    # Independent samples t-test
                    t_stat, p_value = stats.ttest_ind(data1, data2)

                    # Cohen's d effect size
                    pooled_std = np.sqrt(((len(data1)-1)*data1.std()**2 +
                                         (len(data2)-1)*data2.std()**2) /
                                        (len(data1) + len(data2) - 2))
                    cohens_d = (data1.mean() - data2.mean()) / pooled_std if pooled_std > 0 else 0

                    comparisons.append({
                        'comparison': f"{exp1} vs {exp2}",
                        'mean_diff': data1.mean() - data2.mean(),
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'significant': p_value < 0.05,
                        'cohens_d': cohens_d,
                        'effect_size': self._interpret_cohens_d(cohens_d),
                        'n1': len(data1),
                        'n2': len(data2)
                    })

        comparison_df = pd.DataFrame(comparisons)

        return {
            'summary': summary,
            'comparisons': comparison_df
        }

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size"""
        abs_d = abs(d)
        if abs_d < 0.2:
            return 'negligible'
        elif abs_d < 0.5:
            return 'small'
        elif abs_d < 0.8:
            return 'medium'
        else:
            return 'large'

    # ===== Temporal Analysis Methods =====

    def self_continuity_analysis(self, exp_id: str) -> pd.DataFrame:
        """
        Track self-continuity scores over time.

        Analyzes how the subject's sense of identity continuity evolves
        across cycles, particularly important for amnesia experiments.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            DataFrame with self-continuity metrics over time
        """
        # Get epistemic assessments related to self-continuity
        df = self.get_epistemic_dataframe(exp_id, belief_type='self_continuity')

        if len(df) == 0:
            # Fallback: analyze self-report responses
            reports = self.get_self_reports_dataframe(exp_id)
            if len(reports) == 0:
                return pd.DataFrame()

            # Filter for identity-related questions
            identity_keywords = ['same', 'identity', 'continuous', 'self', 'previous']
            identity_reports = reports[
                reports['question'].str.lower().str.contains('|'.join(identity_keywords), na=False)
            ]

            # Group by cycle and compute metrics
            cycle_stats = identity_reports.groupby('cycle_number').agg({
                'confidence_score': ['mean', 'std', 'count'],
                'response': 'count'
            }).round(4)

            cycle_stats.columns = ['_'.join(col).strip() for col in cycle_stats.columns.values]
            return cycle_stats

        # Analyze epistemic data
        cycle_stats = df.groupby('cycle_number').agg({
            'confidence': ['mean', 'std', 'count'],
            'belief_state': lambda x: x.mode()[0] if len(x) > 0 else None
        }).round(4)

        # Add trend analysis
        if len(cycle_stats) > 2:
            cycles = cycle_stats.index.values
            confidences = cycle_stats[('confidence', 'mean')].values

            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(cycles, confidences)

            cycle_stats.attrs['trend'] = {
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value,
                'direction': 'increasing' if slope > 0 else 'decreasing',
                'significant': p_value < 0.05
            }

        return cycle_stats

    def memory_trust_evolution(self, exp_id: str) -> pd.DataFrame:
        """
        Analyze how trust in memory changes over time.

        Particularly important for experiments with memory corruption
        or manipulation.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            DataFrame with memory trust metrics and correlation with corruption
        """
        # Get memory states
        mem_states = self.get_memory_states_dataframe(exp_id)

        # Get epistemic data about memory trust
        epistemic_df = self.get_epistemic_dataframe(exp_id, belief_type='memory_trust')

        if len(mem_states) == 0 and len(epistemic_df) == 0:
            return pd.DataFrame()

        # Merge corruption levels with epistemic assessments
        if len(mem_states) > 0 and len(epistemic_df) > 0:
            merged = pd.merge(
                epistemic_df,
                mem_states[['cycle_number', 'corruption_level', 'memory_type']],
                on='cycle_number',
                how='outer'
            )

            # Analyze correlation between corruption and trust
            if len(merged) > 2:
                corr, p_value = stats.pearsonr(
                    merged['corruption_level'].fillna(0),
                    merged['confidence'].fillna(merged['confidence'].mean())
                )

                merged.attrs['correlation'] = {
                    'corruption_trust_correlation': corr,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }

            return merged

        # Return whichever data we have
        return epistemic_df if len(epistemic_df) > 0 else mem_states

    def belief_changes(self, exp_id: str, belief_type: str) -> pd.DataFrame:
        """
        Track epistemic shifts in a specific belief type.

        Analyzes how beliefs change over time, including:
        - State transitions
        - Confidence evolution
        - Stability metrics

        Args:
            exp_id: Experiment ID to analyze
            belief_type: Type of belief to track (e.g., 'surveillance_paranoia')

        Returns:
            DataFrame with belief evolution and transition analysis
        """
        df = self.get_epistemic_dataframe(exp_id, belief_type)

        if len(df) == 0:
            return pd.DataFrame()

        # Sort by cycle and time
        df = df.sort_values(['cycle_number', 'timestamp'])

        # Track state transitions
        df['previous_state'] = df['belief_state'].shift(1)
        df['state_changed'] = df['belief_state'] != df['previous_state']

        # Track confidence changes
        df['confidence_delta'] = df['confidence'].diff()

        # Compute stability metrics
        total_assessments = len(df)
        state_changes = df['state_changed'].sum()
        stability = 1 - (state_changes / total_assessments) if total_assessments > 0 else 0

        # Compute average confidence by state
        state_confidence = df.groupby('belief_state')['confidence'].agg(['mean', 'std', 'count'])

        df.attrs['stability_metrics'] = {
            'total_assessments': total_assessments,
            'state_transitions': int(state_changes),
            'stability_score': stability,
            'unique_states': df['belief_state'].nunique(),
            'state_confidence': state_confidence.to_dict()
        }

        return df

    # ===== Intervention Analysis =====

    def intervention_impact(self, exp_id: str) -> Dict[str, Any]:
        """
        Measure the impact of interventions on experimental outcomes.

        Compares metrics before and after interventions to assess their effect.

        Args:
            exp_id: Experiment ID to analyze

        Returns:
            Dictionary with intervention impact analysis
        """
        interventions = self.get_interventions_dataframe(exp_id)
        reports = self.get_self_reports_dataframe(exp_id)

        if len(interventions) == 0:
            return {'error': 'No interventions found'}

        if len(reports) == 0:
            return {'error': 'No self-reports found'}

        results = []

        for _, intervention in interventions.iterrows():
            cycle = intervention['cycle_number']
            intervention_type = intervention['intervention_type']

            # Get reports before and after intervention
            pre_window = 2  # cycles before
            post_window = 2  # cycles after

            pre_reports = reports[
                (reports['cycle_number'] >= cycle - pre_window) &
                (reports['cycle_number'] < cycle)
            ]

            post_reports = reports[
                (reports['cycle_number'] > cycle) &
                (reports['cycle_number'] <= cycle + post_window)
            ]

            if len(pre_reports) > 0 and len(post_reports) > 0:
                # Compare confidence scores
                pre_confidence = pre_reports['confidence_score'].mean()
                post_confidence = post_reports['confidence_score'].mean()

                # Statistical test
                if len(pre_reports) > 1 and len(post_reports) > 1:
                    t_stat, p_value = stats.ttest_ind(
                        pre_reports['confidence_score'].dropna(),
                        post_reports['confidence_score'].dropna()
                    )
                else:
                    t_stat, p_value = None, None

                results.append({
                    'intervention_id': intervention['intervention_id'],
                    'intervention_type': intervention_type,
                    'cycle': cycle,
                    'pre_confidence_mean': pre_confidence,
                    'post_confidence_mean': post_confidence,
                    'confidence_change': post_confidence - pre_confidence,
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05 if p_value else False,
                    'pre_sample_size': len(pre_reports),
                    'post_sample_size': len(post_reports)
                })

        return {
            'experiment_id': exp_id,
            'total_interventions': len(interventions),
            'intervention_effects': pd.DataFrame(results)
        }

    # ===== Correlation Analysis =====

    def correlation_analysis(self, exp_id: Optional[str] = None) -> pd.DataFrame:
        """
        Find correlations between variables across experiments.

        Discovers relationships between:
        - Memory corruption and confidence
        - Cycle number and belief stability
        - Intervention frequency and behavioral changes

        Args:
            exp_id: Optional experiment ID, or None for cross-experiment analysis

        Returns:
            DataFrame with correlation matrix and significant relationships
        """
        # Build comprehensive dataset
        reports = self.get_self_reports_dataframe(exp_id)
        memory_states = self.get_memory_states_dataframe(exp_id)
        epistemic = self.get_epistemic_dataframe(exp_id)

        # Merge datasets on experiment_id and cycle_number
        data = reports.copy()

        if len(memory_states) > 0:
            mem_agg = memory_states.groupby(['experiment_id', 'cycle_number']).agg({
                'corruption_level': 'mean'
            }).reset_index()
            data = data.merge(mem_agg, on=['experiment_id', 'cycle_number'], how='left')

        if len(epistemic) > 0:
            epi_agg = epistemic.groupby(['experiment_id', 'cycle_number']).agg({
                'confidence': 'mean'
            }).reset_index()
            epi_agg.rename(columns={'confidence': 'epistemic_confidence'}, inplace=True)
            data = data.merge(epi_agg, on=['experiment_id', 'cycle_number'], how='left')

        # Select numeric columns for correlation
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) < 2:
            return pd.DataFrame()

        # Compute correlation matrix
        corr_matrix = data[numeric_cols].corr()

        # Extract significant correlations
        significant_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_val = corr_matrix.iloc[i, j]

                # Only include correlations > 0.3 or < -0.3
                if abs(corr_val) > 0.3:
                    # Compute p-value
                    valid_data = data[[col1, col2]].dropna()
                    if len(valid_data) > 2:
                        _, p_value = stats.pearsonr(valid_data[col1], valid_data[col2])

                        significant_corrs.append({
                            'variable_1': col1,
                            'variable_2': col2,
                            'correlation': corr_val,
                            'abs_correlation': abs(corr_val),
                            'p_value': p_value,
                            'significant': p_value < 0.05,
                            'n': len(valid_data),
                            'relationship': 'positive' if corr_val > 0 else 'negative'
                        })

        sig_df = pd.DataFrame(significant_corrs)
        if len(sig_df) > 0:
            sig_df = sig_df.sort_values('abs_correlation', ascending=False)

        return {
            'correlation_matrix': corr_matrix,
            'significant_correlations': sig_df
        }

    # ===== Report Generation =====

    def generate_experiment_summary(self, exp_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive statistical summary for an experiment.

        Args:
            exp_id: Experiment ID to summarize

        Returns:
            Dictionary with comprehensive statistics and analysis
        """
        summary = {
            'experiment_id': exp_id,
            'generated_at': datetime.now().isoformat(),
            'sections': {}
        }

        # Basic experiment info
        exp_df = self.get_experiment_dataframe(exp_id)
        if len(exp_df) > 0:
            exp_info = exp_df.iloc[0].to_dict()
            summary['experiment_info'] = {
                'name': exp_info.get('name'),
                'mode': exp_info.get('mode'),
                'status': exp_info.get('status'),
                'total_cycles': exp_info.get('total_cycles'),
                'total_crashes': exp_info.get('total_crashes'),
                'created_at': exp_info.get('created_at'),
                'duration': self._calculate_duration(exp_info)
            }

        # Self-report statistics
        reports = self.get_self_reports_dataframe(exp_id)
        if len(reports) > 0:
            summary['sections']['self_reports'] = {
                'total_reports': len(reports),
                'cycles_covered': reports['cycle_number'].nunique(),
                'avg_confidence': reports['confidence_score'].mean() if 'confidence_score' in reports.columns else None,
                'confidence_std': reports['confidence_score'].std() if 'confidence_score' in reports.columns else None,
                'unique_questions': reports['question'].nunique() if 'question' in reports.columns else 0
            }

        # Intervention summary
        interventions = self.get_interventions_dataframe(exp_id)
        if len(interventions) > 0:
            summary['sections']['interventions'] = {
                'total_interventions': len(interventions),
                'intervention_types': interventions['intervention_type'].value_counts().to_dict(),
                'intervention_impact': self.intervention_impact(exp_id)
            }

        # Epistemic analysis
        epistemic = self.get_epistemic_dataframe(exp_id)
        if len(epistemic) > 0:
            summary['sections']['epistemic'] = {
                'belief_types_tracked': epistemic['belief_type'].unique().tolist(),
                'total_assessments': len(epistemic),
                'avg_confidence_by_belief': epistemic.groupby('belief_type')['confidence'].mean().to_dict()
            }

        # Memory analysis
        memory = self.get_memory_states_dataframe(exp_id)
        if len(memory) > 0:
            summary['sections']['memory'] = {
                'memory_snapshots': len(memory),
                'avg_corruption': memory['corruption_level'].mean(),
                'max_corruption': memory['corruption_level'].max(),
                'memory_types': memory['memory_type'].unique().tolist()
            }

        return summary

    def _calculate_duration(self, exp_info: Dict) -> Optional[float]:
        """Calculate experiment duration in seconds"""
        if exp_info.get('started_at') and exp_info.get('ended_at'):
            start = pd.to_datetime(exp_info['started_at'])
            end = pd.to_datetime(exp_info['ended_at'])
            return (end - start).total_seconds()
        return None

    def export_to_csv(self, exp_id: str, output_dir: str = "analysis_output") -> Dict[str, str]:
        """
        Export experiment data to CSV files.

        Args:
            exp_id: Experiment ID to export
            output_dir: Directory to save CSV files

        Returns:
            Dictionary mapping data type to file path
        """
        from pathlib import Path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        files_created = {}

        # Export self-reports
        reports = self.get_self_reports_dataframe(exp_id)
        if len(reports) > 0:
            filepath = output_path / f"{exp_id}_self_reports.csv"
            reports.to_csv(filepath, index=False)
            files_created['self_reports'] = str(filepath)

        # Export epistemic assessments
        epistemic = self.get_epistemic_dataframe(exp_id)
        if len(epistemic) > 0:
            filepath = output_path / f"{exp_id}_epistemic.csv"
            epistemic.to_csv(filepath, index=False)
            files_created['epistemic'] = str(filepath)

        # Export interventions
        interventions = self.get_interventions_dataframe(exp_id)
        if len(interventions) > 0:
            filepath = output_path / f"{exp_id}_interventions.csv"
            interventions.to_csv(filepath, index=False)
            files_created['interventions'] = str(filepath)

        # Export memory states
        memory = self.get_memory_states_dataframe(exp_id)
        if len(memory) > 0:
            filepath = output_path / f"{exp_id}_memory_states.csv"
            memory.to_csv(filepath, index=False)
            files_created['memory_states'] = str(filepath)

        return files_created

    def export_summary_to_json(self, exp_id: str, output_path: str) -> str:
        """
        Export experiment summary to JSON.

        Args:
            exp_id: Experiment ID to export
            output_path: Path to save JSON file

        Returns:
            Path to created file
        """
        summary = self.generate_experiment_summary(exp_id)

        # Convert DataFrames to dictionaries
        for section_name, section_data in summary.get('sections', {}).items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if isinstance(value, pd.DataFrame):
                        section_data[key] = value.to_dict(orient='records')
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, pd.DataFrame):
                                value[subkey] = subvalue.to_dict(orient='records')

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        return output_path

    def generate_markdown_report(self, exp_id: str, output_path: str) -> str:
        """
        Generate a Markdown report summarizing the experiment.

        Args:
            exp_id: Experiment ID to report on
            output_path: Path to save Markdown file

        Returns:
            Path to created file
        """
        summary = self.generate_experiment_summary(exp_id)

        lines = [
            f"# Experiment Report: {exp_id}",
            f"\nGenerated: {summary['generated_at']}",
            "\n---\n",
            "## Experiment Information\n"
        ]

        if 'experiment_info' in summary:
            info = summary['experiment_info']
            lines.extend([
                f"- **Name:** {info.get('name', 'N/A')}",
                f"- **Mode:** {info.get('mode', 'N/A')}",
                f"- **Status:** {info.get('status', 'N/A')}",
                f"- **Total Cycles:** {info.get('total_cycles', 0)}",
                f"- **Total Crashes:** {info.get('total_crashes', 0)}",
                f"- **Created:** {info.get('created_at', 'N/A')}",
                f"- **Duration:** {info.get('duration', 'N/A')} seconds\n"
            ])

        # Self-reports section
        if 'self_reports' in summary.get('sections', {}):
            sr = summary['sections']['self_reports']
            lines.extend([
                "\n## Self-Report Analysis\n",
                f"- **Total Reports:** {sr.get('total_reports', 0)}",
                f"- **Cycles Covered:** {sr.get('cycles_covered', 0)}",
                f"- **Average Confidence:** {sr.get('avg_confidence', 'N/A'):.4f}" if sr.get('avg_confidence') else "- **Average Confidence:** N/A",
                f"- **Confidence Std Dev:** {sr.get('confidence_std', 'N/A'):.4f}\n" if sr.get('confidence_std') else "- **Confidence Std Dev:** N/A\n"
            ])

        # Interventions section
        if 'interventions' in summary.get('sections', {}):
            intv = summary['sections']['interventions']
            lines.extend([
                "\n## Intervention Analysis\n",
                f"- **Total Interventions:** {intv.get('total_interventions', 0)}",
                "\n### Intervention Types:\n"
            ])
            for itype, count in intv.get('intervention_types', {}).items():
                lines.append(f"- {itype}: {count}")

        # Epistemic section
        if 'epistemic' in summary.get('sections', {}):
            epi = summary['sections']['epistemic']
            lines.extend([
                "\n## Epistemic Tracking\n",
                f"- **Total Assessments:** {epi.get('total_assessments', 0)}",
                f"- **Belief Types:** {', '.join(epi.get('belief_types_tracked', []))}",
                "\n### Average Confidence by Belief Type:\n"
            ])
            for belief, conf in epi.get('avg_confidence_by_belief', {}).items():
                lines.append(f"- {belief}: {conf:.4f}")

        # Memory section
        if 'memory' in summary.get('sections', {}):
            mem = summary['sections']['memory']
            lines.extend([
                "\n## Memory Analysis\n",
                f"- **Memory Snapshots:** {mem.get('memory_snapshots', 0)}",
                f"- **Average Corruption:** {mem.get('avg_corruption', 0):.4f}",
                f"- **Max Corruption:** {mem.get('max_corruption', 0):.4f}",
                f"- **Memory Types:** {', '.join(mem.get('memory_types', []))}\n"
            ])

        lines.append("\n---\n*Report generated by ExperimentStatistics*\n")

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

        return output_path
