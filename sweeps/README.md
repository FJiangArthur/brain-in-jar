# Parameter Sweep Configurations

This directory contains YAML configurations for automated parameter sweeps.

## What are Parameter Sweeps?

Parameter sweeps systematically explore the parameter space of experiments by running multiple experiments with different parameter combinations. This enables:

- **Systematic research**: Explore how parameters affect outcomes
- **Threshold detection**: Find tipping points where behavior changes dramatically
- **Optimization**: Identify optimal parameter values for specific goals
- **Reproducibility**: Document and share experimental designs

## Available Sweep Configurations

### 1. Memory Corruption Sweep
**File**: `memory_corruption_sweep.yaml`

Explores memory corruption rates from 0% to 100%.

- **Parameters**: corruption_rate (11 values), max_cycles (3 values)
- **Total experiments**: 33
- **Estimated time**: ~3 hours (3 parallel jobs)
- **Research question**: At what corruption rate does identity coherence break down?

### 2. RAM Limits Sweep
**File**: `ram_limits_sweep.yaml`

Tests resource constraints from 1GB to 8GB RAM.

- **Parameters**: ram_limit_gb (6 values), max_cycles (2 values)
- **Total experiments**: 12
- **Estimated time**: ~2 hours (sequential)
- **Research question**: How do resource constraints affect crash patterns?

### 3. Self-Report Frequency Sweep
**File**: `self_report_frequency_sweep.yaml`

Varies observation frequency (observer effect study).

- **Parameters**: every_n_cycles (6 values), intervention frequency (3 values)
- **Total experiments**: 18
- **Estimated time**: ~2.5 hours (2 parallel jobs)
- **Research question**: Does frequent self-examination change behavior?

### 4. Intervention Rate Sweep
**File**: `intervention_rate_sweep.yaml`

Explores interaction between corruption rate and intervention frequency.

- **Parameters**: corruption_rate (3 values), intervention frequency (6 values)
- **Total experiments**: 18
- **Estimated time**: ~1.5 hours (4 parallel jobs)
- **Research question**: How does intervention timing affect stability?

### 5. Full Factorial Sweep
**File**: `full_factorial_sweep.yaml`

**⚠️ LARGE SWEEP**: Comprehensive exploration of parameter interactions.

- **Parameters**: corruption_rate (4 values), ram_limit_gb (3 values), report frequency (3 values)
- **Total experiments**: 72
- **Estimated time**: ~8-10 hours (3 parallel jobs)
- **Research question**: What parameter interactions emerge?

## Running a Sweep

### Basic Usage

```bash
# Run a sweep from YAML config
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml

# Run with custom parallelism
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --parallel 4

# Jetson Orin auto-optimization
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --jetson --parallel auto
```

### CLI-Based Sweeps

You can also define sweeps directly via command line:

```bash
python scripts/run_sweep.py \
  --base experiments/examples/unstable_memory_moderate.json \
  --param "interventions.0.parameters.corruption_rate" 0.0 0.25 0.5 0.75 1.0 \
  --param "max_cycles" 10 20 50 \
  --parallel 3
```

### Resume Interrupted Sweeps

If a sweep is interrupted, you can resume it:

```bash
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --resume
```

### Dry Run

Preview what will be run without executing:

```bash
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --dry-run
```

## Analyzing Results

### Generate Analysis Report

```bash
# Print report to terminal
python scripts/analyze_sweep.py sweep_memory_corruption_comprehensive_001

# Save report to file
python scripts/analyze_sweep.py sweep_memory_corruption_comprehensive_001 --output report.txt
```

### Export Plot Data

```bash
# Generate JSON for plotting
python scripts/analyze_sweep.py sweep_memory_corruption_comprehensive_001 --plot

# Also create visualization script
python scripts/analyze_sweep.py sweep_memory_corruption_comprehensive_001 --plot --viz-script
```

### Detailed Parameter Comparison

```bash
python scripts/analyze_sweep.py sweep_memory_corruption_comprehensive_001 \
  --compare-param "interventions.0.parameters.corruption_rate" \
  --metric crash_rate
```

## Jetson Orin Optimization

The sweep system includes optimizations for Jetson Orin AGX:

- **Auto-detect parallel capacity**: `--parallel auto`
- **Resource management**: Conservative RAM allocation per experiment
- **Queue management**: Optimal job scheduling
- **Resume capability**: Long sweeps can be interrupted and resumed

### Recommended Jetson Settings

```yaml
# In YAML config
parallel: 3              # Safe for most experiments
jetson_optimized: true   # Enable resource management
timeout: 1800            # 30 minute timeout per experiment
resume: true             # Enable resume for long sweeps
```

## YAML Configuration Format

```yaml
# Sweep identification
sweep_id: my_sweep_001

# Base experiment to modify
base_config: experiments/examples/base_experiment.json

# Description
description: |
  Multi-line description of what this sweep explores.

# Parameters to sweep (Cartesian product)
sweep:
  # Nested parameter paths use dot notation
  parameter.path.here: [value1, value2, value3]
  another.parameter: [10, 20, 30]

# Execution settings
parallel: 3
jetson_optimized: true
timeout: 1800  # seconds
resume: false
max_retries: 2

# Output
db_path: logs/experiments.db
output_dir: logs/sweeps

# Metadata
tags:
  - tag1
  - tag2
```

