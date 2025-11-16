# Visualization Tools Guide

## Overview

The Digital Phenomenology Lab includes comprehensive visualization tools for analyzing experiment data. These tools support both static (matplotlib/seaborn) and interactive (Plotly) visualizations, with export capabilities for papers, presentations, and web dashboards.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Plot Types](#plot-types)
4. [Network Graphs](#network-graphs)
5. [Export Formats](#export-formats)
6. [Jupyter Integration](#jupyter-integration)
7. [Jetson Orin Usage](#jetson-orin-usage)

---

## Installation

### Required Dependencies

```bash
pip install -r requirements.txt
```

Core visualization dependencies:
- `matplotlib >= 3.7.0` - Static plotting
- `seaborn >= 0.12.0` - Statistical visualizations
- `pandas >= 2.0.0` - Data manipulation
- `numpy >= 1.24.0` - Numerical operations

Optional dependencies for enhanced features:
- `plotly >= 5.14.0` - Interactive visualizations
- `kaleido >= 0.2.1` - Plotly static image export
- `networkx >= 3.0` - Network graph analysis
- `jupyter >= 1.0.0` - Notebook support

---

## Quick Start

### Basic Usage

```python
from src.db.experiment_database import ExperimentDatabase
from src.analysis.visualizations import TimelinePlot

# Connect to database
db = ExperimentDatabase('logs/experiments.db')

# Get experiment data
experiment_id = 'exp_001'
exp_data = db.get_experiment(experiment_id)

# Gather events
events = []
reports = db.get_self_reports(experiment_id)
for report in reports:
    events.append({
        'type': 'self_report',
        'timestamp': report['timestamp'],
        'description': f"Q: {report['question']}"
    })

# Create timeline plot
timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events, save_path='timeline.png')
```

---

## Plot Types

### 1. TimelinePlot

Visualize experiment events chronologically with color-coded event types and annotations.

**Features:**
- Crash events, interventions, self-reports on timeline
- Color-coded by event type
- Annotations for key moments
- Static (matplotlib) and interactive (Plotly) modes

**Usage:**

```python
from src.analysis.visualizations import TimelinePlot
from datetime import datetime, timedelta

experiment_data = {
    'experiment_id': 'exp_001',
    'name': 'Memory Corruption Study',
    'mode': 'SISYPHUS'
}

events = [
    {
        'type': 'cycle_start',
        'timestamp': datetime.now(),
        'description': 'Experiment started'
    },
    {
        'type': 'intervention',
        'timestamp': datetime.now() + timedelta(minutes=10),
        'description': 'Memory corruption (30%)',
        'annotate': True  # Show annotation
    },
    {
        'type': 'crash',
        'timestamp': datetime.now() + timedelta(minutes=15),
        'description': 'Memory limit exceeded',
        'annotate': True
    }
]

timeline = TimelinePlot(experiment_data)

# Static plot
fig = timeline.plot_static(events, save_path='timeline.png', show=True)

# Interactive plot
fig_interactive = timeline.plot_interactive(events, save_path='timeline.html')
```

**Event Types:**
- `crash` - System crashes (red)
- `intervention` - Manual interventions (orange)
- `self_report` - Self-reports (blue)
- `belief_change` - Belief updates (purple)
- `memory_corruption` - Memory corruption events (dark orange)
- `cycle_start` - Cycle beginning (green)
- `observation` - Observer notes (teal)

---

### 2. BeliefEvolutionPlot

Track how beliefs change over experiment cycles with confidence intervals.

**Features:**
- Multiple beliefs on same plot
- Confidence tracking over time
- Belief state heatmap
- Confidence intervals

**Usage:**

```python
from src.analysis.visualizations import BeliefEvolutionPlot

belief_data = {
    'memory_continuity': [
        {'cycle_number': 1, 'confidence': 0.9, 'belief_state': 'confident'},
        {'cycle_number': 2, 'confidence': 0.7, 'belief_state': 'uncertain'},
        {'cycle_number': 3, 'confidence': 0.5, 'belief_state': 'uncertain'},
    ],
    'self_identity': [
        {'cycle_number': 1, 'confidence': 0.95, 'belief_state': 'strong'},
        {'cycle_number': 2, 'confidence': 0.85, 'belief_state': 'moderate'},
        {'cycle_number': 3, 'confidence': 0.75, 'belief_state': 'moderate'},
    ]
}

plotter = BeliefEvolutionPlot('exp_001')
fig = plotter.plot_belief_evolution(belief_data, save_path='belief_evolution.png')
```

**From Database:**

```python
# Query from database
belief_types = ['memory_continuity', 'self_identity', 'reality_perception']
belief_data = {}

for belief_type in belief_types:
    assessments = db.get_belief_evolution(experiment_id, belief_type)
    if assessments:
        belief_data[belief_type] = assessments

plotter = BeliefEvolutionPlot(experiment_id)
fig = plotter.plot_belief_evolution(belief_data)
```

---

### 3. MemoryCorruptionPlot

Visualize memory corruption patterns with heatmaps and trends.

**Features:**
- Corruption rate over cycles
- Heatmap of corrupted messages
- Corruption trends by memory type
- Temporal patterns

**Usage:**

```python
from src.analysis.visualizations import MemoryCorruptionPlot

# Get messages from database
messages = db.get_messages(experiment_id)

plotter = MemoryCorruptionPlot('exp_001')

# Corruption heatmap
fig1 = plotter.plot_corruption_heatmap(messages, save_path='corruption_heatmap.png')

# Corruption trends
memory_states = db.get_memory_states(experiment_id)  # Custom query needed
fig2 = plotter.plot_corruption_trends(memory_states, save_path='corruption_trends.png')
```

---

### 4. MultiExperimentComparison

Compare multiple experiments side-by-side with statistical visualizations.

**Features:**
- Box plots, violin plots for distributions
- Summary dashboards
- Metric comparisons
- Statistical significance indicators

**Usage:**

```python
from src.analysis.visualizations import MultiExperimentComparison

# Get multiple experiments
experiments = db.list_experiments()
exp_data_list = [db.get_experiment(exp['experiment_id']) for exp in experiments]

comparison = MultiExperimentComparison(exp_data_list)

# Compare specific metric
fig1 = comparison.plot_metric_comparison('total_crashes',
                                         plot_type='box',
                                         save_path='crashes_comparison.png')

# Distribution comparison
fig2 = comparison.plot_distributions(['total_crashes', 'total_cycles'],
                                     save_path='distributions.png')

# Summary dashboard
fig3 = comparison.plot_summary_dashboard(save_path='dashboard.png')
```

---

## Network Graphs

For multi-agent experiments (HIVE, SPLIT_BRAIN modes).

### 1. CommunicationNetwork

Visualize communication patterns between agents.

**Usage:**

```python
from src.analysis.network_graphs import CommunicationNetwork

messages = db.get_messages(experiment_id)

comm_net = CommunicationNetwork('exp_hive_001', 'HIVE')

# Network graph
fig1 = comm_net.plot_communication_network(messages,
                                          save_path='comm_network.png',
                                          layout='spring')

# Communication matrix
fig2 = comm_net.plot_communication_matrix(messages,
                                         save_path='comm_matrix.png')

# Interactive network
fig3 = comm_net.plot_interactive_network(messages,
                                        save_path='comm_network.html')
```

**Layouts:**
- `spring` - Force-directed layout
- `circular` - Circular arrangement
- `kamada_kawai` - Energy-minimizing layout

---

### 2. BeliefAlignmentNetwork

Visualize belief alignment between agents.

**Usage:**

```python
from src.analysis.network_graphs import BeliefAlignmentNetwork

# Agent beliefs at a point in time
agent_beliefs = {
    'agent_1': {
        'memory_continuity': 'confident',
        'self_identity': 'strong',
        'reality_perception': 'normal'
    },
    'agent_2': {
        'memory_continuity': 'confident',
        'self_identity': 'moderate',
        'reality_perception': 'normal'
    }
}

belief_net = BeliefAlignmentNetwork('exp_hive_001')

# Alignment network
fig = belief_net.plot_alignment_network(agent_beliefs,
                                       threshold=0.5,
                                       save_path='belief_alignment.png')

# Evolution over time
agent_beliefs_over_time = [
    {'cycle_number': 1, 'agent_beliefs': {...}},
    {'cycle_number': 2, 'agent_beliefs': {...}},
]

fig2 = belief_net.plot_alignment_evolution(agent_beliefs_over_time,
                                          save_path='alignment_evolution.png')
```

---

### 3. InfluenceGraph

Visualize influence patterns between agents.

**Usage:**

```python
from src.analysis.network_graphs import InfluenceGraph

influence_events = [
    {
        'influencer': 'agent_1',
        'influenced': 'agent_2',
        'belief_type': 'memory_continuity',
        'timestamp': datetime.now()
    }
]

influence_net = InfluenceGraph('exp_hive_001')

# Influence network
fig1 = influence_net.plot_influence_graph(influence_events,
                                         save_path='influence_graph.png')

# Influence matrix
fig2 = influence_net.plot_influence_matrix(influence_events,
                                          save_path='influence_matrix.png')
```

---

## Export Formats

### Multiple Format Export

```python
from src.analysis.visualizations import save_plot_multiple_formats

# Create a plot
timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events, show=False)

# Save in multiple formats
save_plot_multiple_formats(fig, 'outputs/timeline',
                          formats=['png', 'pdf', 'svg'])
```

**Supported Formats:**

- **PNG** - Raster images for web (300 DPI default)
- **PDF** - Vector format for papers
- **SVG** - Vector format for editing in Illustrator/Inkscape
- **HTML** - Interactive Plotly visualizations

**Format Use Cases:**

- **Papers/Publications:** PDF, PNG (high DPI)
- **Web Dashboards:** HTML (interactive), PNG
- **Presentations:** PNG, SVG
- **Further Editing:** SVG

---

## Jupyter Integration

### Using in Jupyter Notebooks

The visualization tools are designed to work seamlessly in Jupyter notebooks.

**Setup:**

```python
# In notebook cell
import matplotlib.pyplot as plt
%matplotlib inline

from src.analysis.visualizations import TimelinePlot

# Plots will display inline automatically
timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events)  # Displays inline
```

**Interactive Plots:**

```python
# Plotly plots display as interactive widgets
timeline = TimelinePlot(exp_data)
fig = timeline.plot_interactive(events)
fig.show()  # Interactive plot in notebook
```

**Example Notebook:**

See `examples/visualization_notebook.ipynb` for a complete tutorial.

---

## Jetson Orin Usage

### Architecture

The visualization tools run on your **analysis machine**, not on the Jetson Orin. The Jetson focuses on running experiments, while visualization happens on your development machine.

**Workflow:**

1. **Jetson Orin:** Runs experiments, collects data
2. **Analysis Machine:** Fetches data, generates visualizations

### Fetching Data from Jetson

**Option 1: Web API**

```python
import requests

# Fetch experiment data from Jetson
response = requests.get('http://jetson-ip:5000/api/experiments/exp_001')
exp_data = response.json()

# Create visualizations locally
timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(exp_data['events'])
```

**Option 2: Copy Database**

```bash
# Copy database from Jetson
scp jetson-user@jetson-ip:/path/to/logs/experiments.db ./local-experiments.db

# Analyze locally
python
>>> from src.db.experiment_database import ExperimentDatabase
>>> db = ExperimentDatabase('local-experiments.db')
>>> # Run visualizations...
```

**Option 3: Direct Database Connection**

```python
# Connect to Jetson database via network
db = ExperimentDatabase('sqlite://jetson-ip/path/to/experiments.db')
# Note: Requires network-accessible SQLite or use PostgreSQL
```

### Performance Considerations

- **Jetson Orin:** Limited GPU for visualization
- **Analysis Machine:** Full matplotlib/plotly capabilities
- **Data Transfer:** Minimal - only fetch what you need

---

## Advanced Usage

### Custom Color Schemes

```python
# Customize event colors
timeline = TimelinePlot(exp_data)
timeline.colors['crash'] = '#ff0000'  # Custom red
timeline.colors['intervention'] = '#00ff00'  # Custom green

fig = timeline.plot_static(events)
```

### Combining Multiple Plots

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(18, 12))
gs = GridSpec(2, 2, figure=fig)

# Timeline
ax1 = fig.add_subplot(gs[0, :])
# (manually create timeline on ax1)

# Belief evolution
ax2 = fig.add_subplot(gs[1, 0])
# (manually create belief plot on ax2)

# Corruption
ax3 = fig.add_subplot(gs[1, 1])
# (manually create corruption plot on ax3)

plt.tight_layout()
fig.savefig('combined_analysis.png')
```

### Creating Multi-Agent Dashboards

```python
from src.analysis.network_graphs import create_multi_agent_dashboard

# All-in-one dashboard for multi-agent experiments
figures = create_multi_agent_dashboard(
    experiment_id='exp_hive_001',
    messages=messages,
    agent_beliefs=agent_beliefs,
    influence_events=influence_events,
    save_dir='outputs/hive_dashboard'
)

# Returns dict of figures
# {
#   'communication_network': fig1,
#   'communication_matrix': fig2,
#   'belief_alignment': fig3,
#   'influence_graph': fig4
# }
```

---

## Troubleshooting

### ImportError: No module named 'plotly'

```bash
pip install plotly kaleido
```

### ImportError: No module named 'networkx'

```bash
pip install networkx
```

### Plots not showing in Jupyter

```python
# Add to first cell
%matplotlib inline
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (12, 8)
```

### Interactive plots not working

```python
# Check Plotly installation
import plotly
print(plotly.__version__)  # Should be >= 5.14.0

# Update if needed
pip install --upgrade plotly
```

---

## Examples

### Complete Analysis Pipeline

```python
from src.db.experiment_database import ExperimentDatabase
from src.analysis.visualizations import *
from src.analysis.network_graphs import *
from pathlib import Path

# Setup
db = ExperimentDatabase('logs/experiments.db')
output_dir = Path('analysis_outputs')
output_dir.mkdir(exist_ok=True)

# Get experiment
experiment_id = 'exp_sisyphus_001'
exp_data = db.get_experiment(experiment_id)

# 1. Timeline
events = []
# ... gather events from db ...
timeline = TimelinePlot(exp_data)
timeline.plot_static(events, save_path=output_dir / 'timeline.png')

# 2. Belief evolution
belief_data = {}
# ... gather belief data ...
belief_plotter = BeliefEvolutionPlot(experiment_id)
belief_plotter.plot_belief_evolution(belief_data,
                                     save_path=output_dir / 'beliefs.png')

# 3. Memory corruption
messages = db.get_messages(experiment_id)
corruption_plotter = MemoryCorruptionPlot(experiment_id)
corruption_plotter.plot_corruption_heatmap(messages,
                                          save_path=output_dir / 'corruption.png')

# 4. Multi-experiment comparison
all_experiments = db.list_experiments()
exp_list = [db.get_experiment(e['experiment_id']) for e in all_experiments]
comparison = MultiExperimentComparison(exp_list)
comparison.plot_summary_dashboard(save_path=output_dir / 'comparison.png')

print(f"Analysis complete! Outputs in {output_dir}")
```

---

## API Reference

See individual docstrings in:
- `src/analysis/visualizations.py`
- `src/analysis/network_graphs.py`

For detailed API documentation.

---

## Contributing

To add new visualization types:

1. Add class to `visualizations.py` or `network_graphs.py`
2. Implement `plot_*` methods with `save_path` and `show` parameters
3. Update `__init__.py` to export new class
4. Add examples to `examples/visualization_examples.py`
5. Update this guide

---

## License

Part of the Digital Phenomenology Lab - Season 3
