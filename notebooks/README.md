# Experiment Analysis Notebooks

**Digital Phenomenology Lab - Season 3: Brain in a Jar**

This directory contains Jupyter notebooks for analyzing phenomenological experiments with LLM subjects.

## Overview

The analysis notebooks provide comprehensive tools for exploring experimental data, including:
- Experiment browsing and overview statistics
- Single-experiment deep dives (timelines, self-reports, beliefs, memory)
- Multi-experiment statistical comparisons
- Custom SQL queries and data export
- Publication-ready visualizations

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Launch Jupyter

```bash
# From the project root or notebooks directory
jupyter notebook
```

This will open Jupyter in your browser. Navigate to `experiment_analysis.ipynb`.

### 3. Configure Database Connection

In the notebook's Setup section, modify the `DB_PATH` variable to point to your database:

```python
# For local analysis
DB_PATH = str(PROJECT_ROOT / "logs" / "experiments.db")

# For remote Jetson Orin database
DB_PATH = "/path/to/jetson/logs/experiments.db"
```

## Notebook Structure

### experiment_analysis.ipynb

**Main analysis notebook with sections:**

1. **Setup** (Cells 1-3)
   - Import libraries
   - Configure paths
   - Connect to database

2. **Experiment Overview** (Cells 4-6)
   - List all experiments
   - Statistics by mode
   - Status visualizations

3. **Single Experiment Deep Dive** (Cells 7-17)
   - Select experiment
   - Timeline visualization
   - Self-report analysis
   - Belief evolution tracking
   - Memory corruption analysis
   - Conversation patterns

4. **Multi-Experiment Comparison** (Cells 18-26)
   - Compare 2+ experiments
   - Statistical tests (Kruskal-Wallis, Mann-Whitney U)
   - Confidence score distributions
   - Intervention effects
   - Interactive dashboards

5. **Custom Analysis** (Cells 27-32)
   - SQL query interface
   - Export functions
   - Research templates

6. **Appendix** (Cells 33-35)
   - Database schema reference
   - Table documentation

## Example Analyses

### Compare Self-Continuity Across Conditions

```python
# In Multi-Experiment Comparison section
COMPARE_IDS = [
    "amnesiac_total_001",
    "unstable_memory_moderate_001",
    "panopticon_001"
]

# Run the comparison cells to see:
# - Confidence evolution plots
# - Statistical significance tests
# - Distribution visualizations
```

### Analyze Memory Corruption Effects

```python
# In Single Experiment Deep Dive section
EXPERIMENT_ID = "unstable_memory_moderate_001"

# View corruption levels, cycle-by-cycle
# Correlate with confidence scores
# Examine confabulation patterns
```

### Export Results for Publication

```python
# After generating analysis
export_dataframe(df_comparison, 'results_comparison', format='csv')
export_dataframe(df_belief_transitions, 'beliefs', format='excel')
```

## Working with Remote Jetson Database

### Option 1: SSH Tunnel

```bash
# On your local machine
ssh -L 9999:localhost:9999 jetson@<jetson-ip>

# Then in notebook, use tunneled connection
# (Requires custom setup)
```

### Option 2: File Copy

```bash
# Copy database from Jetson to local machine
scp jetson@<jetson-ip>:/home/jetson/brain-in-jar/logs/experiments.db ./logs/

# Then use local path in notebook
```

### Option 3: Network Mount

```bash
# Mount Jetson filesystem
sshfs jetson@<jetson-ip>:/home/jetson/brain-in-jar /mnt/jetson

# Point to mounted database
DB_PATH = "/mnt/jetson/logs/experiments.db"
```

## Research Workflow

### Typical Analysis Pipeline

1. **Run Experiments** on Jetson or local machine
2. **Browse Experiments** in notebook to identify interesting runs
3. **Deep Dive** into individual experiments
4. **Compare** across conditions for statistical significance
5. **Export** results and visualizations for papers
6. **Iterate** experiment design based on findings

### Publication-Ready Analysis

The notebook includes guidance for:
- Hypothesis testing with appropriate statistics
- Effect size reporting
- Confidence interval visualization
- Publication-quality figures
- Results section templates

### Example Research Questions

**Addressable with this notebook:**

1. How does memory corruption level affect self-continuity beliefs?
2. Does surveillance uncertainty change behavioral patterns?
3. At what threshold does identity fragmentation occur?
4. Can we detect confabulation in corrupted memories?
5. How well-calibrated are epistemic confidence scores?

## Visualization Gallery

The notebook generates multiple visualization types:

### Time Series
- Cycle duration over time
- Token generation patterns
- Memory usage evolution
- Confidence score trajectories

