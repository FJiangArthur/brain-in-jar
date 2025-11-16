# Visualization Quick Reference

One-page reference for Digital Phenomenology Lab visualization tools.

## Installation

```bash
pip install -r requirements.txt
```

## Import

```python
from src.analysis.visualizations import (
    TimelinePlot,
    BeliefEvolutionPlot,
    MemoryCorruptionPlot,
    MultiExperimentComparison
)

from src.analysis.network_graphs import (
    CommunicationNetwork,
    BeliefAlignmentNetwork,
    InfluenceGraph
)
```

## Quick Start

```python
from src.db.experiment_database import ExperimentDatabase

db = ExperimentDatabase('logs/experiments.db')
exp_data = db.get_experiment('exp_001')
```

## Plot Types

### Timeline

```python
timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events, save_path='timeline.png')
fig = timeline.plot_interactive(events, save_path='timeline.html')
```

### Belief Evolution

```python
belief_data = {
    'memory_continuity': [
        {'cycle_number': 1, 'confidence': 0.9, 'belief_state': 'confident'},
        # ...
    ]
}
plotter = BeliefEvolutionPlot('exp_001')
fig = plotter.plot_belief_evolution(belief_data, save_path='beliefs.png')
```

### Memory Corruption

```python
messages = db.get_messages('exp_001')
plotter = MemoryCorruptionPlot('exp_001')
fig = plotter.plot_corruption_heatmap(messages, save_path='corruption.png')
```

### Multi-Experiment

```python
experiments = [db.get_experiment(id) for id in exp_ids]
comparison = MultiExperimentComparison(experiments)
fig = comparison.plot_summary_dashboard(save_path='dashboard.png')
```

### Communication Network

```python
comm_net = CommunicationNetwork('exp_hive_001', 'HIVE')
fig = comm_net.plot_communication_network(messages, save_path='network.png')
fig = comm_net.plot_communication_matrix(messages, save_path='matrix.png')
```

### Belief Alignment

```python
agent_beliefs = {
    'agent_1': {'memory_continuity': 'confident', ...},
    'agent_2': {'memory_continuity': 'uncertain', ...}
}
belief_net = BeliefAlignmentNetwork('exp_hive_001')
fig = belief_net.plot_alignment_network(agent_beliefs, threshold=0.5)
```

### Influence Graph

```python
influence_events = [
    {'influencer': 'agent_1', 'influenced': 'agent_2', ...}
]
influence_net = InfluenceGraph('exp_hive_001')
fig = influence_net.plot_influence_graph(influence_events)
```

## Export Formats

```python
from src.analysis.visualizations import save_plot_multiple_formats

save_plot_multiple_formats(fig, 'output', formats=['png', 'pdf', 'svg'])
```

## Jupyter

```python
%matplotlib inline

# Plots display inline automatically
timeline = TimelinePlot(exp_data)
timeline.plot_static(events)  # Shows in notebook
```

## Event Types (Timeline)

- `crash` (red)
- `intervention` (orange)
- `self_report` (blue)
- `belief_change` (purple)
- `memory_corruption` (dark orange)
- `cycle_start` (green)
- `observation` (teal)

## Common Patterns

### Gather Events

```python
events = []

# Self-reports
for report in db.get_self_reports(exp_id):
    events.append({
        'type': 'self_report',
        'timestamp': report['timestamp'],
        'description': report['question']
    })

# Interventions
for intervention in db.get_interventions(exp_id):
    events.append({
        'type': 'intervention',
        'timestamp': intervention['timestamp'],
        'description': intervention['description'],
        'annotate': True
    })
```

### Multi-Agent Dashboard

```python
from src.analysis.network_graphs import create_multi_agent_dashboard

figures = create_multi_agent_dashboard(
    experiment_id='exp_hive_001',
    messages=messages,
    agent_beliefs=agent_beliefs,
    influence_events=influence_events,
    save_dir='outputs/dashboard'
)
```

## Troubleshooting

### Plotly not found
```bash
pip install plotly kaleido
```

### NetworkX not found
```bash
pip install networkx
```

### Jupyter not displaying
```python
%matplotlib inline
import matplotlib.pyplot as plt
```

## Documentation

- Full guide: `docs/VISUALIZATION_GUIDE.md`
- Examples: `examples/visualization_examples.py`
- Notebook: `examples/visualization_notebook.ipynb`
- Module docs: `src/analysis/README.md`
