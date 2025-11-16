# Experiment Comparison Dashboard - Usage Guide

## Overview

The Experiment Comparison Dashboard is an interactive web-based interface for analyzing and comparing multiple Brain-in-Jar experiments. Built with Streamlit and Plotly, it provides real-time visualization, statistical analysis, and export capabilities.

## Quick Start

### 1. Installation

First, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `streamlit>=1.28.0` - Dashboard framework
- `plotly>=5.14.0` - Interactive visualizations
- `pandas>=2.0.0` - Data manipulation
- `scipy>=1.10.0` - Statistical tests

### 2. Launch the Dashboard

Basic launch (local access only):
```bash
python scripts/run_comparison_dashboard.py
```

Custom database path:
```bash
python scripts/run_comparison_dashboard.py --db logs/experiments.db
```

Allow remote access (useful for Jetson Orin):
```bash
python scripts/run_comparison_dashboard.py --host 0.0.0.0 --port 8501
```

Custom port:
```bash
python scripts/run_comparison_dashboard.py --port 8502
```

Dark theme:
```bash
python scripts/run_comparison_dashboard.py --theme dark
```

### 3. Access the Dashboard

Once launched, open your browser to:
- **Local:** http://localhost:8501
- **Remote:** http://<jetson-ip>:8501

## Dashboard Features

### 1. Experiment Selection

**Location:** Left sidebar

**Features:**
- Filter by experiment mode (baseline, amnesia, paranoia, etc.)
- Filter by status (running, completed, failed)
- Filter by date range (Last 24h, Last Week, Last Month)
- Multi-select experiments for comparison

**Usage:**
1. Apply filters to narrow down experiments
2. Select 2 or more experiments from the dropdown
3. Selected experiments appear in all comparison views

### 2. Metrics Comparison Table

**View:** Side-by-side metrics comparison

**Metrics Displayed:**
- Experiment ID and name
- Mode and status
- Total cycles and crashes
- Crash rate (%)
- Self-reports count
- Interventions count
- Epistemic assessments count
- Average confidence score
- Memory corruption stats
- Duration

**Actions:**
- Scroll to view all metrics
- Download as CSV for offline analysis

### 3. Interactive Visualizations

#### Self-Continuity Score Comparison

**What it shows:**
- Average confidence scores over experiment cycles
- Trends in identity continuity
- Comparison across experiments

**Interactions:**
- Hover over points for exact values
- Click and drag to zoom
- Double-click to reset view
- Click legend items to show/hide experiments

#### Belief Evolution Comparison

**What it shows:**
- Evolution of epistemic beliefs over time
- Confidence levels for different belief types
- Cross-experiment belief patterns

**Features:**
- Dropdown to select specific belief type
- Shows all experiments for that belief
- Track belief stability/changes

#### Memory Corruption Comparison

**What it shows:**
- Memory corruption levels over cycles
- Average corruption across memory types
- Impact of corruption on behavior

**Use cases:**
- Compare amnesia experiments
- Track corruption progression
- Identify corruption thresholds

#### Intervention Effectiveness

**What it shows:**
- Types and frequencies of interventions
- Grouped bar chart by experiment
- Intervention distribution

**Use cases:**
- Compare intervention strategies
- Assess intervention frequency
- Identify successful interventions

### 4. Statistical Testing

**Location:** Optional panel (enable in sidebar)

**Features:**
- Independent samples t-test
- Cohen's d effect size
- Statistical significance (α = 0.05)
- Descriptive statistics

**How to use:**
1. Enable "Show Statistical Tests" in sidebar
2. Select two experiments to compare
3. Choose metric (e.g., confidence_score)
4. Click "Run T-Test"
5. View results and interpretation

**Output:**
- T-statistic and p-value
- Effect size (negligible, small, medium, large)
- Mean and standard deviation for each experiment
- Automatic interpretation of significance

### 5. Export Comparison Reports

**Location:** Sidebar under "Export Options"

**Available Formats:**

#### CSV Export
- Metrics table as CSV
- Easy to import into Excel/R/Python
- Good for statistical analysis

#### JSON Export
- Complete experiment data
- Includes all metadata
- Machine-readable format
- Good for programmatic access

#### Markdown Export
- Human-readable report
- Metrics table + detailed summaries
- Good for documentation
- Can be converted to PDF/HTML

**How to export:**
1. Select experiments to include
2. Click "Export Comparison Report"
3. Choose format (CSV/JSON/Markdown)
4. Click "Generate Report"
5. Download the file

## Use Cases

### 1. Comparing Baseline vs Intervention

**Goal:** Assess if memory corruption affects self-continuity

**Steps:**
1. Select one baseline experiment
2. Select one amnesia experiment
3. View confidence comparison plot
4. Run statistical test on confidence scores
5. Export report with findings

**What to look for:**
- Lower confidence in amnesia experiments
- Increased variance in corrupted memory
- Statistically significant difference

### 2. Evaluating Intervention Effectiveness

**Goal:** Determine which interventions are most effective

**Steps:**
1. Select multiple experiments with different intervention types
2. View intervention effectiveness chart
3. Compare intervention frequencies
4. Check belief evolution for each experiment
5. Export CSV for further analysis

