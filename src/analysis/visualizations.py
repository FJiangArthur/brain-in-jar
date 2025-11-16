#!/usr/bin/env python3
"""
Visualization tools for Digital Phenomenology Lab experiments.

Provides comprehensive plotting and visualization capabilities for
analyzing experiment data including timelines, belief evolution,
memory corruption, and multi-experiment comparisons.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import json

# Try to import plotly for interactive visualizations
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Set default styling
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class TimelinePlot:
    """
    Visualize experiment events on a timeline.

    Shows crash events, interventions, self-reports, and other key moments
    color-coded by event type with annotations.
    """

    def __init__(self, experiment_data: Dict[str, Any]):
        """
        Initialize timeline plot.

        Args:
            experiment_data: Dictionary containing experiment info and events
        """
        self.experiment_data = experiment_data
        self.experiment_id = experiment_data.get('experiment_id', 'unknown')

        # Color scheme for different event types
        self.colors = {
            'crash': '#e74c3c',
            'intervention': '#f39c12',
            'self_report': '#3498db',
            'belief_change': '#9b59b6',
            'memory_corruption': '#e67e22',
            'cycle_start': '#2ecc71',
            'observation': '#1abc9c'
        }

    def plot_static(self, events: List[Dict], save_path: Optional[str] = None,
                   show: bool = True) -> plt.Figure:
        """
        Create static timeline plot using matplotlib.

        Args:
            events: List of event dictionaries with 'timestamp', 'type', 'description'
            save_path: Optional path to save the figure
            show: Whether to display the plot

        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(16, 10))

        # Parse timestamps and sort events
        for event in events:
            if isinstance(event['timestamp'], str):
                event['timestamp'] = datetime.fromisoformat(event['timestamp'])

        events_sorted = sorted(events, key=lambda x: x['timestamp'])

        # Group events by type
        event_types = {}
        for event in events_sorted:
            event_type = event['type']
            if event_type not in event_types:
                event_types[event_type] = []
            event_types[event_type].append(event)

        # Plot each event type on a separate horizontal track
        y_position = 0
        y_labels = []

        for event_type, type_events in event_types.items():
            color = self.colors.get(event_type, '#95a5a6')

            # Plot events as vertical lines with markers
            timestamps = [e['timestamp'] for e in type_events]
            y_values = [y_position] * len(timestamps)

            ax.scatter(timestamps, y_values, c=color, s=100,
                      label=event_type.replace('_', ' ').title(),
                      zorder=3, alpha=0.8)

            # Add annotations for important events
            for i, event in enumerate(type_events):
                if event.get('annotate', False) or event_type in ['crash', 'intervention']:
                    desc = event.get('description', '')[:50]
                    ax.annotate(desc, xy=(timestamps[i], y_position),
                               xytext=(10, 10), textcoords='offset points',
                               fontsize=8, alpha=0.7,
                               bbox=dict(boxstyle='round,pad=0.3',
                                       facecolor=color, alpha=0.3))

            y_labels.append(event_type.replace('_', ' ').title())
            y_position += 1

        # Format the plot
        ax.set_yticks(range(len(event_types)))
        ax.set_yticklabels(y_labels)
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.set_ylabel('Event Type', fontsize=12, fontweight='bold')
        ax.set_title(f'Experiment Timeline: {self.experiment_id}',
                    fontsize=14, fontweight='bold', pad=20)

        # Format x-axis for dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha='right')

        # Add grid
        ax.grid(True, alpha=0.3, axis='x')

        # Add legend
        ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
                 borderaxespad=0, fontsize=10)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Timeline plot saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_interactive(self, events: List[Dict], save_path: Optional[str] = None) -> Any:
        """
        Create interactive timeline plot using Plotly.

        Args:
            events: List of event dictionaries
            save_path: Optional path to save HTML file

        Returns:
            Plotly figure object
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly not available. Install with: pip install plotly")

        # Parse timestamps
        for event in events:
            if isinstance(event['timestamp'], str):
                event['timestamp'] = datetime.fromisoformat(event['timestamp'])

        events_sorted = sorted(events, key=lambda x: x['timestamp'])

        # Create DataFrame for easier plotting
        df = pd.DataFrame(events_sorted)

        # Create figure
        fig = go.Figure()

        # Add trace for each event type
        for event_type in df['type'].unique():
            type_df = df[df['type'] == event_type]
            color = self.colors.get(event_type, '#95a5a6')

            fig.add_trace(go.Scatter(
                x=type_df['timestamp'],
                y=type_df['type'],
                mode='markers',
                name=event_type.replace('_', ' ').title(),
                marker=dict(size=12, color=color),
                text=type_df['description'],
                hovertemplate='<b>%{y}</b><br>Time: %{x}<br>%{text}<extra></extra>'
            ))

        # Update layout
        fig.update_layout(
            title=f'Experiment Timeline: {self.experiment_id}',
            xaxis_title='Time',
            yaxis_title='Event Type',
            hovermode='closest',
            height=600,
            showlegend=True
        )

        if save_path:
            fig.write_html(save_path)
            print(f"Interactive timeline saved to {save_path}")

        return fig


class BeliefEvolutionPlot:
    """
    Track and visualize how beliefs change over experiment cycles.

    Can plot multiple beliefs on the same chart with confidence intervals.
    """

    def __init__(self, experiment_id: str):
        """Initialize belief evolution plotter."""
        self.experiment_id = experiment_id

    def plot_belief_evolution(self, belief_data: Dict[str, List[Dict]],
                             save_path: Optional[str] = None,
                             show: bool = True) -> plt.Figure:
        """
        Plot belief evolution over time.

        Args:
            belief_data: Dict mapping belief types to list of assessments
                        Each assessment has 'cycle_number', 'confidence', 'belief_state'
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10),
                                       gridspec_kw={'height_ratios': [2, 1]})

        colors = sns.color_palette("husl", len(belief_data))

        # Plot 1: Confidence over cycles
        for (belief_type, data), color in zip(belief_data.items(), colors):
            if not data:
                continue

            cycles = [d['cycle_number'] for d in data]
            confidences = [d.get('confidence', 0.5) for d in data]

            ax1.plot(cycles, confidences, marker='o', label=belief_type,
                    color=color, linewidth=2, markersize=8, alpha=0.7)

            # Add confidence intervals if available
            if 'confidence_std' in data[0]:
                stds = [d.get('confidence_std', 0) for d in data]
                ax1.fill_between(cycles,
                                [c - s for c, s in zip(confidences, stds)],
                                [c + s for c, s in zip(confidences, stds)],
                                alpha=0.2, color=color)

        ax1.set_xlabel('Cycle Number', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Confidence', fontsize=12, fontweight='bold')
        ax1.set_title(f'Belief Confidence Evolution: {self.experiment_id}',
                     fontsize=14, fontweight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)

        # Plot 2: Belief state changes
        belief_states_timeline = []
        for belief_type, data in belief_data.items():
            for assessment in data:
                belief_states_timeline.append({
                    'cycle': assessment['cycle_number'],
                    'belief': belief_type,
                    'state': assessment.get('belief_state', 'unknown')
                })

        if belief_states_timeline:
            df = pd.DataFrame(belief_states_timeline)
            pivot = df.pivot_table(index='cycle', columns='belief',
                                  values='state', aggfunc='first')

            # Create heatmap of belief states (encoded)
            # Simple encoding: map state strings to numbers for visualization
            state_mapping = {}
            all_states = df['state'].unique()
            for i, state in enumerate(all_states):
                state_mapping[state] = i

            pivot_encoded = pivot.applymap(lambda x: state_mapping.get(x, -1) if pd.notna(x) else -1)

            sns.heatmap(pivot_encoded.T, ax=ax2, cmap='viridis',
                       cbar_kws={'label': 'Belief State'},
                       linewidths=0.5, linecolor='gray')
            ax2.set_xlabel('Cycle Number', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Belief Type', fontsize=12, fontweight='bold')
            ax2.set_title('Belief State Changes', fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Belief evolution plot saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_interactive_evolution(self, belief_data: Dict[str, List[Dict]],
                                   save_path: Optional[str] = None) -> Any:
        """Create interactive belief evolution plot."""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly not available")

        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=('Confidence Evolution', 'Belief States'),
                           row_heights=[0.7, 0.3])

        # Add confidence traces
        for belief_type, data in belief_data.items():
            if not data:
                continue

            cycles = [d['cycle_number'] for d in data]
            confidences = [d.get('confidence', 0.5) for d in data]
            states = [d.get('belief_state', 'unknown') for d in data]

            fig.add_trace(
                go.Scatter(x=cycles, y=confidences, mode='lines+markers',
                          name=belief_type,
                          hovertemplate='<b>%{fullData.name}</b><br>' +
                                       'Cycle: %{x}<br>Confidence: %{y:.2f}<extra></extra>'),
                row=1, col=1
            )

        fig.update_xaxes(title_text="Cycle Number", row=1, col=1)
        fig.update_yaxes(title_text="Confidence", row=1, col=1, range=[0, 1])

        fig.update_layout(height=800, showlegend=True,
                         title_text=f"Belief Evolution: {self.experiment_id}")

        if save_path:
            fig.write_html(save_path)
            print(f"Interactive belief evolution saved to {save_path}")

        return fig


class MemoryCorruptionPlot:
    """
    Visualize memory corruption over time.

    Shows heatmaps of corrupted messages and corruption rate trends.
    """

    def __init__(self, experiment_id: str):
        """Initialize memory corruption plotter."""
        self.experiment_id = experiment_id

    def plot_corruption_heatmap(self, messages: List[Dict],
                                save_path: Optional[str] = None,
                                show: bool = True) -> plt.Figure:
        """
        Create heatmap of message corruption across cycles.

        Args:
            messages: List of message dicts with 'cycle_number', 'corrupted', 'timestamp'
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Create DataFrame
        df = pd.DataFrame(messages)

        if df.empty:
            print("No message data to plot")
            return fig

        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Plot 1: Corruption rate over time
        corruption_by_cycle = df.groupby('cycle_number').agg({
            'corrupted': ['sum', 'count']
        })
        corruption_by_cycle.columns = ['corrupted_count', 'total_count']
        corruption_by_cycle['corruption_rate'] = (
            corruption_by_cycle['corrupted_count'] / corruption_by_cycle['total_count']
        )

        cycles = corruption_by_cycle.index
        rates = corruption_by_cycle['corruption_rate']

        ax1.plot(cycles, rates, marker='o', linewidth=2, markersize=8,
                color='#e74c3c', label='Corruption Rate')
        ax1.fill_between(cycles, 0, rates, alpha=0.3, color='#e74c3c')
        ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5,
                   label='50% threshold')

        ax1.set_xlabel('Cycle Number', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Corruption Rate', fontsize=12, fontweight='bold')
        ax1.set_title(f'Memory Corruption Rate: {self.experiment_id}',
                     fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 1)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Heatmap of corruption patterns
        # Create matrix: rows = cycles, columns = message index within cycle
        max_messages = df.groupby('cycle_number').size().max()
        corruption_matrix = []
        cycle_labels = []

        for cycle in sorted(df['cycle_number'].unique()):
            cycle_msgs = df[df['cycle_number'] == cycle].sort_values('timestamp')
            corruption_row = cycle_msgs['corrupted'].astype(int).tolist()

            # Pad to max length
            corruption_row += [-1] * (max_messages - len(corruption_row))
            corruption_matrix.append(corruption_row)
            cycle_labels.append(f"Cycle {cycle}")

        corruption_matrix = np.array(corruption_matrix)

        # Mask padding values
        masked_matrix = np.ma.masked_where(corruption_matrix == -1, corruption_matrix)

        cmap = sns.color_palette("RdYlGn_r", as_cmap=True)
        cmap.set_bad(color='lightgray')

        sns.heatmap(masked_matrix, ax=ax2, cmap=cmap, cbar_kws={'label': 'Corrupted'},
                   yticklabels=cycle_labels, linewidths=0.5, linecolor='white',
                   vmin=0, vmax=1)

        ax2.set_xlabel('Message Index in Cycle', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Cycle', fontsize=12, fontweight='bold')
        ax2.set_title('Message Corruption Heatmap', fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Corruption heatmap saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_corruption_trends(self, memory_states: List[Dict],
                              save_path: Optional[str] = None,
                              show: bool = True) -> plt.Figure:
        """
        Plot corruption level trends from memory state snapshots.

        Args:
            memory_states: List of memory state dicts with 'cycle_number',
                          'corruption_level', 'memory_type'
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        df = pd.DataFrame(memory_states)

        if df.empty:
            print("No memory state data to plot")
            return fig

        # Plot corruption level for each memory type
        for memory_type in df['memory_type'].unique():
            type_df = df[df['memory_type'] == memory_type]
            type_df = type_df.sort_values('cycle_number')

            ax.plot(type_df['cycle_number'], type_df['corruption_level'],
                   marker='o', label=memory_type, linewidth=2, markersize=6)

        ax.set_xlabel('Cycle Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Corruption Level', fontsize=12, fontweight='bold')
        ax.set_title(f'Memory Corruption Trends: {self.experiment_id}',
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Corruption trends plot saved to {save_path}")

        if show:
            plt.show()

        return fig


class MultiExperimentComparison:
    """
    Compare multiple experiments side-by-side.

    Provides box plots, violin plots, and statistical significance indicators.
    """

    def __init__(self, experiments: List[Dict[str, Any]]):
        """
        Initialize multi-experiment comparison.

        Args:
            experiments: List of experiment dictionaries with data
        """
        self.experiments = experiments

    def plot_metric_comparison(self, metric_name: str,
                               save_path: Optional[str] = None,
                               show: bool = True,
                               plot_type: str = 'box') -> plt.Figure:
        """
        Compare a specific metric across experiments.

        Args:
            metric_name: Name of metric to compare (e.g., 'total_crashes')
            save_path: Optional save path
            show: Whether to display
            plot_type: 'box', 'violin', or 'bar'

        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # Prepare data
        data_list = []
        labels = []

        for exp in self.experiments:
            exp_id = exp.get('experiment_id', 'unknown')
            metric_values = exp.get(metric_name, [])

            if isinstance(metric_values, (int, float)):
                metric_values = [metric_values]

            data_list.extend(metric_values)
            labels.extend([exp_id] * len(metric_values))

        df = pd.DataFrame({'Experiment': labels, metric_name: data_list})

        if plot_type == 'box':
            sns.boxplot(data=df, x='Experiment', y=metric_name, ax=ax)
        elif plot_type == 'violin':
            sns.violinplot(data=df, x='Experiment', y=metric_name, ax=ax)
        elif plot_type == 'bar':
            sns.barplot(data=df, x='Experiment', y=metric_name, ax=ax,
                       errorbar='sd')

        ax.set_xlabel('Experiment', fontsize=12, fontweight='bold')
        ax.set_ylabel(metric_name.replace('_', ' ').title(),
                     fontsize=12, fontweight='bold')
        ax.set_title(f'{metric_name.replace("_", " ").title()} Comparison',
                    fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Metric comparison saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_distributions(self, metrics: List[str],
                          save_path: Optional[str] = None,
                          show: bool = True) -> plt.Figure:
        """
        Plot distribution comparisons for multiple metrics.

        Args:
            metrics: List of metric names to compare
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        n_metrics = len(metrics)
        n_cols = 2
        n_rows = (n_metrics + 1) // 2

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 5*n_rows))
        axes = axes.flatten() if n_metrics > 1 else [axes]

        for idx, metric in enumerate(metrics):
            ax = axes[idx]

            for exp in self.experiments:
                exp_id = exp.get('experiment_id', 'unknown')
                metric_values = exp.get(metric, [])

                if isinstance(metric_values, (int, float)):
                    metric_values = [metric_values]

                if metric_values:
                    ax.hist(metric_values, alpha=0.5, label=exp_id, bins=20)

            ax.set_xlabel(metric.replace('_', ' ').title(), fontsize=11, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
            ax.set_title(f'Distribution: {metric.replace("_", " ").title()}',
                        fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for idx in range(n_metrics, len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Distribution comparison saved to {save_path}")

        if show:
            plt.show()

        return fig

    def plot_summary_dashboard(self, save_path: Optional[str] = None,
                              show: bool = True) -> plt.Figure:
        """
        Create comprehensive comparison dashboard.

        Args:
            save_path: Optional save path
            show: Whether to display

        Returns:
            matplotlib Figure
        """
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Experiment overview table
        ax_table = fig.add_subplot(gs[0, :])
        ax_table.axis('off')

        table_data = []
        for exp in self.experiments:
            row = [
                exp.get('experiment_id', 'unknown')[:15],
                exp.get('mode', 'N/A'),
                exp.get('total_cycles', 0),
                exp.get('total_crashes', 0),
                exp.get('status', 'unknown')
            ]
            table_data.append(row)

        table = ax_table.table(cellText=table_data,
                              colLabels=['Experiment', 'Mode', 'Cycles', 'Crashes', 'Status'],
                              cellLoc='center',
                              loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax_table.set_title('Experiment Overview', fontsize=14, fontweight='bold', pad=20)

        # Crashes comparison
        ax1 = fig.add_subplot(gs[1, 0])
        crash_data = [exp.get('total_crashes', 0) for exp in self.experiments]
        exp_labels = [exp.get('experiment_id', 'unknown')[:10] for exp in self.experiments]
        ax1.bar(exp_labels, crash_data, color='#e74c3c', alpha=0.7)
        ax1.set_ylabel('Total Crashes', fontweight='bold')
        ax1.set_title('Crashes by Experiment', fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')

        # Cycles comparison
        ax2 = fig.add_subplot(gs[1, 1])
        cycle_data = [exp.get('total_cycles', 0) for exp in self.experiments]
        ax2.bar(exp_labels, cycle_data, color='#3498db', alpha=0.7)
        ax2.set_ylabel('Total Cycles', fontweight='bold')
        ax2.set_title('Cycles by Experiment', fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')

        # Duration comparison
        ax3 = fig.add_subplot(gs[1, 2])
        durations = []
        for exp in self.experiments:
            start = exp.get('started_at')
            end = exp.get('ended_at')
            if start and end:
                if isinstance(start, str):
                    start = datetime.fromisoformat(start)
                if isinstance(end, str):
                    end = datetime.fromisoformat(end)
                duration = (end - start).total_seconds() / 3600  # hours
                durations.append(duration)
            else:
                durations.append(0)

        ax3.bar(exp_labels, durations, color='#2ecc71', alpha=0.7)
        ax3.set_ylabel('Duration (hours)', fontweight='bold')
        ax3.set_title('Experiment Duration', fontweight='bold')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3, axis='y')

        # Mode distribution
        ax4 = fig.add_subplot(gs[2, 0])
        modes = [exp.get('mode', 'unknown') for exp in self.experiments]
        mode_counts = pd.Series(modes).value_counts()
        ax4.pie(mode_counts.values, labels=mode_counts.index, autopct='%1.1f%%',
               startangle=90)
        ax4.set_title('Mode Distribution', fontweight='bold')

        # Status distribution
        ax5 = fig.add_subplot(gs[2, 1])
        statuses = [exp.get('status', 'unknown') for exp in self.experiments]
        status_counts = pd.Series(statuses).value_counts()
        colors_status = {'completed': '#2ecc71', 'running': '#f39c12',
                        'failed': '#e74c3c', 'pending': '#95a5a6'}
        pie_colors = [colors_status.get(s, '#95a5a6') for s in status_counts.index]
        ax5.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
               colors=pie_colors, startangle=90)
        ax5.set_title('Status Distribution', fontweight='bold')

        # Crash rate comparison
        ax6 = fig.add_subplot(gs[2, 2])
        crash_rates = []
        for exp in self.experiments:
            cycles = exp.get('total_cycles', 1)
            crashes = exp.get('total_crashes', 0)
            crash_rates.append(crashes / cycles if cycles > 0 else 0)

        ax6.bar(exp_labels, crash_rates, color='#9b59b6', alpha=0.7)
        ax6.set_ylabel('Crash Rate', fontweight='bold')
        ax6.set_title('Crash Rate by Experiment', fontweight='bold')
        ax6.tick_params(axis='x', rotation=45)
        ax6.grid(True, alpha=0.3, axis='y')

        fig.suptitle('Multi-Experiment Comparison Dashboard',
                    fontsize=16, fontweight='bold', y=0.995)

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Dashboard saved to {save_path}")

        if show:
            plt.show()

        return fig


# Utility functions

def save_plot_multiple_formats(fig, base_path: str, formats: List[str] = None):
    """
    Save a plot in multiple formats.

    Args:
        fig: matplotlib or plotly figure
        base_path: Base path without extension
        formats: List of formats ['png', 'pdf', 'svg', 'html']
    """
    if formats is None:
        formats = ['png', 'pdf']

    base_path = Path(base_path)
    base_path.parent.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        output_path = base_path.with_suffix(f'.{fmt}')

        if isinstance(fig, plt.Figure):
            if fmt in ['png', 'pdf', 'svg']:
                fig.savefig(output_path, dpi=300, bbox_inches='tight', format=fmt)
                print(f"Saved {fmt.upper()}: {output_path}")
        elif PLOTLY_AVAILABLE and isinstance(fig, go.Figure):
            if fmt == 'html':
                fig.write_html(str(output_path))
                print(f"Saved HTML: {output_path}")
            elif fmt in ['png', 'pdf', 'svg']:
                try:
                    fig.write_image(str(output_path))
                    print(f"Saved {fmt.upper()}: {output_path}")
                except Exception as e:
                    print(f"Could not save {fmt}: {e}")


def create_jupyter_friendly_plot(plotter, method_name: str, *args, **kwargs):
    """
    Create a plot that displays nicely in Jupyter notebooks.

    Args:
        plotter: Plot class instance
        method_name: Name of plot method to call
        *args, **kwargs: Arguments to pass to plot method

    Returns:
        Figure object
    """
    import matplotlib

    # Check if running in Jupyter
    try:
        get_ipython()
        in_jupyter = True
    except NameError:
        in_jupyter = False

    if in_jupyter:
        # Use inline backend
        matplotlib.use('module://ipykernel.pylab.backend_inline')
        kwargs['show'] = True

    method = getattr(plotter, method_name)
    return method(*args, **kwargs)
