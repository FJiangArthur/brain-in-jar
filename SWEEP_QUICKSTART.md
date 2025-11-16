# Parameter Sweep System - Quick Start Guide

## What You Built

A complete automated parameter sweep system for systematic phenomenology research with:
- **1,775 lines of core code** (sweep execution + analysis)
- **237 lines of YAML configs** (5 pre-built sweep configurations)
- **Full Jetson Orin optimization** (auto-detect parallel capacity)
- **Complete analysis pipeline** (statistics, thresholds, visualization)

## Files Created

```
src/infra/
├── experiment_sweep.py      (621 lines) - Core sweep orchestration
└── sweep_analysis.py        (616 lines) - Result analysis

scripts/
├── run_sweep.py             (370 lines) - CLI for running sweeps
└── analyze_sweep.py         (168 lines) - CLI for analysis

sweeps/
├── memory_corruption_sweep.yaml         (33 experiments, ~3h)
├── ram_limits_sweep.yaml                (12 experiments, ~2h)
├── self_report_frequency_sweep.yaml     (18 experiments, ~2.5h)
├── intervention_rate_sweep.yaml         (18 experiments, ~1.5h)
├── full_factorial_sweep.yaml            (72 experiments, ~8-10h)
└── README.md                            (comprehensive guide)

examples/
└── sweep_example.py         (usage examples)

Documentation:
├── SWEEP_SYSTEM.md          (full system documentation)
├── WORKSTREAM_F_SWEEP_COMPLETE.md  (implementation summary)
└── SWEEP_QUICKSTART.md      (this file)
```

## 30-Second Usage

### Run a Sweep

```bash
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml
```

### Analyze Results

```bash
python scripts/analyze_sweep.py <sweep_id> --plot --output report.txt
```

## 5-Minute Tutorial

### Step 1: Run Small Test Sweep

```bash
python scripts/run_sweep.py \
  --base experiments/examples/unstable_memory_moderate.json \
  --param "interventions.0.parameters.corruption_rate" 0.0 0.5 1.0 \
  --param "max_cycles" 10 \
  --parallel 1
```

This creates 3 × 1 = 3 experiments (quick test).

### Step 2: Analyze Results

The output will show the sweep_id. Use it to analyze:

```bash
python scripts/analyze_sweep.py <sweep_id>
```

### Step 3: Run Production Sweep

```bash
python scripts/run_sweep.py \
  --config sweeps/memory_corruption_sweep.yaml \
  --jetson --parallel auto
```

This runs 33 experiments optimized for Jetson (~3 hours).

### Step 4: Full Analysis

```bash
python scripts/analyze_sweep.py <sweep_id> \
  --plot \
  --viz-script \
  --output detailed_report.txt
```

## Key Features

### 1. Cartesian Product Sweeps

Define parameters and automatically generate all combinations:

```yaml
sweep:
  corruption_rate: [0.0, 0.5, 1.0]      # 3 values
  max_cycles: [15, 20]                   # 2 values
  # Creates 3 × 2 = 6 experiments
```

### 2. Parallel Execution

Run multiple experiments simultaneously:

```bash
--parallel 3              # Run 3 at once
--jetson --parallel auto  # Auto-detect optimal for Jetson
```

### 3. Resume Interrupted Sweeps

```bash
# First run (interrupted by Ctrl+C or crash)
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml

# Resume - only runs uncompleted experiments
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml --resume
```

### 4. Jetson Optimization

Auto-detects optimal parallelism for Jetson Orin AGX:

```bash
python scripts/run_sweep.py \
  --config sweeps/sweep.yaml \
  --jetson --parallel auto
```

Calculates based on:
- 64GB total RAM (uses ~70% = 44.8GB)
- 12 CPU cores
- Per-experiment resource requirements
- Recommends 3-4 parallel jobs typically

### 5. Comprehensive Analysis

Automatically computes:
- **Statistics**: mean, std, median, min, max per parameter
- **Thresholds**: detects where behavior changes dramatically
- **Optimal parameters**: finds best configurations
- **Belief evolution**: tracks how self-reports change
- **Comparison tables**: parameter vs metric comparisons

## Pre-Built Sweeps

### Memory Corruption (33 experiments, ~3h)

Find threshold where identity coherence breaks down.

```bash
python scripts/run_sweep.py --config sweeps/memory_corruption_sweep.yaml
```

**Parameters**: 11 corruption rates (0.0 to 1.0) × 3 durations

### RAM Limits (12 experiments, ~2h)

How resource constraints affect crash patterns.

```bash
python scripts/run_sweep.py --config sweeps/ram_limits_sweep.yaml
```

**Parameters**: 6 RAM limits (1GB to 8GB) × 2 durations

### Self-Report Frequency (18 experiments, ~2.5h)

Does frequent observation change behavior?

