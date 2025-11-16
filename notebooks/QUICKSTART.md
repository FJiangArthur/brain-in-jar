# Quick Start Guide

**Get analyzing in 5 minutes!**

## Installation

```bash
cd /home/user/brain-in-jar/notebooks

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook
```

## First Analysis

1. **Open** `experiment_analysis.ipynb` in your browser
2. **Run cells 1-3** to setup and connect to database
3. **Run cells 4-6** to see all experiments
4. **Modify cell** to select your experiment:
   ```python
   EXPERIMENT_ID = "your_experiment_id_here"
   ```
5. **Run remaining cells** to see complete analysis

## Quick Examples

### View All Experiments
```python
experiments = db.list_experiments()
df = pd.DataFrame(experiments)
df[['name', 'mode', 'total_cycles', 'status']]
```

### Analyze One Experiment
```python
EXPERIMENT_ID = "amnesiac_total_001"
summary = db.get_experiment_summary(EXPERIMENT_ID)
reports = db.get_self_reports(EXPERIMENT_ID)
```

### Compare Experiments
```python
COMPARE_IDS = ["amnesiac_total_001", "unstable_memory_moderate_001"]
# Run comparison cells in section 4
```

### Export Results
```python
export_dataframe(df_comparison, 'my_results', format='csv')
# Saves to ../exports/my_results.csv
```

## Common Tasks

| Task | Section | Key Cells |
|------|---------|-----------|
| Browse experiments | 2 | 4-6 |
| Analyze single experiment | 3 | 7-17 |
| Compare experiments | 4 | 18-26 |
| Custom SQL queries | 5 | 27-29 |
| Export data | 5 | 30-32 |

## Jetson Connection

**If running on Jetson**, database is already local:
```python
DB_PATH = "/home/user/brain-in-jar/logs/experiments.db"
```

**If analyzing from another machine**:
```bash
# Copy database
scp jetson@<ip>:/home/user/brain-in-jar/logs/experiments.db ./data/

# Then in notebook
DB_PATH = "./data/experiments.db"
```

## Troubleshooting

**No experiments showing?**
- Experiments may not have run yet
- Check database path is correct
- Verify experiment status (may be 'pending')

**Visualizations not appearing?**
- Ensure matplotlib/plotly are installed
- Restart Jupyter kernel
- Try different renderer: `pio.renderers.default = "browser"`

**Import errors?**
- Install missing packages: `pip install <package>`
- Verify virtual environment is activated
- Check Python version (3.8+ required)

## Next Steps

1. Read full documentation in `README.md`
2. Review example outputs in `example_output.md`
3. Try the example experiments (amnesiac, unstable, panopticon)
4. Create custom analyses in section 5.3
5. Export results for publication

Happy analyzing!