**What to look for:**
- Which interventions are used most
- Correlation between interventions and outcomes
- Belief changes after interventions

### 3. Tracking Paranoia Development

**Goal:** Analyze how surveillance awareness develops

**Steps:**
1. Select panopticon experiments
2. Filter belief evolution for "surveillance_paranoia"
3. View confidence trends over cycles
4. Compare to control experiments
5. Export markdown report

**What to look for:**
- Rising paranoia over cycles
- Plateau or continued increase
- Difference from non-surveillance experiments

### 4. Season-Long Analysis

**Goal:** Compare all experiments from a research season

**Steps:**
1. Filter by date range (e.g., "Last Month")
2. View database overview for summary stats
3. Select representative experiments from each mode
4. Generate comprehensive comparison
5. Export JSON for archival

**What to look for:**
- Distribution across experiment modes
- Overall success/completion rates
- Common patterns across modes

## Tips and Best Practices

### Performance Optimization

1. **Limit selections:** Comparing 2-5 experiments is optimal
2. **Use filters:** Narrow down before selecting
3. **Disable unused views:** Uncheck views you don't need
4. **Close when done:** Dashboard uses system resources

### Jetson Orin Deployment

**Running dashboard on Jetson:**
```bash
# On Jetson Orin
python scripts/run_comparison_dashboard.py --host 0.0.0.0 --port 8501
```

**Accessing from another machine:**
```bash
# On your laptop
# Open browser to: http://<jetson-ip>:8501
```

**Lightweight mode:**
- Disable unnecessary visualizations
- Use CSV exports for heavy analysis
- Run dashboard only when needed

### Data Interpretation

**Confidence scores:**
- 0.0-0.3: Low/no continuity
- 0.3-0.6: Moderate continuity
- 0.6-1.0: High continuity

**Statistical significance:**
- p < 0.05: Significant difference
- p >= 0.05: No significant difference
- Always consider effect size!

**Effect sizes (Cohen's d):**
- < 0.2: Negligible
- 0.2-0.5: Small
- 0.5-0.8: Medium
- > 0.8: Large

## Troubleshooting

### Dashboard won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`
**Solution:**
```bash
pip install streamlit plotly
```

### Database not found

**Error:** `Database not found at: logs/experiments.db`
**Solution:**
- Check database path is correct
- Run an experiment first to create database
- Use `--db` flag to specify correct path

### No experiments showing

**Possible causes:**
- Database is empty (run experiments first)
- Filters are too restrictive (reset filters)
- Wrong database path

### Plots not interactive

**Possible causes:**
- Browser JavaScript disabled
- Outdated browser
- Network issues (for remote access)

**Solution:** Use a modern browser (Chrome, Firefox, Edge)

### Port already in use

**Error:** `Address already in use`
**Solution:** Use a different port:
```bash
python scripts/run_comparison_dashboard.py --port 8502
```

## Advanced Usage

### Programmatic Access

You can also use the dashboard components programmatically:

```python
from src.analysis.comparison_dashboard import ComparisonDashboard
from src.analysis.dashboard_components import MetricsTable, ComparisonPlot

# Initialize
dashboard = ComparisonDashboard("logs/experiments.db")
metrics_table = MetricsTable("logs/experiments.db")

# Get metrics for experiments
exp_ids = ["exp_001", "exp_002"]
metrics = [metrics_table.get_experiment_metrics(eid) for eid in exp_ids]

# Generate report programmatically
csv_report = dashboard.generate_csv_report(exp_ids)
json_report = dashboard.generate_json_report(exp_ids)
md_report = dashboard.generate_markdown_report(exp_ids)
```

### Custom Visualizations

Extend the dashboard with custom plots:

```python
from src.analysis.dashboard_components import ComparisonPlot

class CustomPlot(ComparisonPlot):
    def render_custom_metric(self, experiment_ids):
        # Your custom visualization code
        pass
```

### Batch Export

Export all experiments:

```bash
python -c "
from src.analysis.comparison_dashboard import ComparisonDashboard
from src.db.experiment_database import ExperimentDatabase

db = ExperimentDatabase('logs/experiments.db')
dashboard = ComparisonDashboard('logs/experiments.db')

# Get all completed experiments
exps = db.list_experiments(status='completed')
exp_ids = [e['experiment_id'] for e in exps]

# Export
report = dashboard.generate_json_report(exp_ids)
with open('all_experiments_report.json', 'w') as f:
    f.write(report)
"
```

## API Reference

See the following files for detailed API documentation:

- `src/analysis/comparison_dashboard.py` - Main dashboard class
- `src/analysis/dashboard_components.py` - Reusable widgets
- `src/analysis/statistics.py` - Statistical analysis
- `src/analysis/metrics.py` - Metrics calculation

## Support

For issues or questions:
1. Check this documentation
2. Review code comments in source files
3. Check the main project README
4. Review experiment database schema

## Version History

**v1.0 (Season 3)**
- Initial release
- Multi-experiment comparison
- Interactive Plotly visualizations
- Statistical testing
- Export to CSV/JSON/Markdown
- Jetson Orin support