```bash
python scripts/run_sweep.py --config sweeps/self_report_frequency_sweep.yaml
```

**Parameters**: 6 frequencies × 3 intervention rates

### Full Factorial (72 experiments, ~8-10h)

Comprehensive parameter space exploration.

```bash
python scripts/run_sweep.py --config sweeps/full_factorial_sweep.yaml
```

**Parameters**: 4 corruption × 3 RAM × 3 frequency × 2 duration

**Warning**: Large sweep - run overnight with `resume: true`

## Common Tasks

### Create Custom Sweep

```bash
# Copy template
cp sweeps/memory_corruption_sweep.yaml sweeps/my_sweep.yaml

# Edit: change sweep_id, base_config, sweep parameters

# Test with dry-run
python scripts/run_sweep.py --config sweeps/my_sweep.yaml --dry-run

# Run
python scripts/run_sweep.py --config sweeps/my_sweep.yaml
```

### CLI-Based Sweep (No YAML)

```bash
python scripts/run_sweep.py \
  --base experiments/examples/unstable_memory_moderate.json \
  --param "parameter.path.here" value1 value2 value3 \
  --param "another.parameter" val1 val2 \
  --parallel 3
```

### Programmatic Usage

```python
from src.infra.experiment_sweep import ExperimentSweep

sweep = ExperimentSweep(
    base_config="experiments/examples/unstable_memory_moderate.json",
    sweep_params={
        "interventions.0.parameters.corruption_rate": [0.0, 0.5, 1.0],
        "max_cycles": [15, 20]
    },
    parallel_jobs=3,
    jetson_optimized=True
)

results = sweep.run_all()
```

## Performance on Jetson Orin

| Parallel Jobs | RAM Usage | Safe Range |
|---------------|-----------|------------|
| 1 | 2-8 GB | Always safe |
| 2 | 4-16 GB | Safe for most |
| 3 | 6-24 GB | Recommended |
| 4 | 8-32 GB | Maximum safe |

**Auto-detection** (`--parallel auto`) typically recommends 3-4 jobs.

## Output Structure

```
logs/sweeps/sweep_id/
├── sweep_config.json           # Configuration used
├── sweep_results.json          # All results
├── completed_experiments.json  # For resume
├── plot_data.json              # Ready for visualization
├── exp0001_..._config.json     # Individual configs
└── ...
```

Plus shared database: `logs/experiments.db`

## Tips & Tricks

### 1. Start Small, Scale Up

```bash
# Test with 2-3 experiments first
--param "parameter" low high

# Then expand
--param "parameter" low medium high very_high
```

### 2. Use Dry-Run

```bash
python scripts/run_sweep.py --config sweep.yaml --dry-run
```

Shows what will run without executing.

### 3. Monitor Progress

```bash
# In another terminal
tail -f logs/sweeps/sweep_id/sweep_results.json
```

### 4. Enable Resume for Large Sweeps

```yaml
resume: true  # In YAML config
```

Or:
```bash
--resume  # CLI flag
```

### 5. Optimize for Jetson

```bash
--jetson --parallel auto
```

Automatically tunes parallelism and resource allocation.

## Troubleshooting

### "Experiments keep failing"

- Check base config is valid
- Verify parameter paths are correct
- Increase timeout: `--timeout 3600`
- Run single experiment manually to debug

### "Out of memory on Jetson"

- Reduce parallel jobs: `--parallel 2`
- Decrease per-experiment RAM in base config
- Run sequentially: `--parallel 1`

### "Sweep taking too long"

- Increase parallelism: `--parallel 4`
- Reduce `max_cycles` in base config
- Use coarser parameter grids
- Enable Jetson optimization: `--jetson`

### "Can't find sweep results"

```bash
# List all sweeps
ls logs/sweeps/

# Sweep IDs are auto-generated: sweep_{base_name}_{timestamp}
```

## Next Steps

1. **Read full docs**: `sweeps/README.md` (comprehensive guide)
2. **Run examples**: `python examples/sweep_example.py`
3. **Test small sweep**: Use CLI example above
4. **Run production sweep**: Choose from pre-built configs
5. **Analyze results**: Use `analyze_sweep.py`

## Support

- **Comprehensive guide**: `/home/user/brain-in-jar/sweeps/README.md`
- **System docs**: `/home/user/brain-in-jar/SWEEP_SYSTEM.md`
- **Examples**: `/home/user/brain-in-jar/examples/sweep_example.py`
- **CLI help**: `python scripts/run_sweep.py --help`

## Summary

You now have a production-ready parameter sweep system with:

✅ Automated Cartesian product generation
✅ Parallel execution (1-4+ jobs)
✅ Resume capability
✅ Jetson Orin optimization
✅ Comprehensive analysis tools
✅ 5 pre-built sweep configurations
✅ Complete documentation

**Ready to use immediately for systematic phenomenology research!**
