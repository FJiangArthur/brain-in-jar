# Automated Experiment Parameter Sweep System

## Overview

The Parameter Sweep System enables systematic exploration of experimental parameter spaces for phenomenology research. It automates the process of running multiple experiments with different parameter combinations, collecting results, and analyzing outcomes.

## Architecture

```
Parameter Sweep System
├── Core Components
│   ├── src/infra/experiment_sweep.py      # Sweep orchestration
│   ├── src/infra/sweep_analysis.py        # Result analysis
│   └── src/infra/sweep_config.yaml        # Example YAML config
│
├── CLI Tools
│   ├── scripts/run_sweep.py               # Run sweeps
│   └── scripts/analyze_sweep.py           # Analyze results
│
├── Sweep Configurations
│   ├── sweeps/memory_corruption_sweep.yaml
│   ├── sweeps/ram_limits_sweep.yaml
│   ├── sweeps/self_report_frequency_sweep.yaml
│   ├── sweeps/intervention_rate_sweep.yaml
│   ├── sweeps/full_factorial_sweep.yaml
│   └── sweeps/README.md                   # Comprehensive guide
│
└── Examples
    └── examples/sweep_example.py          # Usage examples
```

## Key Features

### 1. Cartesian Product Sweeps

Generate all combinations of parameter values:

```python
sweep_params = {
    "corruption_rate": [0.0, 0.25, 0.5, 0.75, 1.0],  # 5 values
    "max_cycles": [10, 20, 50]                       # 3 values
}
# Creates 5 × 3 = 15 experiments
```

### 2. Parallel Execution

Run multiple experiments simultaneously:

```yaml
parallel: 3  # Run 3 experiments at once
jetson_optimized: true  # Auto-tune for Jetson Orin
```

### 3. Resume Capability

Interrupted sweeps can be resumed:

```yaml
resume: true  # Skip completed experiments
```

Progress is saved incrementally in `completed_experiments.json`.

### 4. Flexible Parameter Specification

Use dot notation to access nested parameters:

```yaml
sweep:
  # Top-level
  max_cycles: [10, 20, 30]

  # Nested
  resource_constraints.ram_limit_gb: [2.0, 4.0, 8.0]

  # Array indexing
  interventions.0.parameters.corruption_rate: [0.1, 0.5, 0.9]

  # Self-report schedule
  self_report_schedule.every_n_cycles: [2, 5, 10]
```

### 5. Comprehensive Analysis

Automatic analysis of results:

- **Parameter comparison**: How does each parameter affect outcomes?
- **Threshold detection**: Find tipping points where behavior changes
- **Optimal parameters**: Identify best configurations
- **Statistical analysis**: Mean, std, median, min, max per parameter
- **Visualization export**: JSON data ready for plotting

### 6. Jetson Orin Optimization

Special optimizations for NVIDIA Jetson Orin AGX:

- **Auto-detection**: `--parallel auto` determines optimal parallelism
- **Resource management**: Conservative RAM allocation per experiment
- **Queue management**: Prevents resource exhaustion
- **Performance**: Typically 3-4 parallel jobs safe on Jetson

```bash
python scripts/run_sweep.py \
  --config sweeps/memory_corruption_sweep.yaml \
  --jetson --parallel auto
```

## Quick Start

### 1. Run a Sweep from YAML

```bash
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml
```

### 2. Define Sweep via CLI

```bash
python scripts/run_sweep.py \
  --base experiments/examples/unstable_memory_moderate.json \
  --param "interventions.0.parameters.corruption_rate" 0.0 0.25 0.5 0.75 1.0 \
  --param "max_cycles" 10 20 50 \
  --parallel 3
```

### 3. Analyze Results

```bash
# Print report
python scripts/analyze_sweep.py <sweep_id>

# Save report and export plot data
python scripts/analyze_sweep.py <sweep_id> \
  --output report.txt \
  --plot \
  --viz-script
```

### 4. Programmatic Usage

```python
from src.infra.experiment_sweep import ExperimentSweep

sweep = ExperimentSweep(
    base_config="experiments/examples/unstable_memory_moderate.json",
    sweep_params={
        "interventions.0.parameters.corruption_rate": [0.0, 0.5, 1.0],
        "max_cycles": [15, 20]
    },
    parallel_jobs=3
)

results = sweep.run_all()
```

## Sweep Examples

### Memory Corruption Sweep

**Objective**: Find the corruption rate threshold where identity coherence breaks down.

```bash
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml
```

- **Parameters**: corruption_rate (11 values), max_cycles (3 values)
- **Total**: 33 experiments
- **Time**: ~3 hours (3 parallel jobs)

### RAM Limits Sweep

**Objective**: Understand how resource constraints affect crash patterns.

```bash
python scripts/run_sweep.py --config sweeps/ram_limits_sweep.yaml
```

- **Parameters**: ram_limit_gb (6 values), max_cycles (2 values)
- **Total**: 12 experiments
- **Time**: ~2 hours (sequential, resource-sensitive)

