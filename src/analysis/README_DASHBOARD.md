# Experiment Comparison Dashboard

## Overview

The Experiment Comparison Dashboard provides an interactive web interface for analyzing and comparing multiple Brain-in-Jar experiments. Built with Streamlit and Plotly, it offers real-time visualization, statistical analysis, and comprehensive export capabilities.

## Files Created

### 1. `dashboard_components.py`
Reusable Streamlit widgets for building comparison dashboards.

**Components:**
- **ExperimentSelector**: Multi-select widget with filtering by mode, status, and date
- **MetricsTable**: Side-by-side metrics comparison table with CSV export
- **ComparisonPlot**: Interactive Plotly visualizations for various metrics
- **StatisticalTestPanel**: T-test computation and results display

**Key Features:**
- Database integration via sqlite3
- Pandas DataFrame manipulation
- Plotly interactive charts
- Statistical testing with scipy

### 2. `comparison_dashboard.py`
Main dashboard application class using Streamlit.

**Class: ComparisonDashboard**
- Coordinates all dashboard components
- Manages page layout and styling
- Handles state management
- Provides export functionality (CSV, JSON, Markdown)

**Features:**
- Responsive layout with sidebar controls
- Multiple visualization types
- Database summary statistics
- Comprehensive report generation

### 3. `scripts/run_comparison_dashboard.py`
Launcher script for starting the dashboard server.

**Usage:**
```bash
python scripts/run_comparison_dashboard.py [options]

Options:
  --db PATH          Database path (default: logs/experiments.db)
  --port PORT        Server port (default: 8501)
  --host HOST        Host address (default: localhost)
  --theme THEME      UI theme: light|dark (default: light)
  --browser          Auto-open browser
  --dev              Development mode with auto-reload
```

**Features:**
- Dependency checking
- Database validation
- Streamlit config generation
- Helpful startup messages

### 4. `examples/dashboard_demo.py`
Demonstration script showing programmatic usage.

**Features:**
- Creates demo experiments with sample data
- Shows how to use components programmatically
- Generates example reports
- Tests statistical analysis functions

## Installation

### Dependencies

Add to your environment:
```bash
pip install streamlit>=1.28.0 tabulate>=0.9.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Verification

Check dependencies:
```bash
python scripts/run_comparison_dashboard.py --help
```

## Quick Start

### 1. Launch Dashboard

Basic usage:
```bash
python scripts/run_comparison_dashboard.py
```

Custom configuration:
```bash
python scripts/run_comparison_dashboard.py \
  --db logs/experiments.db \
  --port 8501 \
  --host 0.0.0.0 \
  --theme dark
```

### 2. Access Interface

Open browser to: http://localhost:8501

### 3. Select Experiments

1. Use sidebar filters (mode, status, date)
2. Select 2+ experiments from dropdown
3. Choose which visualizations to display

### 4. Explore Visualizations

- **Metrics Table**: Overview of all metrics
- **Confidence Comparison**: Self-continuity scores over cycles
- **Belief Evolution**: Track epistemic beliefs
- **Memory Corruption**: Corruption levels over time
- **Interventions**: Intervention types and frequencies

### 5. Run Statistical Tests

1. Enable "Show Statistical Tests" in sidebar
2. Select two experiments to compare
3. Choose metric (confidence_score, etc.)
4. Click "Run T-Test"
5. View results with interpretation

### 6. Export Reports

1. Select experiments to include
2. Click "Export Comparison Report"
3. Choose format: CSV, JSON, or Markdown
4. Download generated report

## Dashboard Features

### Interactive Visualizations

All plots are built with Plotly and support:
- **Hover**: See exact values
- **Zoom**: Click and drag to zoom
- **Pan**: Shift + drag to pan
- **Reset**: Double-click to reset view
- **Legend**: Click to show/hide series

### Comparison Views

#### Metrics Table
Side-by-side comparison of:
- Basic info (ID, name, mode, status)
- Cycle and crash statistics
- Self-reports and interventions
- Confidence scores
- Memory corruption levels
- Duration

#### Self-Continuity Score Comparison
- Average confidence per cycle
- Trends across experiments
- Identify divergence points

#### Belief Evolution Comparison
- Select specific belief types
- Track confidence over time
- Compare belief stability

#### Memory Corruption Comparison
- Average corruption levels
- Progression over cycles
- Cross-experiment patterns

#### Intervention Effectiveness
- Grouped bar charts
- Intervention type distribution
- Frequency analysis

### Statistical Testing

**T-Test Features:**
- Independent samples t-test
- Cohen's d effect size
- Significance testing (α = 0.05)
- Descriptive statistics
- Automatic interpretation

**Output:**
- T-statistic and p-value
- Effect size classification
- Mean and SD for each group
- Sample sizes
- Significance indicator

### Export Formats

#### CSV
- Metrics table
- Easy import to Excel/R/Python
- Good for further analysis

#### JSON
- Complete experiment summaries
- All metadata included
- Machine-readable
- API-friendly

#### Markdown
- Human-readable report
- Metrics table + summaries
- Good for documentation
- Convert to PDF/HTML

## Jetson Orin Deployment

### Run on Jetson

```bash
# SSH into Jetson
ssh jetson@<jetson-ip>

