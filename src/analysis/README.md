# Analysis Module

Comprehensive data analysis and visualization tools for Digital Phenomenology Lab experiments.

## Components

### Core Analysis (Agent D1)
- `statistics.py` - Statistical analysis tools
- `metrics.py` - Metrics calculation
- `export.py` - Data export utilities
- `report_generator.py` - Automated report generation

### Visualization Tools (Agent D2)
- `visualizations.py` - Core plotting classes
- `network_graphs.py` - Multi-agent network visualizations

## Quick Start

```python
from src.analysis.visualizations import TimelinePlot
from src.db.experiment_database import ExperimentDatabase

db = ExperimentDatabase('logs/experiments.db')
exp_data = db.get_experiment('exp_001')

timeline = TimelinePlot(exp_data)
fig = timeline.plot_static(events, save_path='timeline.png')
```

## Documentation

- Full guide: `docs/VISUALIZATION_GUIDE.md`
- Examples: `examples/visualization_examples.py`
- Notebook: `examples/visualization_notebook.ipynb`

## Dependencies

```bash
pip install -r requirements.txt
```

See requirements.txt for visualization dependencies.