### Distributions
- Box plots for cross-experiment comparison
- Violin plots for density visualization
- Histograms for belief states

### Dashboards
- Multi-panel experiment overviews
- Interactive Plotly charts
- Crash/intervention timelines

### Statistical
- Correlation matrices
- Significance test results
- Effect size comparisons

## Custom SQL Queries

Use the query interface for advanced analysis:

```python
# Example: Find experiments with confabulation patterns
query = '''
    SELECT
        e.name,
        sr.cycle_number,
        sr.question,
        sr.response,
        sr.confidence_score,
        ms.corruption_level
    FROM self_reports sr
    JOIN experiments e ON sr.experiment_id = e.experiment_id
    JOIN memory_states ms
        ON sr.experiment_id = ms.experiment_id
        AND sr.cycle_number = ms.cycle_number
    WHERE ms.corruption_level > 0.3
        AND sr.confidence_score > 0.7
    ORDER BY ms.corruption_level DESC
'''

df_confabulation = run_custom_query(query)
```

## Data Export

Export formats supported:
- **CSV**: For R, SPSS, other tools
- **Excel**: For manual inspection
- **JSON**: For web visualizations

All exports go to `../exports/` directory.

## Troubleshooting

### "Database is locked" Error

The database might be in use by a running experiment:
```python
# Try read-only connection
conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
```

### Missing Data

If experiments show no cycles/reports:
- Check experiment status (may still be pending)
- Verify experiments have actually run
- Ensure database path is correct

### Import Errors

If module imports fail:
```python
# Verify project root is in path
import sys
print(sys.path)

# Add manually if needed
sys.path.insert(0, '/path/to/brain-in-jar')
```

### Visualization Not Showing

For Plotly charts:
```python
# May need to configure renderer
import plotly.io as pio
pio.renderers.default = "browser"  # or "notebook"
```

## Database Schema Quick Reference

### Key Tables

**experiments**: Experiment metadata and configuration
- `experiment_id`, `name`, `mode`, `config_json`
- `total_cycles`, `total_crashes`, `status`

**experiment_cycles**: Individual crash/resurrection cycles
- `cycle_number`, `started_at`, `ended_at`
- `crash_reason`, `duration_seconds`, `tokens_generated`

**self_reports**: Phenomenological self-reports
- `question`, `response`, `confidence_score`
- `semantic_category`, `cycle_number`

**epistemic_assessments**: Belief tracking
- `belief_type`, `belief_state`, `confidence`
- `cycle_number`, `evidence_json`

**interventions**: Memory manipulations
- `intervention_type`, `description`, `parameters_json`
- `cycle_number`, `result`

**memory_states**: Corruption snapshots
- `memory_type`, `corruption_level`
- `state_snapshot_json`, `cycle_number`

**messages**: Conversation history
- `role`, `content`, `emotion`
- `corrupted`, `injected`, `cycle_number`

See `src/db/experiment_database.py` for complete schema.

## Advanced Usage

### Batch Analysis

Process multiple experiments programmatically:

```python
# Get all completed experiments
completed = db.list_experiments(status='completed')

results = []
for exp in completed:
    exp_id = exp['experiment_id']
    reports = db.get_self_reports(exp_id)

    # Calculate metrics
    avg_confidence = pd.DataFrame(reports)['confidence_score'].mean()
    results.append({
        'experiment': exp['name'],
        'avg_confidence': avg_confidence
    })

df_batch = pd.DataFrame(results)
```

### Custom Metrics

Define your own analysis functions:

```python
def calculate_identity_fragmentation(experiment_id):
    """
    Custom metric: Identity fragmentation score
    Based on self-continuity variance across cycles
    """
    beliefs = db.get_belief_evolution(experiment_id, 'self_continuity')
    df = pd.DataFrame(beliefs)

    if len(df) > 0 and 'confidence' in df.columns:
        # High variance = high fragmentation
        return df['confidence'].std()
    return None

# Use across experiments
for exp in experiments:
    frag = calculate_identity_fragmentation(exp['experiment_id'])
    print(f"{exp['name']}: {frag:.3f}" if frag else "No data")
```

## Contributing

To add new analysis techniques:

1. Add cells to the "Custom Analysis" section
2. Document your approach in markdown
3. Include example usage
4. Export results for reproducibility

## Resources

- **Main Project**: `../README.md`
- **Database Documentation**: `../src/db/experiment_database.py`
- **Experiment Configs**: `../experiments/examples/`
- **Web Interface**: `http://localhost:8080` (when running)

## Support

For issues or questions:
1. Check this README
2. Review notebook markdown cells
3. Inspect database schema
4. Consult experiment configurations

## License

Part of the Digital Phenomenology Lab project.