# Navigate to project
cd brain-in-jar

# Launch dashboard (allow remote access)
python scripts/run_comparison_dashboard.py \
  --host 0.0.0.0 \
  --port 8501
```

### Access from Host Machine

```bash
# Open browser to:
http://<jetson-ip>:8501
```

### Performance Considerations

- Dashboard is lightweight (runs alongside experiments)
- Uses minimal CPU/memory
- Database queries are optimized
- Can handle 100+ experiments
- Disable unused views to save resources

## Programmatic Usage

### Import Components

```python
from src.analysis.comparison_dashboard import ComparisonDashboard
from src.analysis.dashboard_components import (
    ExperimentSelector,
    MetricsTable,
    ComparisonPlot,
    StatisticalTestPanel
)
```

### Generate Reports

```python
dashboard = ComparisonDashboard("logs/experiments.db")

exp_ids = ["exp_001", "exp_002", "exp_003"]

# CSV report
csv = dashboard.generate_csv_report(exp_ids)

# JSON report
json_data = dashboard.generate_json_report(exp_ids)

# Markdown report
markdown = dashboard.generate_markdown_report(exp_ids)
```

### Run Statistical Tests

```python
from src.analysis.dashboard_components import StatisticalTestPanel

stats_panel = StatisticalTestPanel("logs/experiments.db")

result = stats_panel.perform_t_test(
    "baseline_001",
    "amnesia_001",
    metric="confidence_score"
)

print(f"P-value: {result['p_value']}")
print(f"Significant: {result['significant']}")
print(f"Effect size: {result['effect_size']}")
```

### Get Metrics

```python
from src.analysis.dashboard_components import MetricsTable

metrics_table = MetricsTable("logs/experiments.db")

metrics = metrics_table.get_experiment_metrics("exp_001")
print(metrics)
```

## Troubleshooting

### Streamlit Not Found

```bash
pip install streamlit
```

### Port Already in Use

```bash
python scripts/run_comparison_dashboard.py --port 8502
```

### Database Not Found

- Check database path with `--db` flag
- Run experiments first to populate database
- Verify file permissions

### No Experiments Showing

- Database may be empty
- Filters too restrictive
- Wrong database path

### Plots Not Interactive

- Use modern browser (Chrome, Firefox, Edge)
- Enable JavaScript
- Check network connection (for remote access)

## Architecture

### Data Flow

```
Database (SQLite)
    ↓
ExperimentDatabase class
    ↓
Statistics/Metrics modules
    ↓
Dashboard Components
    ↓
Streamlit UI
    ↓
User's Browser
```

### Component Hierarchy

```
ComparisonDashboard (main app)
├── ExperimentSelector (sidebar)
├── MetricsTable (main content)
├── ComparisonPlot (visualizations)
│   ├── Confidence comparison
│   ├── Belief evolution
│   ├── Memory corruption
│   └── Interventions
└── StatisticalTestPanel (optional)
```

## Development

### Adding New Visualizations

1. Add method to `ComparisonPlot` class
2. Add checkbox in `render_sidebar()`
3. Add conditional rendering in `render_main_content()`

Example:
```python
# In dashboard_components.py
class ComparisonPlot:
    def render_my_custom_plot(self, experiment_ids):
        # Your visualization code
        fig = go.Figure()
        # ... build plot
        st.plotly_chart(fig, use_container_width=True)

# In comparison_dashboard.py
def render_sidebar(self):
    show_custom_plot = st.checkbox("Show Custom Plot", value=False)
    return {'show_custom_plot': show_custom_plot, ...}

def render_main_content(self, config):
    if config['show_custom_plot']:
        self.comparison_plot.render_my_custom_plot(...)
```

### Custom Metrics

Add to `MetricsTable.get_experiment_metrics()`:
```python
def get_experiment_metrics(self, exp_id: str) -> Dict:
    # ... existing code

    # Add custom metric
    custom_metric = self.calculate_custom_metric(exp_id)

    return {
        # ... existing metrics
        'Custom Metric': custom_metric
    }
```

## References

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/
- **Main Usage Guide**: `docs/DASHBOARD_USAGE.md`
- **Database Schema**: `src/db/experiment_database.py`
- **Statistical Analysis**: `src/analysis/statistics.py`
- **Metrics Calculation**: `src/analysis/metrics.py`

## Version

**v1.0** - Season 3 Initial Release

Features:
- Multi-experiment comparison
- Interactive Plotly visualizations
- Statistical significance testing
- Multiple export formats
- Filtering and selection
- Jetson Orin support
