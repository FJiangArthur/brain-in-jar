# Visualization Tools - Agent D2 Implementation

## Quick Overview

Comprehensive visualization tools for Digital Phenomenology Lab experiments.

**Status:** ✅ Complete
**Lines of Code:** 1,678
**Classes:** 7 plot types
**Documentation:** 4 guides
**Examples:** 2 (Python + Jupyter)

---

## What's Included

### 📊 Core Modules

1. **`src/analysis/visualizations.py`** (832 lines)
   - `TimelinePlot` - Event visualization
   - `BeliefEvolutionPlot` - Epistemic tracking
   - `MemoryCorruptionPlot` - Corruption analysis
   - `MultiExperimentComparison` - Comparative analysis

2. **`src/analysis/network_graphs.py`** (846 lines)
   - `CommunicationNetwork` - Agent communication
   - `BeliefAlignmentNetwork` - Belief similarity
   - `InfluenceGraph` - Influence patterns

### 📚 Documentation

- **`docs/VISUALIZATION_GUIDE.md`** - Complete user guide (500+ lines)
- **`docs/VISUALIZATION_QUICK_REF.md`** - One-page reference
- **`src/analysis/README.md`** - Module overview
- **`VISUALIZATION_IMPLEMENTATION.md`** - Implementation details

### 💻 Examples

- **`examples/visualization_examples.py`** - 7 Python examples
- **`examples/visualization_notebook.ipynb`** - Jupyter tutorial

---

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from src.db.experiment_database import ExperimentDatabase
from src.analysis.visualizations import TimelinePlot

# Connect to database
db = ExperimentDatabase('logs/experiments.db')
exp_data = db.get_experiment('exp_001')

# Create timeline
events = []  # Gather from db.get_self_reports(), etc.
timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events, save_path='timeline.png')
```

### Run Examples

```bash
python examples/visualization_examples.py
```

### Open Jupyter Tutorial

```bash
jupyter notebook examples/visualization_notebook.ipynb
```

---

## Plot Types

### 1. Timeline
```python
from src.analysis.visualizations import TimelinePlot

timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events, save_path='timeline.png')
```

### 2. Belief Evolution
```python
from src.analysis.visualizations import BeliefEvolutionPlot

plotter = BeliefEvolutionPlot('exp_001')
fig = plotter.plot_belief_evolution(belief_data)
```

### 3. Memory Corruption
```python
from src.analysis.visualizations import MemoryCorruptionPlot

plotter = MemoryCorruptionPlot('exp_001')
fig = plotter.plot_corruption_heatmap(messages)
```

### 4. Multi-Experiment Comparison
```python
from src.analysis.visualizations import MultiExperimentComparison

comparison = MultiExperimentComparison(experiments)
fig = comparison.plot_summary_dashboard()
```

### 5. Communication Network
```python
from src.analysis.network_graphs import CommunicationNetwork

comm_net = CommunicationNetwork('exp_hive_001', 'HIVE')
fig = comm_net.plot_communication_network(messages)
```

### 6. Belief Alignment
```python
from src.analysis.network_graphs import BeliefAlignmentNetwork

belief_net = BeliefAlignmentNetwork('exp_hive_001')
fig = belief_net.plot_alignment_network(agent_beliefs)
```

### 7. Influence Graph
```python
from src.analysis.network_graphs import InfluenceGraph

influence_net = InfluenceGraph('exp_hive_001')
fig = influence_net.plot_influence_graph(influence_events)
```

---

## Export Formats

All plots support:
- **PNG** - High-resolution (300 DPI)
- **PDF** - Vector format for papers
- **SVG** - Vector format for editing
- **HTML** - Interactive Plotly

```python
from src.analysis.visualizations import save_plot_multiple_formats

save_plot_multiple_formats(fig, 'output', formats=['png', 'pdf', 'svg'])
```

---

## Jupyter Integration

```python
%matplotlib inline

from src.analysis.visualizations import TimelinePlot

timeline = TimelinePlot(exp_data)
timeline.plot_static(events)  # Displays inline automatically
```

---

## Jetson Orin Usage

Visualizations run on your **analysis machine**, not Jetson.

**Fetch data from Jetson:**

```bash
# Option 1: Copy database
scp jetson:/path/to/experiments.db ./local.db

# Option 2: Use web API
curl http://jetson-ip:5000/api/experiments/exp_001
```

---

## Dependencies

### Required
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- pandas >= 2.0.0
- numpy >= 1.24.0

### Optional (for enhanced features)
- plotly >= 5.14.0 (interactive plots)
- networkx >= 3.0 (network graphs)
- jupyter >= 1.0.0 (notebooks)

---

## Documentation

For detailed information:

- **Complete Guide:** `docs/VISUALIZATION_GUIDE.md`
- **Quick Reference:** `docs/VISUALIZATION_QUICK_REF.md`
- **Module Docs:** `src/analysis/README.md`
- **Implementation:** `VISUALIZATION_IMPLEMENTATION.md`

---

## File Structure

```
src/analysis/
├── visualizations.py      (832 lines) - Core plotting
├── network_graphs.py      (846 lines) - Network graphs
└── README.md

docs/
├── VISUALIZATION_GUIDE.md        - Complete guide
└── VISUALIZATION_QUICK_REF.md    - Quick reference

examples/
├── visualization_examples.py     - Python examples
└── visualization_notebook.ipynb  - Jupyter tutorial

VISUALIZATION_IMPLEMENTATION.md   - Implementation summary
README_VISUALIZATION.md           - This file
```

---

## Features

✅ Timeline event visualization
✅ Belief evolution tracking
✅ Memory corruption analysis
✅ Multi-experiment comparisons
✅ Network graphs (multi-agent)
✅ Communication patterns
✅ Belief alignment networks
✅ Influence graphs
✅ Multiple export formats
✅ Jupyter integration
✅ Jetson Orin compatible
✅ Interactive visualizations
✅ Comprehensive documentation

---

## Integration

### With Database
```python
db = ExperimentDatabase('logs/experiments.db')
exp_data = db.get_experiment('exp_001')
```

### With Analysis (Agent D1)
```python
from src.analysis import (
    ExperimentStatistics,      # D1
    TimelinePlot               # D2
)
```

### With Web Interface
```python
@app.route('/api/viz/<exp_id>')
def viz(exp_id):
    timeline = TimelinePlot(exp_data)
    return timeline.plot_interactive(events).to_html()
```

---

## Support

- **Issues:** Check `docs/VISUALIZATION_GUIDE.md` troubleshooting section
- **Examples:** Run `python examples/visualization_examples.py`
- **Tutorial:** Open `examples/visualization_notebook.ipynb`

---

**Agent D2 - Visualization Tools Complete** ✅
