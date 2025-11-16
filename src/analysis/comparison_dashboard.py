#!/usr/bin/env python3
"""
Interactive Comparison Dashboard for Digital Phenomenology Lab Experiments.

Provides a Streamlit-based web interface for comparing multiple experiments
with interactive plots, statistical tests, and export capabilities.

Features:
- Multi-experiment selection with filtering
- Side-by-side metrics comparison
- Interactive time-series plots (confidence, beliefs, memory corruption)
- Statistical significance testing
- Export comparison reports to CSV/JSON/PDF
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import io
import base64

# Import custom components
from src.analysis.dashboard_components import (
    ExperimentSelector,
    MetricsTable,
    ComparisonPlot,
    StatisticalTestPanel
)

# Import analysis modules
from src.analysis.statistics import ExperimentStatistics
from src.analysis.metrics import MetricsCalculator


class ComparisonDashboard:
    """
    Main comparison dashboard class.

    Coordinates all dashboard components and manages state.
    """

    def __init__(self, db_path: str = "logs/experiments.db"):
        """
        Initialize the comparison dashboard.

        Args:
            db_path: Path to the experiments database
        """
        self.db_path = db_path
        self.stats_engine = ExperimentStatistics(db_path)
        self.metrics_calc = MetricsCalculator(db_path)

        # Initialize components
        self.exp_selector = ExperimentSelector(db_path)
        self.metrics_table = MetricsTable(db_path)
        self.comparison_plot = ComparisonPlot(db_path)
        self.stats_panel = StatisticalTestPanel(db_path)

    def configure_page(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Brain-in-Jar: Experiment Comparison",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS for better styling
        st.markdown("""
            <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 1rem;
            }
            .sub-header {
                font-size: 1.2rem;
                color: #666;
                text-align: center;
                margin-bottom: 2rem;
            }
            .metric-card {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # Header
        st.markdown('<p class="main-header">🧠 Digital Phenomenology Lab</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Interactive Experiment Comparison Dashboard</p>', unsafe_allow_html=True)

    def render_sidebar(self) -> Dict[str, Any]:
        """
        Render sidebar with experiment selection and filtering options.

        Returns:
            Dictionary with sidebar configuration
        """
        with st.sidebar:
            st.title("Dashboard Controls")

            # Database info
            st.info(f"📊 Database: `{self.db_path}`")

            # Experiment selector
            selected_experiments = self.exp_selector.render()

            st.markdown("---")

            # View options
            st.subheader("View Options")

            show_metrics_table = st.checkbox("Show Metrics Table", value=True)
            show_confidence_plot = st.checkbox("Show Confidence Comparison", value=True)
            show_belief_plot = st.checkbox("Show Belief Evolution", value=True)
            show_memory_plot = st.checkbox("Show Memory Corruption", value=True)
            show_intervention_plot = st.checkbox("Show Interventions", value=True)
            show_stats_panel = st.checkbox("Show Statistical Tests", value=False)

            st.markdown("---")

            # Export options
            st.subheader("Export Options")

            if st.button("📥 Export Comparison Report", use_container_width=True):
                if selected_experiments:
                    self.export_comparison_report(selected_experiments)
                else:
                    st.warning("Select experiments first")

            st.markdown("---")

            # About section
            with st.expander("ℹ️ About This Dashboard"):
                st.markdown("""
                **Brain-in-Jar Experiment Dashboard**

                This dashboard allows you to:
                - Compare multiple experiments side-by-side
                - Visualize temporal patterns in beliefs and behaviors
                - Analyze statistical significance of differences
                - Export comprehensive comparison reports

                **How to use:**
                1. Select experiments using the filters above
                2. Choose which visualizations to display
                3. Explore interactive plots (hover, zoom, pan)
                4. Run statistical tests to compare experiments
                5. Export results for further analysis
                """)

            return {
                'selected_experiments': selected_experiments,
                'show_metrics_table': show_metrics_table,
                'show_confidence_plot': show_confidence_plot,
                'show_belief_plot': show_belief_plot,
                'show_memory_plot': show_memory_plot,
                'show_intervention_plot': show_intervention_plot,
                'show_stats_panel': show_stats_panel
            }

    def render_main_content(self, config: Dict[str, Any]):
        """
        Render main dashboard content.

        Args:
            config: Configuration from sidebar
        """
        selected_experiments = config['selected_experiments']

        if not selected_experiments:
            # Welcome screen
            st.markdown("## Welcome to the Experiment Comparison Dashboard")
            st.markdown("""
            👈 **Get started by selecting experiments from the sidebar**

            This dashboard provides comprehensive comparison tools for analyzing
            Digital Phenomenology Lab experiments.

            ### Features:
            - 📊 **Metrics Comparison**: Side-by-side comparison of key metrics
            - 📈 **Time-Series Analysis**: Track changes across cycles
            - 🧪 **Statistical Tests**: Validate differences between experiments
            - 💾 **Export Reports**: Generate comprehensive comparison reports
            - 🔍 **Interactive Visualizations**: Zoom, filter, and explore data

            Select one or more experiments from the sidebar to begin.
            """)

            # Show summary statistics
            st.markdown("### Database Overview")
            self.render_database_summary()

        else:
            # Show comparison views
            if config['show_metrics_table']:
                metrics_df = self.metrics_table.render(selected_experiments)
                st.markdown("---")

            if config['show_confidence_plot']:
                self.comparison_plot.render_confidence_comparison(selected_experiments)
                st.markdown("---")

            if config['show_belief_plot']:
                self.comparison_plot.render_belief_evolution_comparison(selected_experiments)
                st.markdown("---")

            if config['show_memory_plot']:
                self.comparison_plot.render_memory_corruption_comparison(selected_experiments)
                st.markdown("---")

            if config['show_intervention_plot']:
                self.comparison_plot.render_intervention_effectiveness(selected_experiments)
                st.markdown("---")

            if config['show_stats_panel']:
                self.stats_panel.render(selected_experiments)
                st.markdown("---")

    def render_database_summary(self):
        """Render a summary of the database contents."""
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get counts
        cursor.execute("SELECT COUNT(*) FROM experiments")
        total_experiments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'completed'")
        completed_experiments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'running'")
        running_experiments = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM self_reports")
        total_reports = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM interventions")
        total_interventions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM epistemic_assessments")
        total_assessments = cursor.fetchone()[0]

        cursor.execute("SELECT DISTINCT mode FROM experiments")
        modes = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Experiments", total_experiments)
            st.metric("Completed", completed_experiments)

        with col2:
            st.metric("Running", running_experiments)
            st.metric("Self Reports", total_reports)

        with col3:
            st.metric("Interventions", total_interventions)
            st.metric("Epistemic Assessments", total_assessments)

        with col4:
            st.metric("Experiment Modes", len(modes))
            if modes:
                st.write("**Modes:**")
                for mode in modes:
                    st.write(f"- {mode}")

    def export_comparison_report(self, experiment_ids: List[str]):
        """
        Export comparison report for selected experiments.

        Args:
            experiment_ids: List of experiment IDs to include in report
        """
        if not experiment_ids:
            st.warning("No experiments selected for export")
            return

        st.subheader("Export Comparison Report")

        # Select export format
        export_format = st.radio(
            "Select Export Format",
            ["CSV", "JSON", "Markdown"],
            horizontal=True
        )

        if st.button("Generate Report"):
            with st.spinner("Generating report..."):
                if export_format == "CSV":
                    report_data = self.generate_csv_report(experiment_ids)
                    mime_type = "text/csv"
                    file_ext = "csv"
                elif export_format == "JSON":
                    report_data = self.generate_json_report(experiment_ids)
                    mime_type = "application/json"
                    file_ext = "json"
                else:  # Markdown
                    report_data = self.generate_markdown_report(experiment_ids)
                    mime_type = "text/markdown"
                    file_ext = "md"

                # Create download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"comparison_report_{timestamp}.{file_ext}"

                st.download_button(
                    label=f"Download {export_format} Report",
                    data=report_data,
                    file_name=filename,
                    mime=mime_type
                )

                st.success(f"Report generated successfully! Click the button above to download.")

    def generate_csv_report(self, experiment_ids: List[str]) -> str:
        """Generate CSV comparison report."""
        # Get metrics for all experiments
        metrics_list = []
        for exp_id in experiment_ids:
            metrics = self.metrics_table.get_experiment_metrics(exp_id)
            if metrics:
                metrics_list.append(metrics)

        df = pd.DataFrame(metrics_list)
        return df.to_csv(index=False)

    def generate_json_report(self, experiment_ids: List[str]) -> str:
        """Generate JSON comparison report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'experiments': []
        }

        for exp_id in experiment_ids:
            exp_summary = self.stats_engine.generate_experiment_summary(exp_id)
            report['experiments'].append(exp_summary)

        return json.dumps(report, indent=2, default=str)

    def generate_markdown_report(self, experiment_ids: List[str]) -> str:
        """Generate Markdown comparison report."""
        lines = [
            "# Experiment Comparison Report",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n**Experiments Compared:** {len(experiment_ids)}",
            "\n---\n"
        ]

        # Add metrics table
        lines.append("## Metrics Comparison\n")

        metrics_list = []
        for exp_id in experiment_ids:
            metrics = self.metrics_table.get_experiment_metrics(exp_id)
            if metrics:
                metrics_list.append(metrics)

        if metrics_list:
            df = pd.DataFrame(metrics_list)
            lines.append(df.to_markdown(index=False))
            lines.append("\n")

        # Add individual experiment summaries
        lines.append("\n## Individual Experiment Details\n")

        for exp_id in experiment_ids:
            lines.append(f"\n### Experiment: {exp_id}\n")

            summary = self.stats_engine.generate_experiment_summary(exp_id)

            if 'experiment_info' in summary:
                info = summary['experiment_info']
                lines.extend([
                    f"- **Name:** {info.get('name', 'N/A')}",
                    f"- **Mode:** {info.get('mode', 'N/A')}",
                    f"- **Status:** {info.get('status', 'N/A')}",
                    f"- **Total Cycles:** {info.get('total_cycles', 0)}",
                    f"- **Total Crashes:** {info.get('total_crashes', 0)}",
                    f"- **Duration:** {info.get('duration', 'N/A')} seconds\n"
                ])

            if 'sections' in summary:
                sections = summary['sections']

                if 'self_reports' in sections:
                    sr = sections['self_reports']
                    lines.extend([
                        "\n**Self-Report Statistics:**",
                        f"- Total Reports: {sr.get('total_reports', 0)}",
                        f"- Avg Confidence: {sr.get('avg_confidence', 'N/A')}\n"
                    ])

                if 'interventions' in sections:
                    intv = sections['interventions']
                    lines.extend([
                        "\n**Intervention Statistics:**",
                        f"- Total Interventions: {intv.get('total_interventions', 0)}\n"
                    ])

        lines.append("\n---\n*Report generated by ComparisonDashboard*\n")

        return '\n'.join(lines)

    def run(self):
        """Run the dashboard application."""
        self.configure_page()

        # Render sidebar and get configuration
        config = self.render_sidebar()

        # Render main content
        self.render_main_content(config)

        # Footer
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center; color: gray;'>"
            "Digital Phenomenology Lab - Season 3 | "
            f"Dashboard Version 1.0 | Database: {self.db_path}"
            "</p>",
            unsafe_allow_html=True
        )


def main(db_path: str = "logs/experiments.db", port: int = 8501):
    """
    Main entry point for the dashboard.

    Args:
        db_path: Path to experiments database
        port: Port number for Streamlit server
    """
    dashboard = ComparisonDashboard(db_path)
    dashboard.run()


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    db_path = "logs/experiments.db"
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    main(db_path)