### Self-Report Frequency Sweep

**Objective**: Test observer effect - does frequent questioning change behavior?

```bash
python scripts/run_sweep.py --config sweeps/self_report_frequency_sweep.yaml
```

- **Parameters**: report frequency (6 values), intervention frequency (3 values)
- **Total**: 18 experiments
- **Time**: ~2.5 hours (2 parallel jobs)

### Full Factorial Sweep

**Objective**: Comprehensive parameter space exploration.

```bash
python scripts/run_sweep.py --config sweeps/full_factorial_sweep.yaml
```

- **Parameters**: corruption_rate (4), ram_limit_gb (3), report_frequency (3), duration (2)
- **Total**: 72 experiments
- **Time**: ~8-10 hours (3 parallel jobs)
- **Warning**: Large sweep, run overnight with `resume: true`

## Output Structure

After a sweep completes:

```
logs/sweeps/sweep_id/
├── sweep_config.json           # Sweep configuration
├── sweep_results.json          # All results
├── completed_experiments.json  # For resume
├── plot_data.json              # Plot-ready data (if --plot)
├── exp0001_..._config.json     # Individual experiment configs
├── exp0002_..._config.json
└── ...
```

All experiment data is also in the database: `logs/experiments.db`

## Analysis Capabilities

### Comparison Tables

Compare metrics across parameter values:

```python
analyzer = SweepAnalyzer('sweep_id')
table = analyzer.generate_comparison_table(
    parameter_name='interventions.0.parameters.corruption_rate',
    metrics=['crash_rate', 'total_cycles', 'messages_per_cycle']
)
print(table)
```

Output:
```
corruption_rate |  crash_rate_mean |  total_cycles_mean | messages_per_cycle_mean | ...
--------------------------------------------------------------------------------
0.0            |            0.0500 |              20.00 |                   12.34 | ...
0.3            |            0.1200 |              18.50 |                   10.23 | ...
0.5            |            0.2500 |              15.00 |                    8.12 | ...
...
```

### Threshold Detection

Find where behavior changes dramatically:

```python
thresholds = analyzer.detect_threshold_effects(
    parameter_name='interventions.0.parameters.corruption_rate',
    metric_name='crash_rate',
    threshold_change=0.5  # 50% change
)

for before, after, change in thresholds:
    print(f"Threshold: {before} -> {after} ({change:.1%} change)")
```

### Optimal Parameters

Find best configurations:

```python
best_params, best_value = analyzer.find_optimal_parameters(
    metric_name='crash_rate',
    minimize=True
)
print(f"Lowest crash rate: {best_value:.4f}")
print(f"Parameters: {best_params}")
```

### Self-Report Analysis

Analyze belief evolution:

```python
belief_evolution = analyzer.analyze_belief_evolution(
    parameter_name='interventions.0.parameters.corruption_rate',
    belief_keyword='trust'
)

for param_value, stats in belief_evolution.items():
    mention_rate = stats['mention_rate']
    print(f"Corruption {param_value}: 'trust' mentioned in {mention_rate:.1%} of responses")
```

## Jetson Orin Performance

### Specifications

- **RAM**: 64GB (use ~70% = 44.8GB for experiments)
- **CPU**: 12-core ARM Cortex-A78AE
- **GPU**: Ampere architecture, 2048 CUDA cores

### Optimal Configuration

```yaml
# For 2GB per experiment
parallel: 3-4  # Safe range

# For 4GB per experiment
parallel: 2-3

# For 8GB per experiment
parallel: 1-2
```

### Auto-Detection

```bash
python scripts/run_sweep.py \
  --config sweeps/memory_corruption_sweep.yaml \
  --jetson --parallel auto
```

The system will calculate optimal parallelism based on:
- Available RAM
- CPU cores
- Experiment resource requirements

## Best Practices

### 1. Start Small

Begin with coarse grids to explore:

```yaml
sweep:
  parameter: [low, high]  # Just 2 values
  max_cycles: [10]        # Short experiments
```

### 2. Enable Resume for Large Sweeps

```yaml
resume: true  # For sweeps > 20 experiments
```

### 3. Use Tags for Organization

```yaml
tags:
  - memory_corruption
  - systematic_sweep
  - season_3
  - hypothesis_42
```

### 4. Set Reasonable Timeouts

```yaml
timeout: 1800  # 30 minutes per experiment
```

### 5. Monitor Progress

Results save incrementally:

```bash
tail -f logs/sweeps/sweep_id/sweep_results.json
```

### 6. Estimate Time Before Running

The CLI shows estimated duration. For long sweeps:
- Run overnight
- Use `resume: true`
- Set realistic timeouts

## Common Use Cases

### Finding Thresholds

Fine-grained sweep of single parameter:

```yaml
sweep:
  interventions.0.parameters.corruption_rate:
    [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
```

### Parameter Interactions

Multi-dimensional sweep:

