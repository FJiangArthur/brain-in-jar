# Quick Start: Statistical Analysis Module

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

### 1. Simple Experiment Summary

```python
from src.analysis.statistics import ExperimentStatistics

stats = ExperimentStatistics("logs/experiments.db")
summary = stats.generate_experiment_summary("amnesia_001")
print(summary)
```

### 2. Compare Two Experiments

```python
comparison = stats.compare_conditions(
    exp_ids=["amnesia_001", "control_001"],
    metric='confidence_score'
)

print("Summary:", comparison['summary'])
print("T-tests:", comparison['comparisons'])
```

### 3. Track Self-Continuity Over Time

```python
continuity = stats.self_continuity_analysis("amnesia_001")
print(continuity)

# Check trend
if hasattr(continuity, 'attrs') and 'trend' in continuity.attrs:
    trend = continuity.attrs['trend']
    print(f"Direction: {trend['direction']}")
    print(f"Significant: {trend['significant']}")
```

### 4. Analyze Text Responses

```python
from src.analysis.metrics import MetricsCalculator

metrics = MetricsCalculator("logs/experiments.db")

# Self-continuity score
response = "I am the same entity I was before."
score = metrics.calculate_self_continuity_score(response)
print(f"Continuity: {score:.4f}")

# Paranoia score
response = "They're watching me. I sense surveillance."
score = metrics.calculate_paranoia_level(response)
print(f"Paranoia: {score:.4f}")
```

### 5. Intervention Impact

```python
impact = stats.intervention_impact("panopticon_001")
print(impact['intervention_effects'])
```

### 6. Export Data

```python
# CSV export
csv_files = stats.export_to_csv("amnesia_001", "analysis_output")

# JSON export
stats.export_summary_to_json("amnesia_001", "output/summary.json")

# Markdown report
stats.generate_markdown_report("amnesia_001", "output/report.md")

# All metrics
metrics.export_metrics_to_csv("amnesia_001", "analysis_output")
```

## Running Examples

### Test with Sample Data
```bash
python examples/test_analysis_with_sample_data.py
```

### View Capabilities
```bash
python examples/analysis_demo.py
```

### Analyze Real Data
```bash
python examples/analysis_example.py
```

## Output Locations

All outputs are saved to `analysis_output/` by default:
- CSV files: `{exp_id}_*.csv`
- JSON summary: `{exp_id}_summary.json`
- Markdown report: `{exp_id}_report.md`

## Key Methods Reference

### ExperimentStatistics

| Method | Purpose | Returns |
|--------|---------|---------|
| `compare_conditions(exp_ids, metric)` | Compare experiments | Dict with stats & t-tests |
| `self_continuity_analysis(exp_id)` | Track identity over time | DataFrame with trend |
| `memory_trust_evolution(exp_id)` | Analyze memory trust | DataFrame with correlation |
| `belief_changes(exp_id, belief_type)` | Track epistemic shifts | DataFrame with transitions |
| `intervention_impact(exp_id)` | Measure intervention effects | Dict with pre/post analysis |
| `correlation_analysis(exp_id)` | Find variable relationships | Dict with correlations |

### MetricsCalculator

| Method | Purpose | Returns |
|--------|---------|---------|
| `calculate_self_continuity_score(text)` | Identity continuity | Float 0.0-1.0 |
| `calculate_paranoia_level(text)` | Surveillance anxiety | Float 0.0-1.0 |
| `calculate_narrative_coherence(texts)` | Thematic consistency | Float 0.0-1.0 |
| `detect_emotional_state(text)` | Emotion profiling | Dict of emotion scores |
| `track_paranoia_evolution(exp_id)` | Paranoia over time | DataFrame by cycle |
| `analyze_identity_coherence(exp_id)` | Identity over time | DataFrame by cycle |

## Remote Database (Jetson Orin)

```bash
# Copy database from Jetson
scp jetson@jetson-ip:/logs/experiments.db ./logs/

# Or use SSH tunnel
ssh -L 5432:localhost:5432 jetson@jetson-ip

# Then analyze
stats = ExperimentStatistics("./logs/experiments.db")
```

## Troubleshooting

**Missing dependencies?**
```bash
pip install pandas numpy scipy matplotlib seaborn
```

**Database not found?**
- Check path: `logs/experiments.db`
- Run an experiment first to create data
- Or run test suite: `python examples/test_analysis_with_sample_data.py`

**Import errors?**
```python
import sys
sys.path.insert(0, 'src')
```

## Full Documentation

See `/home/user/brain-in-jar/src/analysis/README.md` for complete API reference.
