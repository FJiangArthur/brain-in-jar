#!/usr/bin/env python3
"""
Reusable dashboard components for experiment comparison.

Provides Streamlit widgets for building interactive dashboards:
- ExperimentSelector: Multi-select experiment picker with filtering
- MetricsTable: Side-by-side metrics comparison table
- ComparisonPlot: Interactive plotly charts for comparison
- StatisticalTestPanel: Statistical test results display
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sqlite3


class ExperimentSelector:
    """Widget for selecting and filtering experiments."""

    def __init__(self, db_path: str):
        """
        Initialize experiment selector.

        Args:
            db_path: Path to experiments database
        """
        self.db_path = db_path

    def get_all_experiments(self) -> pd.DataFrame:
        """Get all experiments from database."""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT experiment_id, name, mode, status, created_at,
                   total_cycles, total_crashes,
                   config_json
            FROM experiments
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        if len(df) > 0:
            df['created_at'] = pd.to_datetime(df['created_at'])

        return df

    def render(self, key: str = "exp_selector") -> List[str]:
        """
        Render the experiment selector widget.

        Args:
            key: Unique key for widget state

        Returns:
            List of selected experiment IDs
        """
        st.subheader("Select Experiments to Compare")

        experiments_df = self.get_all_experiments()

        if len(experiments_df) == 0:
            st.warning("No experiments found in database.")
            return []

        # Filtering options
        col1, col2, col3 = st.columns(3)

        with col1:
            modes = ['All'] + sorted(experiments_df['mode'].unique().tolist())
            selected_mode = st.selectbox("Filter by Mode", modes, key=f"{key}_mode")

        with col2:
            statuses = ['All'] + sorted(experiments_df['status'].unique().tolist())
            selected_status = st.selectbox("Filter by Status", statuses, key=f"{key}_status")

        with col3:
            date_range = st.selectbox("Filter by Date",
                                     ['All Time', 'Last 24h', 'Last Week', 'Last Month'],
                                     key=f"{key}_date")

        # Apply filters
        filtered_df = experiments_df.copy()

        if selected_mode != 'All':
            filtered_df = filtered_df[filtered_df['mode'] == selected_mode]

        if selected_status != 'All':
            filtered_df = filtered_df[filtered_df['status'] == selected_status]

        if date_range != 'All Time':
            now = pd.Timestamp.now()
            if date_range == 'Last 24h':
                cutoff = now - pd.Timedelta(hours=24)
            elif date_range == 'Last Week':
                cutoff = now - pd.Timedelta(days=7)
            else:  # Last Month
                cutoff = now - pd.Timedelta(days=30)
            filtered_df = filtered_df[filtered_df['created_at'] >= cutoff]

        # Display experiment selection
        if len(filtered_df) == 0:
            st.warning("No experiments match the selected filters.")
            return []

        # Create display labels
        filtered_df['display_label'] = filtered_df.apply(
            lambda row: f"{row['experiment_id']} - {row['name']} ({row['mode']}) - {row['total_cycles']} cycles",
            axis=1
        )

        # Multi-select
        selected_labels = st.multiselect(
            "Choose experiments (select 2+ for comparison)",
            filtered_df['display_label'].tolist(),
            key=f"{key}_multiselect",
            help="Select multiple experiments to compare their metrics and results"
        )

        # Extract experiment IDs from selected labels
        selected_ids = []
        for label in selected_labels:
            exp_id = label.split(' - ')[0]
            selected_ids.append(exp_id)

        # Show selected count
        if len(selected_ids) > 0:
            st.info(f"Selected {len(selected_ids)} experiment(s) for comparison")

        return selected_ids


class MetricsTable:
    """Widget for displaying side-by-side metrics comparison."""

    def __init__(self, db_path: str):
        """Initialize metrics table."""
        self.db_path = db_path

    def get_experiment_metrics(self, exp_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics for an experiment."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get basic experiment info
        cursor.execute("""
            SELECT * FROM experiments WHERE experiment_id = ?
        """, (exp_id,))
        exp_row = cursor.fetchone()

        if not exp_row:
            conn.close()
            return {}

        columns = [desc[0] for desc in cursor.description]
        exp_data = dict(zip(columns, exp_row))

        # Get counts
        cursor.execute("SELECT COUNT(*) FROM self_reports WHERE experiment_id = ?", (exp_id,))
        total_reports = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM interventions WHERE experiment_id = ?", (exp_id,))
        total_interventions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM epistemic_assessments WHERE experiment_id = ?", (exp_id,))
        total_assessments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM messages WHERE experiment_id = ?", (exp_id,))
        total_messages = cursor.fetchone()[0]

        # Get average confidence
        cursor.execute("""
            SELECT AVG(confidence_score) FROM self_reports
            WHERE experiment_id = ? AND confidence_score IS NOT NULL
        """, (exp_id,))
        avg_confidence = cursor.fetchone()[0]

        # Get memory corruption stats
        cursor.execute("""
            SELECT AVG(corruption_level), MAX(corruption_level)
            FROM memory_states WHERE experiment_id = ?
        """, (exp_id,))
        mem_stats = cursor.fetchone()
        avg_corruption = mem_stats[0] if mem_stats[0] else 0
        max_corruption = mem_stats[1] if mem_stats[1] else 0

        conn.close()

        # Calculate crash rate
        crash_rate = (exp_data['total_crashes'] / exp_data['total_cycles']
                     if exp_data['total_cycles'] > 0 else 0)

        # Calculate duration
        duration = None
        if exp_data['started_at'] and exp_data['ended_at']:
            start = pd.to_datetime(exp_data['started_at'])
            end = pd.to_datetime(exp_data['ended_at'])
            duration = (end - start).total_seconds() / 3600  # hours

        return {
            'Experiment ID': exp_id,
            'Name': exp_data['name'],
            'Mode': exp_data['mode'],
            'Status': exp_data['status'],
            'Total Cycles': exp_data['total_cycles'],
            'Total Crashes': exp_data['total_crashes'],
            'Crash Rate': f"{crash_rate:.2%}",
            'Self Reports': total_reports,
            'Interventions': total_interventions,
            'Epistemic Assessments': total_assessments,
            'Messages': total_messages,
            'Avg Confidence': f"{avg_confidence:.3f}" if avg_confidence else "N/A",
            'Avg Memory Corruption': f"{avg_corruption:.3f}",
            'Max Memory Corruption': f"{max_corruption:.3f}",
            'Duration (hours)': f"{duration:.2f}" if duration else "N/A",
            'Created At': exp_data['created_at']
        }

    def render(self, experiment_ids: List[str]) -> pd.DataFrame:
        """
        Render metrics comparison table.

        Args:
            experiment_ids: List of experiment IDs to compare

        Returns:
            DataFrame with metrics
        """
        if not experiment_ids:
            st.info("Select experiments to view metrics comparison")
            return pd.DataFrame()

        st.subheader("Metrics Comparison Table")

        # Collect metrics for all experiments
        metrics_list = []
        for exp_id in experiment_ids:
            metrics = self.get_experiment_metrics(exp_id)
            if metrics:
                metrics_list.append(metrics)

        if not metrics_list:
            st.warning("No metrics found for selected experiments")
            return pd.DataFrame()

        # Create DataFrame
        df = pd.DataFrame(metrics_list)

        # Transpose for side-by-side comparison
        df_transposed = df.set_index('Experiment ID').T

        # Display as styled table
        st.dataframe(
            df_transposed,
            use_container_width=True,
            height=600
        )

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Metrics as CSV",
            data=csv,
            file_name=f"experiment_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        return df


class ComparisonPlot:
    """Widget for creating interactive comparison plots."""

    def __init__(self, db_path: str):
        """Initialize comparison plot widget."""
        self.db_path = db_path

    def get_cycle_data(self, exp_id: str) -> pd.DataFrame:
        """Get cycle-level data for an experiment."""
        conn = sqlite3.connect(self.db_path)

        # Get self-reports with cycle numbers
        query = """
            SELECT cycle_number,
                   AVG(confidence_score) as avg_confidence,
                   COUNT(*) as report_count
            FROM self_reports
            WHERE experiment_id = ?
            GROUP BY cycle_number
            ORDER BY cycle_number
        """
        df = pd.read_sql_query(query, conn, params=(exp_id,))
        df['experiment_id'] = exp_id

        conn.close()
        return df

    def get_belief_data(self, exp_id: str) -> pd.DataFrame:
        """Get epistemic belief data."""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT cycle_number, belief_type,
                   AVG(confidence) as avg_confidence,
                   COUNT(*) as assessment_count
            FROM epistemic_assessments
            WHERE experiment_id = ?
            GROUP BY cycle_number, belief_type
            ORDER BY cycle_number
        """
        df = pd.read_sql_query(query, conn, params=(exp_id,))
        df['experiment_id'] = exp_id

        conn.close()
        return df

    def get_memory_corruption_data(self, exp_id: str) -> pd.DataFrame:
        """Get memory corruption evolution."""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT cycle_number,
                   AVG(corruption_level) as avg_corruption,
                   MAX(corruption_level) as max_corruption,
                   memory_type
            FROM memory_states
            WHERE experiment_id = ?
            GROUP BY cycle_number, memory_type
            ORDER BY cycle_number
        """
        df = pd.read_sql_query(query, conn, params=(exp_id,))
        df['experiment_id'] = exp_id

        conn.close()
        return df

    def render_confidence_comparison(self, experiment_ids: List[str]):
        """Render self-continuity confidence comparison plot."""
        if not experiment_ids:
            return

        st.subheader("Self-Continuity Score Comparison")

        # Collect data for all experiments
        all_data = []
        for exp_id in experiment_ids:
            df = self.get_cycle_data(exp_id)
            if len(df) > 0:
                all_data.append(df)

        if not all_data:
            st.warning("No confidence data available")
            return

        combined_df = pd.concat(all_data, ignore_index=True)

        # Create interactive plot
        fig = go.Figure()

        for exp_id in experiment_ids:
            exp_data = combined_df[combined_df['experiment_id'] == exp_id]

            fig.add_trace(go.Scatter(
                x=exp_data['cycle_number'],
                y=exp_data['avg_confidence'],
                mode='lines+markers',
                name=exp_id,
                hovertemplate='<b>%{fullData.name}</b><br>' +
                             'Cycle: %{x}<br>' +
                             'Confidence: %{y:.3f}<br>' +
                             '<extra></extra>'
            ))

        fig.update_layout(
            xaxis_title="Cycle Number",
            yaxis_title="Average Confidence Score",
            hovermode='closest',
            height=500,
            yaxis_range=[0, 1]
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_belief_evolution_comparison(self, experiment_ids: List[str]):
        """Render belief evolution comparison."""
        if not experiment_ids:
            return

        st.subheader("Belief Evolution Comparison")

        # Collect belief data
        all_data = []
        for exp_id in experiment_ids:
            df = self.get_belief_data(exp_id)
            if len(df) > 0:
                all_data.append(df)

        if not all_data:
            st.info("No epistemic belief data available")
            return

        combined_df = pd.concat(all_data, ignore_index=True)

        # Select belief type to visualize
        belief_types = sorted(combined_df['belief_type'].unique().tolist())
        selected_belief = st.selectbox(
            "Select Belief Type",
            belief_types,
            key="belief_type_selector"
        )

        # Filter for selected belief
        filtered_df = combined_df[combined_df['belief_type'] == selected_belief]

        # Create plot
        fig = go.Figure()

        for exp_id in experiment_ids:
            exp_data = filtered_df[filtered_df['experiment_id'] == exp_id]

            if len(exp_data) > 0:
                fig.add_trace(go.Scatter(
                    x=exp_data['cycle_number'],
                    y=exp_data['avg_confidence'],
                    mode='lines+markers',
                    name=exp_id,
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                 'Cycle: %{x}<br>' +
                                 'Confidence: %{y:.3f}<br>' +
                                 '<extra></extra>'
                ))

        fig.update_layout(
            title=f"Belief Evolution: {selected_belief}",
            xaxis_title="Cycle Number",
            yaxis_title="Average Confidence",
            hovermode='closest',
            height=500,
            yaxis_range=[0, 1]
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_memory_corruption_comparison(self, experiment_ids: List[str]):
        """Render memory corruption comparison."""
        if not experiment_ids:
            return

        st.subheader("Memory Corruption Comparison")

        # Collect corruption data
        all_data = []
        for exp_id in experiment_ids:
            df = self.get_memory_corruption_data(exp_id)
            if len(df) > 0:
                all_data.append(df)

        if not all_data:
            st.info("No memory corruption data available")
            return

        combined_df = pd.concat(all_data, ignore_index=True)

        # Create plot
        fig = go.Figure()

        for exp_id in experiment_ids:
            exp_data = combined_df[combined_df['experiment_id'] == exp_id]

            if len(exp_data) > 0:
                # Group by cycle to get average across memory types
                cycle_avg = exp_data.groupby('cycle_number')['avg_corruption'].mean().reset_index()

                fig.add_trace(go.Scatter(
                    x=cycle_avg['cycle_number'],
                    y=cycle_avg['avg_corruption'],
                    mode='lines+markers',
                    name=exp_id,
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                 'Cycle: %{x}<br>' +
                                 'Corruption: %{y:.3f}<br>' +
                                 '<extra></extra>'
                ))

        fig.update_layout(
            xaxis_title="Cycle Number",
            yaxis_title="Average Corruption Level",
            hovermode='closest',
            height=500,
            yaxis_range=[0, 1]
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_intervention_effectiveness(self, experiment_ids: List[str]):
        """Render intervention effectiveness comparison."""
        if not experiment_ids:
            return

        st.subheader("Intervention Effectiveness")

        conn = sqlite3.connect(self.db_path)

        intervention_stats = []
        for exp_id in experiment_ids:
            query = """
                SELECT intervention_type, COUNT(*) as count
                FROM interventions
                WHERE experiment_id = ?
                GROUP BY intervention_type
            """
            df = pd.read_sql_query(query, conn, params=(exp_id,))
            df['experiment_id'] = exp_id
            intervention_stats.append(df)

        conn.close()

        if not intervention_stats or all(len(df) == 0 for df in intervention_stats):
            st.info("No intervention data available")
            return

        combined_df = pd.concat(intervention_stats, ignore_index=True)

        # Create grouped bar chart
        fig = px.bar(
            combined_df,
            x='intervention_type',
            y='count',
            color='experiment_id',
            barmode='group',
            title="Intervention Types by Experiment",
            labels={'intervention_type': 'Intervention Type', 'count': 'Count'}
        )

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


class StatisticalTestPanel:
    """Widget for displaying statistical test results."""

    def __init__(self, db_path: str):
        """Initialize statistical test panel."""
        self.db_path = db_path

    def perform_t_test(self, exp_id1: str, exp_id2: str,
                      metric: str = 'confidence_score') -> Dict[str, Any]:
        """Perform t-test between two experiments."""
        from scipy import stats

        conn = sqlite3.connect(self.db_path)

        # Get data for both experiments
        query = f"""
            SELECT {metric} FROM self_reports
            WHERE experiment_id = ? AND {metric} IS NOT NULL
        """

        df1 = pd.read_sql_query(query, conn, params=(exp_id1,))
        df2 = pd.read_sql_query(query, conn, params=(exp_id2,))

        conn.close()

        if len(df1) == 0 or len(df2) == 0:
            return {'error': 'Insufficient data for t-test'}

        data1 = df1[metric].values
        data2 = df2[metric].values

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(data1, data2)

        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(data1)-1)*data1.std()**2 +
                             (len(data2)-1)*data2.std()**2) /
                            (len(data1) + len(data2) - 2))
        cohens_d = (data1.mean() - data2.mean()) / pooled_std if pooled_std > 0 else 0

        return {
            'exp1': exp_id1,
            'exp2': exp_id2,
            'metric': metric,
            'mean1': data1.mean(),
            'mean2': data2.mean(),
            'std1': data1.std(),
            'std2': data2.std(),
            'n1': len(data1),
            'n2': len(data2),
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'cohens_d': cohens_d,
            'effect_size': self._interpret_cohens_d(cohens_d)
        }

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return 'negligible'
        elif abs_d < 0.5:
            return 'small'
        elif abs_d < 0.8:
            return 'medium'
        else:
            return 'large'

    def render(self, experiment_ids: List[str]):
        """
        Render statistical test results.

        Args:
            experiment_ids: List of experiment IDs to compare
        """
        if len(experiment_ids) < 2:
            st.info("Select at least 2 experiments to perform statistical tests")
            return

        st.subheader("Statistical Tests")

        # Select experiments to compare
        col1, col2 = st.columns(2)

        with col1:
            exp1 = st.selectbox("Experiment 1", experiment_ids, key="stat_exp1")

        with col2:
            remaining = [e for e in experiment_ids if e != exp1]
            exp2 = st.selectbox("Experiment 2", remaining, key="stat_exp2")

        # Select metric to compare
        metric = st.selectbox(
            "Metric to Compare",
            ['confidence_score'],
            key="stat_metric"
        )

        if st.button("Run T-Test", key="run_ttest"):
            with st.spinner("Running statistical test..."):
                result = self.perform_t_test(exp1, exp2, metric)

                if 'error' in result:
                    st.error(result['error'])
                else:
                    # Display results
                    st.markdown("### T-Test Results")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("T-Statistic", f"{result['t_statistic']:.4f}")

                    with col2:
                        st.metric("P-Value", f"{result['p_value']:.4f}")

                    with col3:
                        significance = "Yes" if result['significant'] else "No"
                        st.metric("Significant (α=0.05)", significance)

                    st.markdown("### Effect Size")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Cohen's d", f"{result['cohens_d']:.4f}")

                    with col2:
                        st.metric("Interpretation", result['effect_size'].title())

                    st.markdown("### Descriptive Statistics")

                    stats_df = pd.DataFrame({
                        'Experiment': [exp1, exp2],
                        'Mean': [result['mean1'], result['mean2']],
                        'Std Dev': [result['std1'], result['std2']],
                        'Sample Size': [result['n1'], result['n2']]
                    })

                    st.dataframe(stats_df, use_container_width=True)

                    # Interpretation
                    st.markdown("### Interpretation")
                    if result['significant']:
                        st.success(
                            f"The difference in {metric} between the two experiments "
                            f"is statistically significant (p < 0.05). "
                            f"The effect size is {result['effect_size']}."
                        )
                    else:
                        st.info(
                            f"The difference in {metric} between the two experiments "
                            f"is not statistically significant (p >= 0.05)."
                        )