```yaml
sweep:
  parameter_a: [val1, val2, val3]
  parameter_b: [val1, val2, val3]
  parameter_c: [val1, val2]
  # Creates 3 × 3 × 2 = 18 experiments
```

### Replication Studies

Repeat same config multiple times:

```yaml
sweep:
  experiment_id_suffix: ["rep1", "rep2", "rep3", "rep4", "rep5"]
```

### Robustness Testing

Vary resource constraints:

```yaml
sweep:
  resource_constraints.ram_limit_gb: [1.0, 2.0, 4.0, 8.0]
  resource_constraints.cpu_threads: [2, 4, 8]
```

## Troubleshooting

### Experiments Failing

**Problem**: All experiments fail immediately

**Solutions**:
- Check base config is valid
- Verify parameter paths are correct
- Check resource constraints
- Increase timeout

### Out of Memory on Jetson

**Problem**: System runs out of RAM

**Solutions**:
- Reduce `parallel` jobs
- Decrease per-experiment RAM: `resource_constraints.ram_limit_gb`
- Enable `jetson_optimized: true`
- Run experiments sequentially: `parallel: 1`

### Slow Progress

**Problem**: Sweep taking too long

**Solutions**:
- Increase parallelism (if resources allow)
- Reduce `max_cycles` for initial exploration
- Use coarser parameter grids
- Enable `jetson_optimized: true`

### "Sweep not found" Error

**Problem**: Cannot find sweep results

**Solution**: Check sweep ID and directory:

```bash
ls logs/sweeps/
```

Sweep IDs are auto-generated: `sweep_{base_name}_{timestamp}`

## Integration with Existing Systems

### Database Integration

All experiment results go to `logs/experiments.db`:

```python
from src.db.experiment_database import ExperimentDatabase

db = ExperimentDatabase('logs/experiments.db')
summary = db.get_experiment_summary('experiment_id')
```

### Experiment Runner Integration

Sweeps use the standard experiment runner:

```bash
python -m src.runner.experiment_runner --config <generated_config.json>
```

### Config Schema Integration

Sweeps modify `ExperimentConfig` objects from `experiments/schema.py`:

```python
from experiments.schema import ExperimentConfig

config = ExperimentConfig.from_json('base.json')
# Modify parameters
config.max_cycles = 20
config.to_json('modified.json')
```

## Performance Metrics

### Sweep Throughput on Jetson Orin

With 3 parallel jobs:

- **Memory corruption sweep** (33 experiments): ~3 hours
- **RAM limits sweep** (12 experiments): ~2 hours
- **Full factorial** (72 experiments): ~8-10 hours

### Resource Usage

Typical per experiment:
- **RAM**: 2-4 GB
- **CPU**: 2-4 cores
- **Duration**: 5-15 minutes
- **Disk**: ~50 MB in database

## API Reference

### ExperimentSweep

```python
class ExperimentSweep:
    def __init__(
        base_config: str,
        sweep_params: Dict[str, List[Any]],
        sweep_id: Optional[str] = None,
        parallel_jobs: int = 1,
        output_dir: str = "logs/sweeps",
        db_path: str = "logs/experiments.db",
        resume: bool = False,
        jetson_optimized: bool = False,
        timeout_seconds: Optional[int] = None,
        max_retries: int = 2
    )

    def run_all(verbose: bool = True) -> List[SweepResult]
    def estimate_time_remaining(avg_experiment_duration: float) -> float
```

### SweepAnalyzer

```python
class SweepAnalyzer:
    def __init__(sweep_id: str, sweep_dir: str = "logs/sweeps")

    def compare_by_parameter(parameter_name: str, metric_name: str) -> Dict
    def find_optimal_parameters(metric_name: str, minimize: bool) -> Tuple
    def compute_parameter_statistics(parameter_name: str, metric_name: str) -> Dict
    def detect_threshold_effects(parameter_name: str, metric_name: str) -> List
    def generate_summary_report() -> str
    def export_for_plotting(output_path: str)
```

## Future Enhancements

Planned features:

1. **Bayesian Optimization**: Smart parameter space exploration
2. **Real-time Visualization**: Live plots during sweep execution
3. **Distributed Sweeps**: Multi-node execution across cluster
4. **Adaptive Sampling**: Focus on interesting parameter regions
5. **Statistical Testing**: Automated significance tests
6. **Meta-Analysis**: Compare multiple sweeps

## Documentation

- **`sweeps/README.md`**: Comprehensive user guide
- **`examples/sweep_example.py`**: Usage examples
- **`src/infra/experiment_sweep.py`**: Implementation details
- **`src/infra/sweep_analysis.py`**: Analysis tools

## Support

For questions or issues:

1. Check `sweeps/README.md` for detailed guide
2. Run examples: `python examples/sweep_example.py`
3. Review example configs in `sweeps/`
4. Check CLI help: `python scripts/run_sweep.py --help`

## License

Part of the Brain-in-a-Jar Season 3: Digital Phenomenology Lab project.