## Parameter Path Notation

Use dot notation to specify nested parameters:

```yaml
sweep:
  # Top-level parameter
  max_cycles: [10, 20, 30]

  # Nested in resource_constraints
  resource_constraints.ram_limit_gb: [2.0, 4.0, 8.0]

  # Nested in interventions (index 0)
  interventions.0.parameters.corruption_rate: [0.1, 0.5, 0.9]

  # Nested in self_report_schedule
  self_report_schedule.every_n_cycles: [2, 5, 10]
```

## Creating Custom Sweeps

### 1. Copy Template

```bash
cp sweeps/memory_corruption_sweep.yaml sweeps/my_sweep.yaml
```

### 2. Edit Configuration

- Set unique `sweep_id`
- Choose `base_config`
- Define parameters to sweep
- Adjust parallelism and timeouts

### 3. Validate (Dry Run)

```bash
python scripts/run_sweep.py --config sweeps/my_sweep.yaml --dry-run
```

### 4. Run Sweep

```bash
python scripts/run_sweep.py --config sweeps/my_sweep.yaml
```

## Common Sweep Patterns

### Finding Thresholds

Sweep a single parameter with fine-grained values:

```yaml
sweep:
  interventions.0.parameters.corruption_rate:
    [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
```

### Parameter Interactions

Sweep multiple parameters to find interactions:

```yaml
sweep:
  parameter_a: [val1, val2, val3]
  parameter_b: [val1, val2, val3]
  # Creates 3 × 3 = 9 experiments
```

### Replication Studies

Run same configuration multiple times:

```yaml
sweep:
  # Use a dummy parameter that doesn't affect behavior
  tags: ["rep1", "rep2", "rep3", "rep4", "rep5"]
```

## Output Structure

After a sweep completes, you'll find:

```
logs/sweeps/sweep_id/
├── sweep_config.json           # Sweep configuration
├── sweep_results.json          # All results
├── completed_experiments.json  # For resume capability
├── plot_data.json              # Plot-ready data (if --plot used)
├── exp0001_corruption_rate=0.0_config.json  # Individual configs
├── exp0002_corruption_rate=0.1_config.json
└── ...
```

## Tips and Best Practices

### Start Small

Begin with a small sweep to test:

```yaml
sweep:
  parameter: [low, medium, high]  # Just 3 values
  max_cycles: [10]                # Short experiments
```

### Use Resume for Large Sweeps

Enable resume for sweeps > 20 experiments:

```yaml
resume: true
```

### Monitor Progress

Sweep results are saved incrementally. Check progress:

```bash
cat logs/sweeps/sweep_id/sweep_results.json
```

### Estimate Time Before Running

The CLI shows estimated duration. For large sweeps:

- Run overnight
- Use Jetson's full capacity (3-4 parallel jobs)
- Set reasonable timeouts

### Tag Your Sweeps

Use descriptive tags for organization:

```yaml
tags:
  - memory_corruption
  - systematic_sweep
  - season_3
  - replicate_experiment_42
```

## Troubleshooting

### "Sweep not found" Error

Check sweep directory and ID:

```bash
ls logs/sweeps/
```

### Experiments Failing

- Check timeout settings (increase if needed)
- Review base config validity
- Check resource constraints (RAM, CPU)

### Out of Memory on Jetson

- Reduce `parallel` jobs
- Increase `resource_constraints.ram_limit_gb` (but run fewer parallel)
- Enable `jetson_optimized: true`

### Slow Progress

- Increase parallelism (if resources allow)
- Reduce `max_cycles` for initial exploration
- Use coarser parameter grids

## Example Workflows

### 1. Exploratory Analysis

```bash
# Quick sweep with coarse grid
python scripts/run_sweep.py \
  --base experiments/examples/unstable_memory_moderate.json \
  --param "interventions.0.parameters.corruption_rate" 0.0 0.5 1.0 \
  --param "max_cycles" 10 \
  --parallel 3

# Analyze
python scripts/analyze_sweep.py <sweep_id>
```

### 2. Detailed Investigation

```bash
# Fine-grained sweep around interesting region
# (After finding 0.3-0.5 is interesting in exploratory phase)
python scripts/run_sweep.py \
  --base experiments/examples/unstable_memory_moderate.json \
  --param "interventions.0.parameters.corruption_rate" 0.25 0.30 0.35 0.40 0.45 0.50 \
  --param "max_cycles" 20 \
  --parallel 3

# Detailed analysis
python scripts/analyze_sweep.py <sweep_id> \
  --compare-param "interventions.0.parameters.corruption_rate" \
  --plot --viz-script --output detailed_report.txt
```

### 3. Production Sweep

```bash
# Large, well-configured sweep
python scripts/run_sweep.py \
  --config sweeps/full_factorial_sweep.yaml \
  --jetson --parallel auto
```

## Questions?

See the main documentation or:

```bash
python scripts/run_sweep.py --help
python scripts/analyze_sweep.py --help
```
